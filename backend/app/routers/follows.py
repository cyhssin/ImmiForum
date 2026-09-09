from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import (
    get_current_user,
    get_current_verified_user,
    get_optional_current_user,
)
from app.models.user import User
from app.schemas.follow import (
    FeedResponse,
    FollowListResponse,
    FollowStateResponse,
    FollowToggleResponse,
)
from app.services.follow_service import FollowService

router = APIRouter(tags=["Follows"])

# ⚠️ /users/me/* routes MUST be listed BEFORE /users/{username}/* routes,
# otherwise "me" would be captured as a username parameter.

# Private (current user)

@router.get("/users/me/following", response_model=FollowListResponse)
def my_following(
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=50),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Users the current user follows."""
    return FollowService(db).list_following(current_user.username, page=page, size=size)

@router.get("/users/me/followers", response_model=FollowListResponse)
def my_followers(
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=50),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Users who follow the current user."""
    return FollowService(db).list_followers(current_user.username, page=page, size=size)

@router.get("/users/me/feed", response_model=FeedResponse)
def my_feed(
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=50),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Activity feed: questions and comments from followed users, newest first."""
    return FollowService(db).get_feed(current_user, page=page, size=size)

# Public / per-username 

@router.post("/users/{username}/follow", response_model=FollowToggleResponse)
def toggle_follow(
    username: str,
    current_user: User = Depends(get_current_verified_user),
    db: Session = Depends(get_db),
):
    """Follow/unfollow toggle. Self-follow is rejected."""
    return FollowService(db).toggle_follow(current_user, username)

@router.get("/users/{username}/follow-state", response_model=FollowStateResponse)
def follow_state(
    username: str,
    viewer: Optional[User] = Depends(get_optional_current_user),
    db: Session = Depends(get_db),
):
    """Follow counts plus the viewer's follow status (null when anonymous)."""
    return FollowService(db).get_follow_state(viewer, username)

@router.get("/users/{username}/followers", response_model=FollowListResponse)
def user_followers(
    username: str,
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db),
):
    """Public list of a user's followers."""
    return FollowService(db).list_followers(username, page=page, size=size)

@router.get("/users/{username}/following", response_model=FollowListResponse)
def user_following(
    username: str,
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db),
):
    """Public list of who a user follows."""
    return FollowService(db).list_following(username, page=page, size=size)