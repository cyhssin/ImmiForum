from uuid import UUID

from fastapi import HTTPException, status

from app.models.question import Question
from app.models.user import User
from app.repositories.bookmark_repository import BookmarkRepository
from app.repositories.like_repository import LikeRepository
from app.repositories.question_repository import QuestionRepository
from app.schemas.reaction import (
    BookmarkToggleResponse,
    LikeToggleResponse,
    LikedQuestionsResponse,
)
from app.services.question_service import question_to_response

class ReactionService:
    def __init__(self, db):
        self.like_repo = LikeRepository(db)
        self.bookmark_repo = BookmarkRepository(db)
        self.question_repo = QuestionRepository(db)

    # Likes

    def toggle_like(
        self, current_user: User, question_id: UUID
    ) -> LikeToggleResponse:
        question = self._question_or_404(question_id)

        if self.like_repo.has(current_user.id, question.id):
            self.like_repo.remove(current_user.id, question.id)
            liked = False
        else:
            self.like_repo.add(current_user.id, question.id)
            liked = True

        return LikeToggleResponse(
            liked=liked,
            likes_count=self.like_repo.count_for_question(question.id),
        )

    def list_liked_question_ids(self, current_user: User) -> LikedQuestionsResponse:
        return LikedQuestionsResponse(
            question_ids=self.like_repo.get_ids_for_user(current_user.id)
        )

    def list_liked_questions(
        self, current_user: User, *, page: int, size: int
    ) -> tuple[list, int]:
        """Paginated liked-question cards for the dashboard Likes tab."""
        questions, total = self.like_repo.list_questions_for_user(
            current_user.id, offset=(page - 1) * size, limit=size
        )
        counts = self.question_repo.get_counts([q.id for q in questions])
        return (
            [question_to_response(q, counts.get(q.id, {})) for q in questions],
            total,
        )

    # Bookmarks

    def toggle_bookmark(
        self, current_user: User, question_id: UUID
    ) -> BookmarkToggleResponse:
        question = self._question_or_404(question_id)

        if self.bookmark_repo.has(current_user.id, question.id):
            self.bookmark_repo.remove(current_user.id, question.id)
            bookmarked = False
        else:
            self.bookmark_repo.add(current_user.id, question.id)
            bookmarked = True

        bookmarks_count = (
            self.question_repo.get_counts([question.id])
            .get(question.id, {})
            .get("bookmarks", 0)
        )
        return BookmarkToggleResponse(
            bookmarked=bookmarked, bookmarks_count=bookmarks_count
        )

    def list_bookmarks(
        self, current_user: User, *, page: int, size: int
    ) -> tuple[list, int]:
        questions, total = self.bookmark_repo.list_questions_for_user(
            current_user.id, offset=(page - 1) * size, limit=size
        )
        counts = self.question_repo.get_counts([q.id for q in questions])
        return (
            [question_to_response(q, counts.get(q.id, {})) for q in questions],
            total,
        )

    # Helpers

    def _question_or_404(self, question_id: UUID) -> Question:
        question = self.question_repo.get_by_id(question_id)
        if question is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Question not found"
            )
        return question