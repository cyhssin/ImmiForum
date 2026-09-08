from uuid import UUID

from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, joinedload, selectinload

from app.models.bookmark import Bookmark
from app.models.question import Question

class BookmarkRepository:
    def __init__(self, db: Session):
        self.db = db

    def has(self, user_id: UUID, question_id: UUID) -> bool:
        return (
            self.db.query(Bookmark)
            .filter(Bookmark.user_id == user_id, Bookmark.question_id == question_id)
            .first()
            is not None
        )

    def add(self, user_id: UUID, question_id: UUID) -> None:
        """Guarded by uq_user_question_bookmark — races absorbed as no-op."""
        try:
            self.db.add(Bookmark(user_id=user_id, question_id=question_id))
            self.db.commit()
        except IntegrityError:
            self.db.rollback()

    def remove(self, user_id: UUID, question_id: UUID) -> None:
        (
            self.db.query(Bookmark)
            .filter(Bookmark.user_id == user_id, Bookmark.question_id == question_id)
            .delete()
        )
        self.db.commit()

    def list_questions_for_user(
        self, user_id: UUID, *, offset: int, limit: int
    ) -> tuple[list[Question], int]:
        """Bookmarked questions, most recently saved first."""
        query = (
            self.db.query(Question)
            .join(Bookmark, Bookmark.question_id == Question.id)
            .filter(Bookmark.user_id == user_id)
        )
        total = query.order_by(None).count()
        items = (
            query
            .options(
                joinedload(Question.author),
                joinedload(Question.category),
                selectinload(Question.tags),
            )
            .order_by(Bookmark.created_at.desc())
            .offset(offset)
            .limit(limit)
            .all()
        )
        return items, total