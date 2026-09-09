from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field

from app.schemas.question import AuthorBrief

class ModerationActionResponse(BaseModel):
    id: UUID
    status: str
    is_pinned: bool

class RoleItem(BaseModel):
    id: UUID
    name: str
    permissions: list[str] = []

class AdminUserItem(BaseModel):
    id: UUID
    email: str
    username: str
    role: Optional[str] = None
    is_active: bool
    is_verified: bool
    created_at: datetime

class AdminUserDetail(AdminUserItem):
    bio: Optional[str] = None
    questions_count: int = 0
    comments_count: int = 0

class AdminUserListResponse(BaseModel):
    items: list[AdminUserItem]
    total: int
    page: int
    size: int

class UserStatusUpdate(BaseModel):
    is_active: bool

class UserRoleUpdate(BaseModel):
    role: str = Field(..., min_length=2, max_length=50)

class ModerationLogItem(BaseModel):
    id: UUID
    moderator: AuthorBrief
    action: str
    target_type: str
    target_id: str
    detail: Optional[str] = None
    created_at: datetime

class ModerationLogListResponse(BaseModel):
    items: list[ModerationLogItem]
    total: int
    page: int
    size: int