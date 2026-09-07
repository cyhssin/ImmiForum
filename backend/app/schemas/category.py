from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field

class CategoryCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    description: Optional[str] = None

class CategoryUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    description: Optional[str] = None

class CategoryResponse(BaseModel):
    id: UUID
    name: str
    description: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True