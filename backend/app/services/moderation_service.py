from uuid import UUID

from fastapi import HTTPException, status

from app.models.moderation_log import ModerationLog
from app.models.question import Question
from app.models.user import User
from app.repositories.comment_repository import CommentRepository
from app.repositories.moderation_log_repository import ModerationLogRepository
from app.repositories.question_repository import QuestionRepository
from app.schemas.moderation import ModerationActionResponse

class ModerationService:
    def __init__(self, db):
        self.question_repo = QuestionRepository(db)
        self.comment_repo = CommentRepository(db)
        self.log_repo = ModerationLogRepository(db)

    # Question: pin / unpin (idempotent)

    def set_pinned(self, moderator: User, question_id: UUID, pinned: bool):
        question = self._question_or_404(question_id)
        if question.is_pinned != pinned:
            question.is_pinned = pinned
            self.question_repo.update(question)
            self._log(
                moderator,
                "pin" if pinned else "unpin",
                "question",
                str(question.id),
                detail=question.title[:200],
            )
        return _action_response(question)

    # Question: close / reopen (idempotent)

    def set_closed(self, moderator: User, question_id: UUID, closed: bool):
        question = self._question_or_404(question_id)
        desired = "closed" if closed else "open"
        if question.status != desired:
            question.status = desired
            self.question_repo.update(question)
            self._log(
                moderator,
                "close" if closed else "reopen",
                "question",
                str(question.id),
                detail=question.title[:200],
            )
        return _action_response(question)

    # Force delete (logs BEFORE the row disappears) 

    def delete_question(self, moderator: User, question_id: UUID) -> None:
        question = self._question_or_404(question_id)
        self._log(
            moderator,
            "delete_question",
            "question",
            str(question.id),
            detail=question.title[:200],
        )
        self.question_repo.delete(question)  # comments/likes/bookmarks cascade

    def delete_comment(self, moderator: User, comment_id: UUID) -> None:
        comment = self.comment_repo.get_by_id(comment_id)
        if comment is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found"
            )
        self._log(
            moderator,
            "delete_comment",
            "comment",
            str(comment.id),
            detail=(comment.body or "")[:200],
        )
        self.comment_repo.delete(comment)  # replies cascade

    # Helpers

    def _question_or_404(self, question_id: UUID) -> Question:
        question = self.question_repo.get_by_id(question_id)
        if question is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Question not found"
            )
        return question

    def _log(
        self,
        moderator: User,
        action: str,
        target_type: str,
        target_id: str,
        detail: str = None,
    ) -> None:
        self.log_repo.create(
            ModerationLog(
                moderator_id=moderator.id,
                action=action,
                target_type=target_type,
                target_id=target_id,
                detail=detail,
            )
        )

def _action_response(q: Question) -> ModerationActionResponse:
    return ModerationActionResponse(id=q.id, status=q.status, is_pinned=q.is_pinned)