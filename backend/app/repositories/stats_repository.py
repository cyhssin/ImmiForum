from uuid import UUID

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models import Bookmark, Comment, Like, Question

class StatsRepository:
    def __init__(self, db: Session):
        self.db = db

    def questions_count(self, user_id: UUID) -> int:
        return (
            self.db.query(func.count(Question.id))
            .filter(Question.author_id == user_id)
            .scalar()
            or 0
        )

    def comments_count(self, user_id: UUID) -> int:
        return (
            self.db.query(func.count(Comment.id))
            .filter(Comment.author_id == user_id)
            .scalar()
            or 0
        )

    def bookmarks_count(self, user_id: UUID) -> int:
        return (
            self.db.query(func.count(Bookmark.id))
            .filter(Bookmark.user_id == user_id)
            .scalar()
            or 0
        )

    def likes_given_count(self, user_id: UUID) -> int:
        return (
            self.db.query(func.count(Like.id))
            .filter(Like.user_id == user_id)
            .scalar()
            or 0
        )

    def likes_received_count(self, user_id: UUID) -> int:
        return (
            self.db.query(func.count(Like.id))
            .join(Question, Like.question_id == Question.id)
            .filter(Question.author_id == user_id)
            .scalar()
            or 0
        )