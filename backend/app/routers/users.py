from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.schemas.auth import MessageResponse
from app.schemas.question import QuestionListResponse
from app.schemas.user import (
    PasswordChange,
    UserCommentsResponse,
    UserPrivateResponse,
    UserPublicResponse,
    UserStatsResponse,
    UserUpdate,
)
from app.services.reaction_service import ReactionService
from app.services.user_service import UserService

router = APIRouter(tags=["Users"])

# ⚠️ All /users/me* routes MUST be registered BEFORE /users/{username}
# routes, otherwise "me" would be captured as a username parameter.

# Private: current user (dashboard)

@router.get("/users/me", response_model=UserPrivateResponse)
def get_me(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Private profile of the logged-in user (includes email & role)."""
    return UserService(db).get_me(current_user)

@router.put("/users/me", response_model=UserPrivateResponse)
def update_me(
    data: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update own profile (username / bio / avatar_url). Partial update."""
    return UserService(db).update_profile(current_user, data)

@router.put("/users/me/password", response_model=MessageResponse)
def change_password(
    data: PasswordChange,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Change own password after verifying the current one."""
    UserService(db).change_password(current_user, data)
    return MessageResponse(message="Password updated successfully")

@router.get("/users/me/stats", response_model=UserStatsResponse)
def my_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Dashboard stat tiles: own activity counts incl. likes received."""
    return UserService(db).get_my_stats(current_user)

@router.get("/users/me/liked", response_model=QuestionListResponse)
def my_liked_questions(
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=50),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Likes tab: questions the current user liked, newest-like first."""
    items, total = ReactionService(db).list_liked_questions(
        current_user, page=page, size=size
    )
    return QuestionListResponse(items=items, total=total, page=page, size=size)

# Public profiles

@router.get("/users/{username}", response_model=UserPublicResponse)
def public_profile(username: str, db: Session = Depends(get_db)):
    """Public profile. Email and private stats are never exposed."""
    return UserService(db).get_public_profile(username)

@router.get("/users/{username}/questions", response_model=QuestionListResponse)
def user_questions(
    username: str,
    status: Optional[str] = Query(None, pattern="^(open|closed)$"),
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db),
):
    """Public activity tab: questions authored by this user."""
    items, total = UserService(db).list_user_questions(
        username, question_status=status, page=page, size=size
    )
    return QuestionListResponse(items=items, total=total, page=page, size=size)

@router.get("/users/{username}/comments", response_model=UserCommentsResponse)
def user_comments(
    username: str,
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db),
):
    """Public activity tab: comments authored by this user (with question links)."""
    items, total = UserService(db).list_user_comments(username, page=page, size=size)
    return UserCommentsResponse(items=items, total=total, page=page, size=size)