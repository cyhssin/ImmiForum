from datetime import datetime
from uuid import UUID
from typing import Optional
from pydantic import BaseModel

class UserRoleUpdate(BaseModel):
    role_id: UUID

class AdminUserResponse(BaseModel):
    id: UUID
    email: str
    username: str
    is_active: bool
    is_verified: bool
    role: Optional[str] = None
    role_id: Optional[UUID] = None
    permissions: list[str] = []
    created_at: datetime

class AdminUserToggleActive(BaseModel):
    is_active: bool
