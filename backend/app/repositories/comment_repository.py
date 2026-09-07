from typing import Optional
from uuid import UUID

from sqlalchemy.orm import Session

from app.models.comment import Comment
from app.models.user import User

class CommentRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, comment_id: UUID) -> Optional[Comment]:
        return self.db.query(Comment).filter(Comment.id == comment_id).first()

    def list_for_question(self, question_id: UUID) -> list[tuple[Comment, str]]:
        """All comments of a question joined with the author's username.

        Chronological order guarantees a parent is always present before
        its replies are processed — enables single-pass tree assembly.
        """
        return (
            self.db.query(Comment, User.username)
            .join(User, Comment.author_id == User.id)
            .filter(Comment.question_id == question_id)
            .order_by(Comment.created_at.asc(), Comment.id.asc())
            .all()
        )

    def create(self, comment: Comment) -> Comment:
        self.db.add(comment)
        self.db.commit()
        self.db.refresh(comment)
        return comment

    def update(self, comment: Comment) -> Comment:
        self.db.commit()
        self.db.refresh(comment)
        return comment

    def delete(self, comment: Comment) -> None:
        self.db.delete(comment)
        self.db.commit()