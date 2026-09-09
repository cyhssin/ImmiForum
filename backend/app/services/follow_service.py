from typing import Optional

from fastapi import HTTPException, status

from app.models.user import User
from app.repositories.feed_repository import FeedRepository
from app.repositories.follow_repository import FollowRepository
from app.repositories.user_repository import UserRepository
from app.schemas.follow import (
    FeedItem,
    FeedResponse,
    FollowListResponse,
    FollowStateResponse,
    FollowToggleResponse,
    FollowUserItem,
)
from app.schemas.question import AuthorBrief

class FollowService:
    def __init__(self, db):
        self.follow_repo = FollowRepository(db)
        self.user_repo = UserRepository(db)
        self.feed_repo = FeedRepository(db)

    # Toggle

    def toggle_follow(
        self, current_user: User, username: str
    ) -> FollowToggleResponse:
        target = self._user_by_username_or_404(username)

        if target.id == current_user.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="You cannot follow yourself",
            )

        if self.follow_repo.has(current_user.id, target.id):
            self.follow_repo.remove(current_user.id, target.id)
        else:
            self.follow_repo.add(current_user.id, target.id)

        # Re-read state after the operation: exact even under a toggle race
        return FollowToggleResponse(
            is_following=self.follow_repo.has(current_user.id, target.id),
            followers_count=self.follow_repo.followers_count(target.id),
        )

    # State (anonymous-safe) 

    def get_follow_state(
        self, viewer: Optional[User], username: str
    ) -> FollowStateResponse:
        target = self._user_by_username_or_404(username)
        is_following = (
            None
            if viewer is None
            else self.follow_repo.has(viewer.id, target.id)
        )
        return FollowStateResponse(
            is_following=is_following,
            followers_count=self.follow_repo.followers_count(target.id),
            following_count=self.follow_repo.following_count(target.id),
        )

    # Lists

    def list_followers(
        self, username: str, *, page: int, size: int
    ) -> FollowListResponse:
        user = self._user_by_username_or_404(username)
        users, total = self.follow_repo.followers_of(
            user.id, offset=(page - 1) * size, limit=size
        )
        return FollowListResponse(
            items=[_user_item(u) for u in users], total=total, page=page, size=size
        )

    def list_following(
        self, username: str, *, page: int, size: int
    ) -> FollowListResponse:
        user = self._user_by_username_or_404(username)
        users, total = self.follow_repo.following_of(
            user.id, offset=(page - 1) * size, limit=size
        )
        return FollowListResponse(
            items=[_user_item(u) for u in users], total=total, page=page, size=size
        )

    # Activity feed

    def get_feed(self, current_user: User, *, page: int, size: int) -> FeedResponse:
        followed_ids = self.follow_repo.get_followed_user_ids(current_user.id)
        if not followed_ids:
            return FeedResponse(items=[], total=0, page=page, size=size)

        offset = (page - 1) * size
        # Each source is fetched sorted desc; merging preserves global order,
        # so slicing [0:size] after merge yields the correct page-1... and
        # slicing the merged list at [0:size] is the whole page because both
        # sources contributed their top `offset + size` rows.
        questions, q_total = self.feed_repo.recent_questions(
            followed_ids, offset=offset, limit=size
        )
        comments, c_total = self.feed_repo.recent_comments(
            followed_ids, offset=offset, limit=size
        )

        items: list[FeedItem] = []
        for q in questions:
            items.append(
                FeedItem(
                    activity_type="question_created",
                    created_at=q.created_at,
                    user=AuthorBrief(id=q.author.id, username=q.author.username),
                    question_id=q.id,
                    question_slug=q.slug,
                    question_title=q.title,
                    snippet=(q.body or "")[:200],
                )
            )
        for comment, q_slug, q_title, username in comments:
            items.append(
                FeedItem(
                    activity_type="comment_created",
                    created_at=comment.created_at,
                    user=AuthorBrief(id=comment.author_id, username=username),
                    question_id=comment.question_id,
                    question_slug=q_slug,
                    question_title=q_title,
                    comment_id=comment.id,
                    snippet=(comment.body or "")[:200],
                )
            )

        items.sort(key=lambda i: i.created_at, reverse=True)
        return FeedResponse(
            items=items[:size], total=q_total + c_total, page=page, size=size
        )

    # Helpers

    def _user_by_username_or_404(self, username: str) -> User:
        user = self.user_repo.get_by_username(username)
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )
        return user

def _user_item(user: User) -> FollowUserItem:
    return FollowUserItem(
        id=user.id, username=user.username, avatar_url=user.avatar_url
    )