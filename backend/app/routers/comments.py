from uuid import UUID

from fastapi import APIRouter, Depends, Query, Response, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_verified_user, require_permission
from app.models.user import User
from app.schemas.comment import CommentCreate, CommentResponse, CommentUpdate
from app.services.comment_service import CommentService

router = APIRouter(tags=["Comments"])

@router.get("/questions/{slug}/comments", response_model=list[CommentResponse])
def list_comments(
    slug: str,
    sort: str = Query("oldest", pattern="^(oldest|newest)$"),
    db: Session = Depends(get_db),
):
    """Public comment tree. Top-level comments follow `sort`; replies are
    always chronological (oldest first)."""
    return CommentService(db).list_tree(slug, sort)

@router.post(
    "/questions/{slug}/comments",
    response_model=CommentResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_comment(
    slug: str,
    data: CommentCreate,
    current_user: User = Depends(get_current_verified_user),
    _perm: User = Depends(require_permission("create_comment")),
    db: Session = Depends(get_db),
):
    """Create a root comment, or a reply when `parent_id` is given.
    Nesting depth is unlimited."""
    return CommentService(db).create(current_user, slug, data)

@router.put("/comments/{comment_id}", response_model=CommentResponse)
def update_comment(
    comment_id: UUID,
    data: CommentUpdate,
    current_user: User = Depends(get_current_verified_user),
    db: Session = Depends(get_db),
):
    """Author-only edit of the body. Thread position cannot change."""
    return CommentService(db).update(current_user, comment_id, data)

@router.delete("/comments/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_comment(
    comment_id: UUID,
    current_user: User = Depends(get_current_verified_user),
    db: Session = Depends(get_db),
):
    """Delete: comment author, or a role with delete_comment permission.
    Replies are deleted as well (cascade)."""
    CommentService(db).delete(current_user, comment_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)