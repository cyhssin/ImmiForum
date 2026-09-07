from uuid import UUID

from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_admin_user
from app.models.user import User
from app.schemas.category import CategoryCreate, CategoryResponse, CategoryUpdate
from app.services.category_service import CategoryService

router = APIRouter(prefix="/categories", tags=["Categories"])

@router.get("", response_model=list[CategoryResponse])
def list_categories(db: Session = Depends(get_db)):
    """Public list of all categories."""
    return CategoryService(db).list_categories()

@router.post("", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
def create_category(
    data: CategoryCreate,
    _admin: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
):
    """Admin only."""
    return CategoryService(db).create(data)

@router.put("/{category_id}", response_model=CategoryResponse)
def update_category(
    category_id: UUID,
    data: CategoryUpdate,
    _admin: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
):
    """Admin only."""
    return CategoryService(db).update(category_id, data)

@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_category(
    category_id: UUID,
    _admin: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
):
    """Admin only. Questions keep existing with category = NULL."""
    CategoryService(db).delete(category_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)