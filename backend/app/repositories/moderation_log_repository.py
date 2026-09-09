from typing import Optional, Sequence
from uuid import UUID

from sqlalchemy.orm import Session

from app.models.moderation_log import ModerationLog
from app.models.user import User

class ModerationLogRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, log: ModerationLog) -> ModerationLog:
        self.db.add(log)
        self.db.commit()
        self.db.refresh(log)
        return log

    def list(
        self,
        *,
        action: Optional[str] = None,
        moderator_id: Optional[UUID] = None,
        offset: int = 0,
        limit: int = 20,
    ) -> tuple[Sequence[tuple[ModerationLog, str]], int]:
        """(log, moderator_username) rows, newest first."""
        query = (
            self.db.query(ModerationLog, User.username)
            .join(User, ModerationLog.moderator_id == User.id)
        )
        if action:
            query = query.filter(ModerationLog.action == action)
        if moderator_id:
            query = query.filter(ModerationLog.moderator_id == moderator_id)
        total = query.order_by(None).count()
        items = (
            query.order_by(ModerationLog.created_at.desc(), ModerationLog.id.desc())
            .offset(offset)
            .limit(limit)
            .all()
        )
        return items, total