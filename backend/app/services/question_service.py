from uuid import UUID, uuid4

from fastapi import HTTPException, status

from app.core.utils import slugify
from app.models.question import Question
from app.models.tag import Tag
from app.models.user import User
from app.repositories.category_repository import CategoryRepository
from app.repositories.question_repository import QuestionRepository
from app.repositories.tag_repository import TagRepository
from app.schemas.question import (
    QuestionCreate,
    QuestionResponse,
    QuestionUpdate,
)

class QuestionService:
    def __init__(self, db):
        self.question_repo = QuestionRepository(db)
        self.tag_repo = TagRepository(db)
        self.category_repo = CategoryRepository(db)

    # Read 

    def list_questions(self, *, search, tag, category_id, page, size):
        items, total = self.question_repo.list(
            search=search,
            tag=tag,
            category_id=category_id,
            offset=(page - 1) * size,
            limit=size,
        )
        counts = self.question_repo.get_counts([q.id for q in items])
        return (
            [_to_response(q, counts.get(q.id, {})) for q in items],
            total,
        )

    def get_question(self, slug: str) -> QuestionResponse:
        question = self.question_repo.get_by_slug(slug)
        if question is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Question not found"
            )
        counts = self.question_repo.get_counts([question.id])
        return _to_response(question, counts.get(question.id, {}))

    # Create (any authenticated user)

    def create(self, current_user: User, data: QuestionCreate) -> QuestionResponse:
        if data.category_id and not self.category_repo.get_by_id(data.category_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Category not found"
            )

        question = Question(
            title=data.title,
            slug=self._generate_slug(data.title),
            body=data.body,
            author_id=current_user.id,
            category_id=data.category_id,
            status="open",
        )
        question.tags = self._resolve_tags(data.tag_names or [])
        question = self.question_repo.create(question)

        counts = self.question_repo.get_counts([question.id])
        return _to_response(question, counts.get(question.id, {}))

    # Update (owner only - slug cannot be changed)

    def update(
        self, current_user: User, question_id: UUID, data: QuestionUpdate
    ) -> QuestionResponse:
        question = self._get_or_404(question_id)

        if question.author_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only edit your own questions",
            )

        changes = data.model_dump(exclude_unset=True)

        if "title" in changes:
            question.title = changes["title"]
        if "body" in changes:
            question.body = changes["body"]
        if "tag_names" in changes:
            question.tags = self._resolve_tags(changes["tag_names"] or [])
        if "category_id" in changes:
            if changes["category_id"] is not None and not self.category_repo.get_by_id(
                changes["category_id"]
            ):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Category not found",
                )
            question.category_id = changes["category_id"]

        question = self.question_repo.update(question)
        counts = self.question_repo.get_counts([question.id])
        return _to_response(question, counts.get(question.id, {}))

    # Delete (owner or delete_question permission)

    def delete(self, current_user: User, question_id: UUID) -> None:
        question = self._get_or_404(question_id)

        is_owner = question.author_id == current_user.id
        has_permission = (
            current_user.role is not None
            and "delete_question" in (current_user.role.permissions or [])
        )
        if not (is_owner or has_permission):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions"
            )

        self.question_repo.delete(question)

    # Helpers

    def _get_or_404(self, question_id: UUID) -> Question:
        question = self.question_repo.get_by_id(question_id)
        if question is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Question not found"
            )
        return question

    def _generate_slug(self, title: str) -> str:
        base = (slugify(title) or "question")[:200]
        slug = base
        while self.question_repo.get_by_slug_any(slug):
            slug = f"{base}-{uuid4().hex[:6]}"
        return slug

    def _resolve_tags(self, raw_names: list[str]) -> list[Tag]:
        tags, seen = [], set()
        for raw in raw_names:
            name = raw.strip().lower()
            if not name or len(name) > 50 or name in seen:
                continue
            seen.add(name)
            tags.append(self.tag_repo.get_or_create(name))
        return tags

def _to_response(q: Question, counts: dict) -> QuestionResponse:
    return QuestionResponse(
        id=q.id,
        title=q.title,
        slug=q.slug,
        body=q.body,
        status=q.status,
        is_pinned=bool(q.is_pinned),
        author={"id": q.author.id, "username": q.author.username},
        category=(
            {"id": q.category.id, "name": q.category.name} if q.category else None
        ),
        tags=[{"id": t.id, "name": t.name} for t in q.tags],
        likes_count=counts.get("likes", 0),
        comments_count=counts.get("comments", 0),
        bookmarks_count=counts.get("bookmarks", 0),
        created_at=q.created_at,
        updated_at=q.updated_at,
    )
question_to_response = _to_response
