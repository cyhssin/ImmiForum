from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Query, Response, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_verified_user, require_permission
from app.models.user import User
from app.schemas.question import (
    QuestionCreate,
    QuestionListResponse,
    QuestionResponse,
    QuestionUpdate,
)
from app.services.question_service import QuestionService

router = APIRouter(prefix="/questions", tags=["Questions"])

@router.get("", response_model=QuestionListResponse)
def list_questions(
    search: Optional[str] = Query(None, description="ILIKE on title/body"),
    tag: Optional[str] = Query(None),
    category_id: Optional[UUID] = Query(None),
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db),
):
    """Public question list with search, tag/category filters and pagination."""
    service = QuestionService(db)
    items, total = service.list_questions(
        search=search, tag=tag, category_id=category_id, page=page, size=size
    )
    return QuestionListResponse(items=items, total=total, page=page, size=size)

@router.get("/{slug}", response_model=QuestionResponse)
def get_question(slug: str, db: Session = Depends(get_db)):
    """Public question detail by slug."""
    return QuestionService(db).get_question(slug)

@router.post("", response_model=QuestionResponse, status_code=status.HTTP_201_CREATED)
def create_question(
    data: QuestionCreate,
    current_user: User = Depends(get_current_verified_user),
    _perm: User = Depends(require_permission("create_question")),
    db: Session = Depends(get_db),
):
    """Create a question. Tags are auto get-or-created (lowercase)."""
    return QuestionService(db).create(current_user, data)

@router.put("/{question_id}", response_model=QuestionResponse)
def update_question(
    question_id: UUID,
    data: QuestionUpdate,
    current_user: User = Depends(get_current_verified_user),
    db: Session = Depends(get_db),
):
    """Owner-only partial update. The slug is never regenerated."""
    return QuestionService(db).update(current_user, question_id, data)

@router.delete("/{question_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_question(
    question_id: UUID,
    current_user: User = Depends(get_current_verified_user),
    db: Session = Depends(get_db),
):
    """Delete: question owner, or a role with delete_question permission."""
    QuestionService(db).delete(current_user, question_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)