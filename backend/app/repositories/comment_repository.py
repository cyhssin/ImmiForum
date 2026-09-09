from typing import Optional
from uuid import UUID

from sqlalchemy.orm import Session

from app.models.comment import Comment
from app.models.question import Question
from app.models.user import User

class CommentRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, comment_id: UUID) -> Optional[Comment]:
        return self.db.query(Comment).filter(Comment.id == comment_id).first()

    def list_for_question(self, question_id: UUID) -> list[tuple[Comment, str]]:
        """All comments of a question joined with the author's username.

        Chronological order guarantees a parent is always present before
        its replies are processed — enables single-pass tree assembly.
        """
        return (
            self.db.query(Comment, User.username)
            .join(User, Comment.author_id == User.id)
            .filter(Comment.question_id == question_id)
            .order_by(Comment.created_at.asc(), Comment.id.asc())
            .all()
        )

    def list_for_user(
        self, author_id: UUID, *, offset: int, limit: int
    ) -> tuple[list[tuple[Comment, str, str]], int]:
        """(Comment, question_slug, question_title) rows, newest first, plus total."""
        query = (
            self.db.query(Comment, Question.slug, Question.title)
            .join(Question, Comment.question_id == Question.id)
            .filter(Comment.author_id == author_id)
        )
        total = query.order_by(None).count()
        items = (
            query.order_by(Comment.created_at.desc(), Comment.id.desc())
            .offset(offset)
            .limit(limit)
            .all()
        )
        return items, total

    def create(self, comment: Comment) -> Comment:
        self.db.add(comment)
        self.db.commit()
        self.db.refresh(comment)
        return comment

    def update(self, comment: Comment) -> Comment:
        self.db.commit()
        self.db.refresh(comment)
        return comment

    def delete(self, comment: Comment) -> None:
        self.db.delete(comment)
        self.db.commit()