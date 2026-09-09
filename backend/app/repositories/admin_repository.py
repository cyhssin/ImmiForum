from typing import Optional

from sqlalchemy import or_
from sqlalchemy.orm import Session, joinedload

from app.models.user import User

class AdminRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, user_id) -> Optional[User]:
        return (
            self.db.query(User)
            .options(joinedload(User.role))
            .filter(User.id == user_id)
            .first()
        )

    def list_users(
        self, *, search: Optional[str] = None, offset: int = 0, limit: int = 20
    ) -> tuple[list[User], int]:
        filters = None
        if search:
            pattern = f"%{search.strip()}%"
            filters = or_(User.username.ilike(pattern), User.email.ilike(pattern))

        count_query = self.db.query(User)
        if filters is not None:
            count_query = count_query.filter(filters)
        total = count_query.count()

        query = self.db.query(User).options(joinedload(User.role))
        if filters is not None:
            query = query.filter(filters)
        items = query.order_by(User.created_at.desc()).offset(offset).limit(limit).all()
        return items, total