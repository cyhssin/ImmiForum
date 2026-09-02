from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_admin_user
from app.models.user import User
from app.schemas.admin import AdminUserResponse, AdminUserToggleActive, UserRoleUpdate
from app.schemas.role import RoleCreate, RoleResponse, RoleUpdate
from app.schemas.auth import MessageResponse
from app.services.role_service import RoleService

router = APIRouter(prefix="/admin", tags=["Admin"])

# ── Role management ─────────────────────────────────────────────────

@router.get("/roles", response_model=list[RoleResponse])
def list_roles(
    admin: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
):
    """List all roles with their permissions."""
    service = RoleService(db)
    return service.get_all_roles()

@router.get("/roles/{role_id}", response_model=RoleResponse)
def get_role(
    role_id: UUID,
    admin: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
):
    """Get a specific role by ID."""
    service = RoleService(db)
    return service.get_role(str(role_id))

@router.post("/roles", response_model=RoleResponse, status_code=status.HTTP_201_CREATED)
def create_role(
    data: RoleCreate,
    admin: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
):
    """Create a new role with permissions."""
    service = RoleService(db)
    return service.create_role(data)

@router.put("/roles/{role_id}", response_model=RoleResponse)
def update_role(
    role_id: UUID,
    data: RoleUpdate,
    admin: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
):
    """Update a role's name, description, or permissions."""
    service = RoleService(db)
    return service.update_role(str(role_id), data)

@router.delete("/roles/{role_id}", response_model=MessageResponse)
def delete_role(
    role_id: UUID,
    admin: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
):
    """Delete a role (cannot delete default roles or roles with users)."""
    service = RoleService(db)
    service.delete_role(str(role_id))
    return MessageResponse(message="Role deleted successfully")

# ── User management ─────────────────────────────────────────────────

@router.get("/users", response_model=list[AdminUserResponse])
def list_users(
    admin: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
):
    """List all users with their roles and permissions."""
    service = RoleService(db)
    return service.get_all_users()

@router.put("/users/{user_id}/role", response_model=AdminUserResponse)
def change_user_role(
    user_id: UUID,
    data: UserRoleUpdate,
    admin: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
):
    """Change a user's role."""
    service = RoleService(db)
    return service.change_user_role(str(user_id), data)

@router.patch("/users/{user_id}/active", response_model=AdminUserResponse)
def toggle_user_active(
    user_id: UUID,
    data: AdminUserToggleActive,
    admin: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
):
    """Activate or deactivate a user account."""
    service = RoleService(db)
    return service.toggle_user_active(str(user_id), data.is_active)
