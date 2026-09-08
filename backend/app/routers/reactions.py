from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_verified_user
from app.models.user import User
from app.schemas.question import QuestionListResponse
from app.schemas.reaction import (
    BookmarkToggleResponse,
    LikeToggleResponse,
    LikedQuestionsResponse,
)
from app.services.reaction_service import ReactionService

router = APIRouter(tags=["Likes & Bookmarks"])

@router.post("/questions/{question_id}/like", response_model=LikeToggleResponse)
def toggle_like(
    question_id: UUID,
    current_user: User = Depends(get_current_verified_user),
    db: Session = Depends(get_db),
):
    """Like/unlike toggle. Returns the new state and the fresh total."""
    return ReactionService(db).toggle_like(current_user, question_id)

@router.get("/users/me/likes", response_model=LikedQuestionsResponse)
def my_liked_question_ids(
    current_user: User = Depends(get_current_verified_user),
    db: Session = Depends(get_db),
):
    """IDs of questions the current user has liked (for UI highlighting)."""
    return ReactionService(db).list_liked_question_ids(current_user)

@router.post(
    "/questions/{question_id}/bookmark", response_model=BookmarkToggleResponse
)
def toggle_bookmark(
    question_id: UUID,
    current_user: User = Depends(get_current_verified_user),
    db: Session = Depends(get_db),
):
    """Bookmark/unbookmark toggle. Returns the new state and the fresh total."""
    return ReactionService(db).toggle_bookmark(current_user, question_id)

@router.get("/users/me/bookmarks", response_model=QuestionListResponse)
def my_bookmarks(
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=50),
    current_user: User = Depends(get_current_verified_user),
    db: Session = Depends(get_db),
):
    """The current user's saved questions, most recently saved first."""
    items, total = ReactionService(db).list_bookmarks(
        current_user, page=page, size=size
    )
    return QuestionListResponse(items=items, total=total, page=page, size=size)