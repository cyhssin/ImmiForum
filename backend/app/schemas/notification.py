from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class NotificationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    notification_type: Literal["question_comment", "comment_reply"]
    actor_username: str
    comment_id: UUID
    comment_body: str
    question_slug: str
    question_title: str
    created_at: datetime
    read_at: datetime | None


class NotificationListResponse(BaseModel):
    items: list[NotificationResponse]
    unread_count: int


class NotificationUnreadCountResponse(BaseModel):
    unread_count: int
    total_count: int


class NotificationReadResponse(BaseModel):
    id: UUID
    read_at: datetime