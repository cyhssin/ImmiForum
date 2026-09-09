from uuid import UUID

from fastapi import HTTPException, status

from app.models.moderation_log import ModerationLog
from app.models.user import User
from app.repositories.admin_repository import AdminRepository
from app.repositories.moderation_log_repository import ModerationLogRepository
from app.repositories.role_repository import RoleRepository
from app.repositories.stats_repository import StatsRepository
from app.repositories.user_repository import UserRepository
from app.schemas.moderation import (
    AdminUserDetail,
    AdminUserItem,
    AdminUserListResponse,
    ModerationLogItem,
    ModerationLogListResponse,
    RoleItem,
)
from app.schemas.question import AuthorBrief

class AdminService:
    def __init__(self, db):
        self.admin_repo = AdminRepository(db)
        self.user_repo = UserRepository(db)
        self.role_repo = RoleRepository(db)
        self.stats_repo = StatsRepository(db)
        self.log_repo = ModerationLogRepository(db)

    # Roles

    def list_roles(self) -> list[RoleItem]:
        return [
            RoleItem(
                id=r.id, name=r.name, permissions=list(r.permissions or [])
            )
            for r in self.role_repo.list()
        ]

    # User management

    def list_users(self, *, search, page: int, size: int) -> AdminUserListResponse:
        users, total = self.admin_repo.list_users(
            search=search, offset=(page - 1) * size, limit=size
        )
        return AdminUserListResponse(
            items=[_admin_user_item(u) for u in users],
            total=total,
            page=page,
            size=size,
        )

    def get_user(self, user_id: UUID) -> AdminUserDetail:
        user = self._user_or_404(user_id)
        detail = _admin_user_item(user)
        return AdminUserDetail(
            **detail.model_dump(),
            bio=user.bio,
            questions_count=self.stats_repo.questions_count(user.id),
            comments_count=self.stats_repo.comments_count(user.id),
        )

    def set_status(self, admin: User, user_id: UUID, is_active: bool) -> AdminUserDetail:
        if user_id == admin.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="You cannot change your own status",
            )
        user = self._user_or_404(user_id)
        if user.is_active != is_active:
            user.is_active = is_active
            self.user_repo.update(user)
            self._log(
                admin,
                "ban_user" if not is_active else "activate_user",
                "user",
                str(user.id),
                detail=user.username,
            )
        return self.get_user(user_id)

    def set_role(self, admin: User, user_id: UUID, role_name: str) -> AdminUserDetail:
        if user_id == admin.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="You cannot change your own role",
            )
        role = self.role_repo.get_by_name(role_name)
        if role is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Role '{role_name}' does not exist",
            )
        user = self._user_or_404(user_id)
        old_role = user.role.name if user.role else None
        if old_role != role.name:
            user.role = role
            self.user_repo.update(user)
            self._log(
                admin,
                "change_role",
                "user",
                str(user.id),
                detail=f"{old_role} -> {role.name}",
            )
        return self.get_user(user_id)

    # Audit trail

    def list_logs(self, *, action, moderator_id, page: int, size: int):
        rows, total = self.log_repo.list(
            action=action,
            moderator_id=moderator_id,
            offset=(page - 1) * size,
            limit=size,
        )
        items = [
            ModerationLogItem(
                id=log.id,
                moderator=AuthorBrief(id=log.moderator_id, username=username),
                action=log.action,
                target_type=log.target_type,
                target_id=log.target_id,
                detail=log.detail,
                created_at=log.created_at,
            )
            for log, username in rows
        ]
        return ModerationLogListResponse(
            items=items, total=total, page=page, size=size
        )

    # Helpers

    def _user_or_404(self, user_id: UUID) -> User:
        user = self.admin_repo.get_by_id(user_id)
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )
        return user

    def _log(self, moderator, action, target_type, target_id, detail=None):
        self.log_repo.create(
            ModerationLog(
                moderator_id=moderator.id,
                action=action,
                target_type=target_type,
                target_id=target_id,
                detail=detail,
            )
        )

def _admin_user_item(user: User) -> AdminUserItem:
    return AdminUserItem(
        id=user.id,
        email=user.email,
        username=user.username,
        role=user.role.name if user.role else None,
        is_active=user.is_active,
        is_verified=user.is_verified,
        created_at=user.created_at,
    )