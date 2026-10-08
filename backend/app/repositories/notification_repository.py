from datetime import datetime, timezone
from typing import Optional
from uuid import UUID

from sqlalchemy.orm import Session

from app.models.comment import Comment
from app.models.notification import Notification
from app.models.question import Question
from app.models.user import User


class NotificationRepository:
    def __init__(self, db: Session):
        self.db = db

    def add(self, notification: Notification) -> None:
        self.db.add(notification)

    def list_for_user(
        self, recipient_id: UUID, *, limit: int
    ) -> tuple[list[tuple[Notification, str, str, str, str]], int]:
        query = (
            self.db.query(
                Notification,
                User.username,
                Comment.body,
                Question.slug,
                Question.title,
            )
            .join(User, Notification.actor_id == User.id)
            .join(Comment, Notification.comment_id == Comment.id)
            .join(Question, Comment.question_id == Question.id)
            .filter(Notification.recipient_id == recipient_id)
        )
        unread_count = (
            self.db.query(Notification)
            .filter(
                Notification.recipient_id == recipient_id,
                Notification.read_at.is_(None),
            )
            .count()
        )
        items = (
            query.order_by(Notification.created_at.desc(), Notification.id.desc())
            .limit(limit)
            .all()
        )
        return items, unread_count

    def unread_count(self, recipient_id: UUID) -> int:
        return (
            self.db.query(Notification)
            .filter(
                Notification.recipient_id == recipient_id,
                Notification.read_at.is_(None),
            )
            .count()
        )

    def total_count(self, recipient_id: UUID) -> int:
        return (
            self.db.query(Notification)
            .filter(Notification.recipient_id == recipient_id)
            .count()
        )

    def get_for_user(
        self, notification_id: UUID, recipient_id: UUID
    ) -> Optional[Notification]:
        return (
            self.db.query(Notification)
            .filter(
                Notification.id == notification_id,
                Notification.recipient_id == recipient_id,
            )
            .first()
        )

    def mark_all_read(self, recipient_id: UUID) -> None:
        self.db.query(Notification).filter(
            Notification.recipient_id == recipient_id,
            Notification.read_at.is_(None),
        ).update({Notification.read_at: datetime.now(timezone.utc)}, synchronize_session=False)
        self.db.commit()