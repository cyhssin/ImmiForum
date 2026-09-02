from datetime import datetime
from uuid import UUID
from typing import List, Optional
from pydantic import BaseModel, Field

class RoleResponse(BaseModel):
    id: UUID
    name: str
    description: Optional[str] = None
    permissions: List[str] = []
    created_at: datetime

    class Config:
        from_attributes = True

class RoleUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=50)
    description: Optional[str] = None
    permissions: Optional[List[str]] = None

class RoleCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=50)
    description: Optional[str] = None
    permissions: List[str] = []
