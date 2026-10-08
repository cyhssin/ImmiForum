from uuid import UUID

from fastapi import APIRouter, Depends, Query, Response, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_verified_user
from app.models.user import User
from app.schemas.notification import (
    NotificationListResponse,
    NotificationReadResponse,
    NotificationUnreadCountResponse,
)
from app.services.notification_service import NotificationService

router = APIRouter(prefix="/notifications", tags=["Notifications"])


@router.get("", response_model=NotificationListResponse)
def list_notifications(
    limit: int = Query(50, ge=1, le=100),
    current_user: User = Depends(get_current_verified_user),
    db: Session = Depends(get_db),
):
    return NotificationService(db).list_for_user(current_user, limit)


@router.get("/unread-count", response_model=NotificationUnreadCountResponse)
def unread_count(
    current_user: User = Depends(get_current_verified_user),
    db: Session = Depends(get_db),
):
    return NotificationService(db).counts(current_user)


@router.put("/read-all", status_code=status.HTTP_204_NO_CONTENT)
def mark_all_notifications_read(
    current_user: User = Depends(get_current_verified_user),
    db: Session = Depends(get_db),
):
    NotificationService(db).mark_all_read(current_user)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.put("/{notification_id}/read", response_model=NotificationReadResponse)
def mark_notification_read(
    notification_id: UUID,
    current_user: User = Depends(get_current_verified_user),
    db: Session = Depends(get_db),
):
    return NotificationService(db).mark_read(current_user, notification_id)