from uuid import UUID

from pydantic import BaseModel

class LikeToggleResponse(BaseModel):
    liked: bool
    likes_count: int

class BookmarkToggleResponse(BaseModel):
    bookmarked: bool
    bookmarks_count: int

class LikedQuestionsResponse(BaseModel):
    question_ids: list[UUID] = []