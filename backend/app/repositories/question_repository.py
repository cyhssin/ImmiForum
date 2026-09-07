from typing import Optional, Sequence
from uuid import UUID

from sqlalchemy import func, or_
from sqlalchemy.orm import Session, joinedload, selectinload

from app.models import Bookmark, Comment, Like, Question, Tag

class QuestionRepository:
    def __init__(self, db: Session):
        self.db = db

    def _base_query(self):
        return (
            self.db.query(Question)
            .options(
                joinedload(Question.author),
                joinedload(Question.category),
                selectinload(Question.tags),
            )
        )

    def _apply_filters(self, query, *, search, tag, category_id):
        if search:
            pattern = f"%{search.strip()}%"
            query = query.filter(
                or_(Question.title.ilike(pattern), Question.body.ilike(pattern))
            )
        if tag:
            # tag names are stored lowercase
            query = query.join(Question.tags).filter(
                Tag.name == tag.strip().lower()
            )
        if category_id:
            query = query.filter(Question.category_id == category_id)
        return query

    def list(
        self,
        *,
        search: Optional[str] = None,
        tag: Optional[str] = None,
        category_id: Optional[UUID] = None,
        offset: int = 0,
        limit: int = 10,
    ) -> tuple[Sequence[Question], int]:
        query = self._apply_filters(
            self._base_query(), search=search, tag=tag, category_id=category_id
        )
        total = query.order_by(None).count()
        items = (
            query.order_by(Question.created_at.desc())
            .offset(offset)
            .limit(limit)
            .all()
        )
        return items, total

    def get_by_id(self, question_id: UUID) -> Optional[Question]:
        return self._base_query().filter(Question.id == question_id).first()

    def get_by_slug(self, slug: str) -> Optional[Question]:
        return self._base_query().filter(Question.slug == slug).first()

    def get_by_slug_any(self, slug: str) -> Optional[Question]:
        return self.db.query(Question).filter(Question.slug == slug).first()

    def get_counts(self, question_ids: Sequence[UUID]) -> dict[UUID, dict[str, int]]:
        """Batch-fetch like/comment/bookmark counts in 3 grouped queries (no N+1)."""
        if not question_ids:
            return {}

        likes = dict(
            self.db.query(Like.question_id, func.count(Like.id))
            .filter(Like.question_id.in_(question_ids))
            .group_by(Like.question_id)
            .all()
        )
        comments = dict(
            self.db.query(Comment.question_id, func.count(Comment.id))
            .filter(Comment.question_id.in_(question_ids))
            .group_by(Comment.question_id)
            .all()
        )
        bookmarks = dict(
            self.db.query(Bookmark.question_id, func.count(Bookmark.id))
            .filter(Bookmark.question_id.in_(question_ids))
            .group_by(Bookmark.question_id)
            .all()
        )

        return {
            qid: {
                "likes": likes.get(qid, 0),
                "comments": comments.get(qid, 0),
                "bookmarks": bookmarks.get(qid, 0),
            }
            for qid in question_ids
        }

    def create(self, question: Question) -> Question:
        self.db.add(question)
        self.db.commit()
        self.db.refresh(question)
        return question

    def update(self, question: Question) -> Question:
        self.db.commit()
        self.db.refresh(question)
        return question

    def delete(self, question: Question) -> None:
        self.db.delete(question)
        self.db.commit()