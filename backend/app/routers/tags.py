from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.repositories.tag_repository import TagRepository
from app.schemas.tag import TagResponse

router = APIRouter(prefix="/tags", tags=["Tags"])

@router.get("", response_model=list[TagResponse])
def list_tags(db: Session = Depends(get_db)):
    """Public list of all tags (tags are created via question create/update)."""
    return TagRepository(db).list()