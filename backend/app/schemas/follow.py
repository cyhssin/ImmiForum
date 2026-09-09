from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel

from app.schemas.question import AuthorBrief

class FollowToggleResponse(BaseModel):
    is_following: bool
    followers_count: int

class FollowStateResponse(BaseModel):
    is_following: Optional[bool] = None  # None when the viewer is anonymous
    followers_count: int = 0
    following_count: int = 0

class FollowUserItem(BaseModel):
    id: UUID
    username: str
    avatar_url: Optional[str] = None

class FollowListResponse(BaseModel):
    items: list[FollowUserItem]
    total: int
    page: int
    size: int

class FeedItem(BaseModel):
    activity_type: str  # "question_created" | "comment_created"
    created_at: datetime
    user: AuthorBrief
    question_id: UUID
    question_slug: str
    question_title: str
    comment_id: Optional[UUID] = None
    snippet: str = ""

class FeedResponse(BaseModel):
    items: list[FeedItem]
    total: int
    page: int
    size: int