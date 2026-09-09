from typing import Sequence
from uuid import UUID

from sqlalchemy.orm import Session, joinedload, selectinload

from app.models.comment import Comment
from app.models.question import Question
from app.models.user import User

class FeedRepository:
    def __init__(self, db: Session):
        self.db = db

    def recent_questions(
        self, author_ids: Sequence[UUID], *, offset: int, limit: int
    ) -> tuple[list[Question], int]:
        query = (
            self.db.query(Question)
            .options(
                joinedload(Question.author),
                joinedload(Question.category),
                selectinload(Question.tags),
            )
            .filter(Question.author_id.in_(author_ids))
        )
        total = query.order_by(None).count()
        items = (
            query.order_by(Question.created_at.desc(), Question.id.desc())
            .offset(offset)
            .limit(limit)
            .all()
        )
        return items, total

    def recent_comments(
        self, author_ids: Sequence[UUID], *, offset: int, limit: int
    ) -> tuple[list[tuple[Comment, str, str, str]], int]:
        """(Comment, question_slug, question_title, author_username) rows."""
        query = (
            self.db.query(Comment, Question.slug, Question.title, User.username)
            .join(Question, Comment.question_id == Question.id)
            .join(User, Comment.author_id == User.id)
            .filter(Comment.author_id.in_(author_ids))
        )
        total = query.order_by(None).count()
        items = (
            query.order_by(Comment.created_at.desc(), Comment.id.desc())
            .offset(offset)
            .limit(limit)
            .all()
        )
        return items, total