from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field

class AuthorBrief(BaseModel):
    id: UUID
    username: str

class TagBrief(BaseModel):
    id: UUID
    name: str

class CategoryBrief(BaseModel):
    id: UUID
    name: str

class QuestionCreate(BaseModel):
    title: str = Field(..., min_length=10, max_length=255)
    body: str = Field(..., min_length=20)
    tag_names: list[str] = Field(default_factory=list, max_length=20)
    category_id: Optional[UUID] = None

class QuestionUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=10, max_length=255)
    body: Optional[str] = Field(None, min_length=20)
    tag_names: Optional[list[str]] = Field(None, max_length=20)
    category_id: Optional[UUID] = None

class QuestionResponse(BaseModel):
    id: UUID
    title: str
    slug: str
    body: str
    status: str
    is_pinned: bool = False
    author: AuthorBrief
    category: Optional[CategoryBrief] = None
    tags: list[TagBrief] = []
    likes_count: int = 0
    comments_count: int = 0
    bookmarks_count: int = 0
    created_at: datetime
    updated_at: Optional[datetime] = None

class QuestionListResponse(BaseModel):
    items: list[QuestionResponse]
    total: int
    page: int
    size: int