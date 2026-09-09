from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field

class UserUpdate(BaseModel):
    username: Optional[str] = Field(
        None, min_length=3, max_length=50, pattern=r"^[a-zA-Z0-9_]+$"
    )
    bio: Optional[str] = Field(None, max_length=500)
    avatar_url: Optional[str] = Field(None, max_length=500)

class PasswordChange(BaseModel):
    current_password: str
    new_password: str = Field(..., min_length=8, max_length=100)

class UserPrivateResponse(BaseModel):
    id: UUID
    email: str
    username: str
    bio: Optional[str] = None
    avatar_url: Optional[str] = None
    is_active: bool
    is_verified: bool
    role: Optional[str] = None
    created_at: datetime

class UserPublicResponse(BaseModel):
    id: UUID
    username: str
    bio: Optional[str] = None
    avatar_url: Optional[str] = None
    questions_count: int = 0
    comments_count: int = 0
    created_at: datetime

class UserStatsResponse(BaseModel):
    questions_count: int
    comments_count: int
    bookmarks_count: int
    likes_given_count: int
    likes_received_count: int

class UserCommentItem(BaseModel):
    id: UUID
    body: str
    question_id: UUID
    question_slug: str
    question_title: str
    created_at: datetime
    updated_at: Optional[datetime] = None

class UserCommentsResponse(BaseModel):
    items: list[UserCommentItem]
    total: int
    page: int
    size: int