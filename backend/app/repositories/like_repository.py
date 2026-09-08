from uuid import UUID

from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.like import Like

class LikeRepository:
    def __init__(self, db: Session):
        self.db = db

    def has(self, user_id: UUID, question_id: UUID) -> bool:
        return (
            self.db.query(Like)
            .filter(Like.user_id == user_id, Like.question_id == question_id)
            .first()
            is not None
        )

    def add(self, user_id: UUID, question_id: UUID) -> None:
        """Guarded by uq_user_question_like — a race with a concurrent
        toggle hits the unique constraint and is absorbed (no-op)."""
        try:
            self.db.add(Like(user_id=user_id, question_id=question_id))
            self.db.commit()
        except IntegrityError:
            self.db.rollback()

    def remove(self, user_id: UUID, question_id: UUID) -> None:
        (
            self.db.query(Like)
            .filter(Like.user_id == user_id, Like.question_id == question_id)
            .delete()
        )
        self.db.commit()

    def count_for_question(self, question_id: UUID) -> int:
        return (
            self.db.query(func.count(Like.id))
            .filter(Like.question_id == question_id)
            .scalar()
            or 0
        )

    def get_ids_for_user(self, user_id: UUID) -> list[UUID]:
        rows = (
            self.db.query(Like.question_id)
            .filter(Like.user_id == user_id)
            .order_by(Like.created_at.desc())
            .all()
        )
        return [row[0] for row in rows]