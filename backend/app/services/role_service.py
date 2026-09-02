from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.role import Role
from app.models.user import User
from app.repositories.role_repository import RoleRepository
from app.repositories.user_repository import UserRepository
from app.schemas.admin import AdminUserResponse, UserRoleUpdate
from app.schemas.role import RoleCreate, RoleUpdate

class RoleService:
    def __init__(self, db: Session):
        self.db = db
        self.role_repo = RoleRepository(db)
        self.user_repo = UserRepository(db)

    # ── Role CRUD ───────────────────────────────────────────────────

    def get_all_roles(self):
        roles = self.role_repo.get_all()
        return roles

    def get_role(self, role_id: str):
        role = self.role_repo.get_by_id(role_id)
        if not role:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Role not found",
            )
        return role

    def create_role(self, data: RoleCreate):
        if self.role_repo.get_by_name(data.name):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Role with this name already exists",
            )
        role = Role(
            name=data.name,
            description=data.description,
            permissions=data.permissions,
        )
        return self.role_repo.create(role)

    def update_role(self, role_id: str, data: RoleUpdate):
        role = self.get_role(role_id)

        if data.name and data.name != role.name:
            if self.role_repo.get_by_name(data.name):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Role with this name already exists",
                )
            role.name = data.name

        if data.description is not None:
            role.description = data.description

        if data.permissions is not None:
            role.permissions = data.permissions

        return self.role_repo.update(role)

    def delete_role(self, role_id: str):
        role = self.get_role(role_id)

        # Prevent deleting default roles
        if role.name in ("user", "moderator", "admin"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot delete default roles",
            )

        # Check if any users have this role
        users_with_role = self.db.query(User).filter(User.role_id == role_id).count()
        if users_with_role > 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot delete role: {users_with_role} user(s) assigned",
            )

        self.role_repo.delete(role)

    # ── User management ─────────────────────────────────────────────

    def get_all_users(self):
        users = self.db.query(User).order_by(User.created_at.desc()).all()
        return [
            AdminUserResponse(
                id=u.id,
                email=u.email,
                username=u.username,
                is_active=u.is_active,
                is_verified=u.is_verified,
                role=u.role.name if u.role else None,
                role_id=u.role_id,
                permissions=u.role.permissions if u.role else [],
                created_at=u.created_at,
            )
            for u in users
        ]

    def change_user_role(self, user_id: str, data: UserRoleUpdate):
        user = self.user_repo.get_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )

        new_role = self.role_repo.get_by_id(data.role_id)
        if not new_role:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Role not found",
            )

        user.role_id = new_role.id
        self.user_repo.update(user)
        return AdminUserResponse(
            id=user.id,
            email=user.email,
            username=user.username,
            is_active=user.is_active,
            is_verified=user.is_verified,
            role=new_role.name,
            role_id=new_role.id,
            permissions=new_role.permissions,
            created_at=user.created_at,
        )

    def toggle_user_active(self, user_id: str, is_active: bool):
        user = self.user_repo.get_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )
        user.is_active = is_active
        self.user_repo.update(user)
        return AdminUserResponse(
            id=user.id,
            email=user.email,
            username=user.username,
            is_active=user.is_active,
            is_verified=user.is_verified,
            role=user.role.name if user.role else None,
            role_id=user.role_id,
            permissions=user.role.permissions if user.role else [],
            created_at=user.created_at,
        )
