from fastapi import HTTPException, status

from app.core.security import get_password_hash, verify_password
from app.models.user import User
from app.repositories.comment_repository import CommentRepository
from app.repositories.question_repository import QuestionRepository
from app.repositories.stats_repository import StatsRepository
from app.repositories.user_repository import UserRepository
from app.schemas.question import QuestionResponse
from app.schemas.user import (
    PasswordChange,
    UserCommentItem,
    UserPrivateResponse,
    UserPublicResponse,
    UserStatsResponse,
    UserUpdate,
)
from app.services.question_service import question_to_response

class UserService:
    def __init__(self, db):
        self.user_repo = UserRepository(db)
        self.stats_repo = StatsRepository(db)
        self.question_repo = QuestionRepository(db)
        self.comment_repo = CommentRepository(db)

    # Private profile (/users/me)

    def get_me(self, current_user: User) -> UserPrivateResponse:
        return _private_response(current_user)

    def update_profile(self, current_user: User, data: UserUpdate) -> UserPrivateResponse:
        changes = data.model_dump(exclude_unset=True)

        if "username" in changes:
            new_name = changes["username"]
            existing = self.user_repo.get_by_username(new_name)
            if existing and existing.id != current_user.id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Username already taken",
                )
            current_user.username = new_name
        if "bio" in changes:
            current_user.bio = changes["bio"]
        if "avatar_url" in changes:
            current_user.avatar_url = changes["avatar_url"]

        user = self.user_repo.update(current_user)
        return _private_response(user)

    def change_password(self, current_user: User, data: PasswordChange) -> None:
        if not verify_password(data.current_password, current_user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Current password is incorrect",
            )
        if data.current_password == data.new_password:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="New password must be different from the current password",
            )
        current_user.hashed_password = get_password_hash(data.new_password)
        self.user_repo.update(current_user)

    def get_my_stats(self, current_user: User) -> UserStatsResponse:
        uid = current_user.id
        return UserStatsResponse(
            questions_count=self.stats_repo.questions_count(uid),
            comments_count=self.stats_repo.comments_count(uid),
            bookmarks_count=self.stats_repo.bookmarks_count(uid),
            likes_given_count=self.stats_repo.likes_given_count(uid),
            likes_received_count=self.stats_repo.likes_received_count(uid),
        )

    # Public profile (/users/{username})

    def get_public_profile(self, username: str) -> UserPublicResponse:
        user = self._user_by_username_or_404(username)
        return UserPublicResponse(
            id=user.id,
            username=user.username,
            bio=user.bio,
            avatar_url=user.avatar_url,
            questions_count=self.stats_repo.questions_count(user.id),
            comments_count=self.stats_repo.comments_count(user.id),
            created_at=user.created_at,
        )

    def list_user_questions(
        self, username: str, *, question_status, page: int, size: int
    ) -> tuple[list[QuestionResponse], int]:
        user = self._user_by_username_or_404(username)
        items, total = self.question_repo.list_by_author(
            user.id,
            status=question_status,
            offset=(page - 1) * size,
            limit=size,
        )
        counts = self.question_repo.get_counts([q.id for q in items])
        return (
            [question_to_response(q, counts.get(q.id, {})) for q in items],
            total,
        )

    def list_user_comments(
        self, username: str, *, page: int, size: int
    ) -> tuple[list[UserCommentItem], int]:
        user = self._user_by_username_or_404(username)
        rows, total = self.comment_repo.list_for_user(
            user.id, offset=(page - 1) * size, limit=size
        )
        return (
            [
                UserCommentItem(
                    id=c.id,
                    body=c.body,
                    question_id=c.question_id,
                    question_slug=question_slug,
                    question_title=question_title,
                    created_at=c.created_at,
                    updated_at=c.updated_at,
                )
                for c, question_slug, question_title in rows
            ],
            total,
        )

    # Helpers

    def _user_by_username_or_404(self, username: str) -> User:
        user = self.user_repo.get_by_username(username)
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )
        return user

def _private_response(user: User) -> UserPrivateResponse:
    return UserPrivateResponse(
        id=user.id,
        email=user.email,
        username=user.username,
        bio=user.bio,
        avatar_url=user.avatar_url,
        is_active=user.is_active,
        is_verified=user.is_verified,
        role=user.role.name if user.role else None,
        created_at=user.created_at,
    )