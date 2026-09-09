from uuid import UUID

from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.follow import Follow
from app.models.user import User

class FollowRepository:
    def __init__(self, db: Session):
        self.db = db

    def has(self, follower_id: UUID, following_id: UUID) -> bool:
        return (
            self.db.query(Follow)
            .filter(Follow.follower_id == follower_id, Follow.following_id == following_id)
            .first()
            is not None
        )

    def add(self, follower_id: UUID, following_id: UUID) -> None:
        """Guarded by uq_follower_following — races absorbed as no-op."""
        try:
            self.db.add(Follow(follower_id=follower_id, following_id=following_id))
            self.db.commit()
        except IntegrityError:
            self.db.rollback()

    def remove(self, follower_id: UUID, following_id: UUID) -> None:
        (
            self.db.query(Follow)
            .filter(Follow.follower_id == follower_id, Follow.following_id == following_id)
            .delete()
        )
        self.db.commit()

    def followers_count(self, user_id: UUID) -> int:
        """How many users follow `user_id`."""
        return (
            self.db.query(func.count(Follow.id))
            .filter(Follow.following_id == user_id)
            .scalar()
            or 0
        )

    def following_count(self, user_id: UUID) -> int:
        """How many users `user_id` follows."""
        return (
            self.db.query(func.count(Follow.id))
            .filter(Follow.follower_id == user_id)
            .scalar()
            or 0
        )

    def get_followed_user_ids(self, follower_id: UUID) -> list[UUID]:
        rows = (
            self.db.query(Follow.following_id)
            .filter(Follow.follower_id == follower_id)
            .all()
        )
        return [row[0] for row in rows]

    def followers_of(
        self, user_id: UUID, *, offset: int, limit: int
    ) -> tuple[list[User], int]:
        """Users who follow `user_id`, alphabetical."""
        query = (
            self.db.query(User)
            .join(Follow, Follow.follower_id == User.id)
            .filter(Follow.following_id == user_id)
        )
        total = query.order_by(None).count()
        items = (
            query.order_by(User.username.asc())
            .offset(offset)
            .limit(limit)
            .all()
        )
        return items, total

    def following_of(
        self, user_id: UUID, *, offset: int, limit: int
    ) -> tuple[list[User], int]:
        """Users `user_id` follows, alphabetical."""
        query = (
            self.db.query(User)
            .join(Follow, Follow.following_id == User.id)
            .filter(Follow.follower_id == user_id)
        )
        total = query.order_by(None).count()
        items = (
            query.order_by(User.username.asc())
            .offset(offset)
            .limit(limit)
            .all()
        )
        return items, total