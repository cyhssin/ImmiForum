from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field

from app.schemas.question import AuthorBrief

class CommentCreate(BaseModel):
    body: str = Field(..., min_length=1, max_length=5000)
    parent_id: Optional[UUID] = None

class CommentUpdate(BaseModel):
    body: str = Field(..., min_length=1, max_length=5000)

class CommentResponse(BaseModel):
    id: UUID
    body: str
    question_id: UUID
    author: AuthorBrief
    parent_id: Optional[UUID] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    replies: list["CommentResponse"] = []

CommentResponse.model_rebuild()