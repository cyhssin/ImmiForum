from datetime import datetime, timezone
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.notification import Notification
from app.models.user import User
from app.repositories.notification_repository import NotificationRepository
from app.schemas.notification import (
    NotificationListResponse,
    NotificationReadResponse,
    NotificationResponse,
)


class NotificationService:
    def __init__(self, db: Session):
        self.db = db
        self.notification_repo = NotificationRepository(db)

    def list_for_user(self, current_user: User, limit: int) -> NotificationListResponse:
        rows, unread_count = self.notification_repo.list_for_user(
            current_user.id, limit=limit
        )
        items = [
            NotificationResponse(
                id=notification.id,
                notification_type=notification.notification_type,
                actor_username=actor_username,
                comment_id=notification.comment_id,
                comment_body=comment_body[:240],
                question_slug=question_slug,
                question_title=question_title,
                created_at=notification.created_at,
                read_at=notification.read_at,
            )
            for notification, actor_username, comment_body, question_slug, question_title in rows
        ]
        return NotificationListResponse(items=items, unread_count=unread_count)

    def unread_count(self, current_user: User) -> int:
        return self.notification_repo.unread_count(current_user.id)

    def counts(self, current_user: User) -> dict[str, int]:
        return {
            "unread_count": self.notification_repo.unread_count(current_user.id),
            "total_count": self.notification_repo.total_count(current_user.id),
        }

    def mark_read(
        self, current_user: User, notification_id: UUID
    ) -> NotificationReadResponse:
        notification = self.notification_repo.get_for_user(
            notification_id, current_user.id
        )
        if notification is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Notification not found",
            )
        if notification.read_at is None:
            notification.read_at = datetime.now(timezone.utc)
            self.db.commit()
            self.db.refresh(notification)
        return NotificationReadResponse(id=notification.id, read_at=notification.read_at)

    def mark_all_read(self, current_user: User) -> None:
        self.notification_repo.mark_all_read(current_user.id)