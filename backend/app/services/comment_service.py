from uuid import UUID

from fastapi import HTTPException, status

from app.models.comment import Comment
from app.models.question import Question
from app.models.user import User
from app.repositories.comment_repository import CommentRepository
from app.repositories.question_repository import QuestionRepository
from app.schemas.comment import CommentCreate, CommentResponse, CommentUpdate
from app.schemas.question import AuthorBrief

class CommentService:
    def __init__(self, db):
        self.comment_repo = CommentRepository(db)
        self.question_repo = QuestionRepository(db)

    # Read (tree)

    def list_tree(self, slug: str, sort: str) -> list[CommentResponse]:
        question = self._get_question_or_404(slug)

        rows = self.comment_repo.list_for_question(question.id)

        nodes: dict[UUID, CommentResponse] = {}
        roots: list[CommentResponse] = []
        for comment, username in rows:
            node = _to_response(comment, username)
            nodes[comment.id] = node
            # Chronological ordering guarantees the parent was seen already;
            # a parentless/mismatched row degrades gracefully to a root.
            parent = nodes.get(comment.parent_id) if comment.parent_id else None
            if parent is not None:
                parent.replies.append(node)
            else:
                roots.append(node)

        if sort == "newest":
            roots.reverse()
        return roots

    # Create 

    def create(
        self, current_user: User, slug: str, data: CommentCreate
    ) -> CommentResponse:
        question = self._get_question_or_404(slug)

        if question.status == "closed":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Question is closed to new comments",
            )

        body = data.body.strip()
        if not body:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Comment body cannot be empty",
            )

        if data.parent_id is not None:
            parent = self.comment_repo.get_by_id(data.parent_id)
            if parent is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Parent comment not found",
                )
            if parent.question_id != question.id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Parent comment does not belong to this question",
                )

        comment = self.comment_repo.create(
            Comment(
                body=body,
                question_id=question.id,
                author_id=current_user.id,
                parent_id=data.parent_id,
            )
        )
        return _to_response(comment, current_user.username)

    # Update (author only) 

    def update(
        self, current_user: User, comment_id: UUID, data: CommentUpdate
    ) -> CommentResponse:
        comment = self._get_or_404(comment_id)

        if comment.author_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only edit your own comments",
            )

        body = data.body.strip()
        if not body:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Comment body cannot be empty",
            )

        comment.body = body
        comment = self.comment_repo.update(comment)
        return _to_response(comment, current_user.username)

    # Delete (owner or delete_comment permission) 

    def delete(self, current_user: User, comment_id: UUID) -> None:
        comment = self._get_or_404(comment_id)

        is_owner = comment.author_id == current_user.id
        has_permission = (
            current_user.role is not None
            and "delete_comment" in (current_user.role.permissions or [])
        )
        if not (is_owner or has_permission):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions"
            )

        # Replies are removed too (parent_id FK ON DELETE CASCADE)
        self.comment_repo.delete(comment)

    # Helpers

    def _get_question_or_404(self, slug: str) -> Question:
        question = self.question_repo.get_by_slug(slug)
        if question is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Question not found"
            )
        return question

    def _get_or_404(self, comment_id: UUID) -> Comment:
        comment = self.comment_repo.get_by_id(comment_id)
        if comment is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found"
            )
        return comment

def _to_response(comment: Comment, username: str) -> CommentResponse:
    return CommentResponse(
        id=comment.id,
        body=comment.body,
        question_id=comment.question_id,
        author=AuthorBrief(id=comment.author_id, username=username),
        parent_id=comment.parent_id,
        created_at=comment.created_at,
        updated_at=comment.updated_at,
        replies=[],
    )