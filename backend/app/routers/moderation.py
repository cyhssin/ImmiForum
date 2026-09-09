from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Query, Response, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_admin_user, get_current_moderator_user
from app.models.user import User
from app.schemas.moderation import (
    AdminUserDetail,
    AdminUserListResponse,
    ModerationActionResponse,
    ModerationLogListResponse,
    RoleItem,
    UserStatusUpdate,
    UserRoleUpdate,
)
from app.services.admin_service import AdminService
from app.services.moderation_service import ModerationService

router = APIRouter(tags=["Admin & Moderation"])

# Question moderation (moderator or admin)

@router.post("/admin/questions/{question_id}/pin", response_model=ModerationActionResponse)
def pin_question(
    question_id: UUID,
    moderator: User = Depends(get_current_moderator_user),
    db: Session = Depends(get_db),
):
    """Pin a question (idempotent). Pinned questions lead the global list."""
    return ModerationService(db).set_pinned(moderator, question_id, pinned=True)

@router.post("/admin/questions/{question_id}/unpin", response_model=ModerationActionResponse)
def unpin_question(
    question_id: UUID,
    moderator: User = Depends(get_current_moderator_user),
    db: Session = Depends(get_db),
):
    """Unpin a question (idempotent)."""
    return ModerationService(db).set_pinned(moderator, question_id, pinned=False)

@router.post("/admin/questions/{question_id}/close", response_model=ModerationActionResponse)
def close_question(
    question_id: UUID,
    moderator: User = Depends(get_current_moderator_user),
    db: Session = Depends(get_db),
):
    """Close a question: new comments are rejected with 400 (phase-5 guard)."""
    return ModerationService(db).set_closed(moderator, question_id, closed=True)

@router.post("/admin/questions/{question_id}/reopen", response_model=ModerationActionResponse)
def reopen_question(
    question_id: UUID,
    moderator: User = Depends(get_current_moderator_user),
    db: Session = Depends(get_db),
):
    """Reopen a previously closed question."""
    return ModerationService(db).set_closed(moderator, question_id, closed=False)

@router.delete("/admin/questions/{question_id}", status_code=status.HTTP_204_NO_CONTENT)
def force_delete_question(
    question_id: UUID,
    moderator: User = Depends(get_current_moderator_user),
    db: Session = Depends(get_db),
):
    """Moderator force-delete; comments/likes/bookmarks cascade. Logged."""
    ModerationService(db).delete_question(moderator, question_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)

@router.delete("/admin/comments/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
def force_delete_comment(
    comment_id: UUID,
    moderator: User = Depends(get_current_moderator_user),
    db: Session = Depends(get_db),
):
    """Moderator force-delete of any comment (and its replies). Logged."""
    ModerationService(db).delete_comment(moderator, comment_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)

# Audit trail (moderator or admin)

@router.get("/admin/moderation-logs", response_model=ModerationLogListResponse)
def moderation_logs(
    action: Optional[str] = Query(None),
    moderator_id: Optional[UUID] = Query(None),
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=50),
    _mod: User = Depends(get_current_moderator_user),
    db: Session = Depends(get_db),
):
    """Who did what, when — filterable by action and moderator."""
    return AdminService(db).list_logs(
        action=action, moderator_id=moderator_id, page=page, size=size
    )

# User management (admin only)

@router.get("/admin/roles", response_model=list[RoleItem])
def list_roles(
    _admin: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
):
    """Available roles and their permissions (for assignment UI)."""
    return AdminService(db).list_roles()

@router.get("/admin/users", response_model=AdminUserListResponse)
def list_users(
    search: Optional[str] = Query(None, description="username/email ILIKE"),
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    _admin: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
):
    return AdminService(db).list_users(search=search, page=page, size=size)

@router.get("/admin/users/{user_id}", response_model=AdminUserDetail)
def get_user(
    user_id: UUID,
    _admin: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
):
    return AdminService(db).get_user(user_id)

@router.put("/admin/users/{user_id}/status", response_model=AdminUserDetail)
def set_user_status(
    user_id: UUID,
    data: UserStatusUpdate,
    admin: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
):
    """Activate/deactivate a user. Deactivated users fail every authed call
    with 403 immediately (see get_current_user). Self-deactivation -> 400."""
    return AdminService(db).set_status(admin, user_id, data.is_active)

@router.put("/admin/users/{user_id}/role", response_model=AdminUserDetail)
def set_user_role(
    user_id: UUID,
    data: UserRoleUpdate,
    admin: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
):
    """Assign a role by name (see GET /admin/roles). Self role-change -> 400."""
    return AdminService(db).set_role(admin, user_id, data.role)