from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import (
    create_access_token,
    create_email_verification_token,
    create_refresh_token,
    get_password_hash,
    verify_password,
    verify_token,
)
from app.models.role import Role
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.schemas.auth import UserRegister, UserResponse
from app.services.email_service import EmailService

class AuthService:
    def __init__(self, db: Session):
        self.db = db
        self.user_repo = UserRepository(db)
        self.email_service = EmailService()

    # ── Register ────────────────────────────────────────────────────

    async def register(self, user_data: UserRegister) -> UserResponse:
        if self.user_repo.get_by_email(user_data.email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered",
            )

        if self.user_repo.get_by_username(user_data.username):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already taken",
            )

        # Assign default "user" role
        default_role = self.db.query(Role).filter(Role.name == "user").first()

        user = User(
            email=user_data.email,
            username=user_data.username,
            hashed_password=get_password_hash(user_data.password),
            is_active=True,
            is_verified=False,
            role_id=default_role.id if default_role else None,
        )
        user = self.user_repo.create(user)

        # Send verification email
        token = create_email_verification_token(user.email)
        await self.email_service.send_verification_email(user.email, token)

        return _to_response(user)

    # ── Login ───────────────────────────────────────────────────────

    async def login(self, email: str, password: str):
        user = self.user_repo.get_by_email(email)

        if not user or not verify_password(password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Inactive user account",
            )

        return {
            "access_token": create_access_token(subject=str(user.id)),
            "refresh_token": create_refresh_token(subject=str(user.id)),
            "token_type": "bearer",
        }

    # ── Verify email ────────────────────────────────────────────────

    async def verify_email(self, token: str) -> None:
        payload = verify_token(token, "verification")
        if payload is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired verification token",
            )

        email = payload.get("sub")
        user = self.user_repo.get_by_email(email)

        if user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )

        if user.is_verified:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already verified",
            )

        user.is_verified = True
        self.user_repo.update(user)

    # ── Refresh token ───────────────────────────────────────────────

    async def refresh_token(self, refresh_token: str):
        payload = verify_token(refresh_token, "refresh")
        if payload is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired refresh token",
                headers={"WWW-Authenticate": "Bearer"},
            )

        user_id = payload.get("sub")
        user = self.user_repo.get_by_id(user_id)

        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token",
                headers={"WWW-Authenticate": "Bearer"},
            )

        return {
            "access_token": create_access_token(subject=str(user.id)),
            "refresh_token": create_refresh_token(subject=str(user.id)),
            "token_type": "bearer",
        }

    # ── Resend verification ─────────────────────────────────────────

    async def resend_verification(self, email: str) -> None:
        user = self.user_repo.get_by_email(email)

        # Always return success to avoid revealing if email exists
        if not user or user.is_verified:
            return

        token = create_email_verification_token(user.email)
        await self.email_service.send_verification_email(user.email, token)

# ── Helper ──────────────────────────────────────────────────────────

def _to_response(user: User) -> UserResponse:
    return UserResponse(
        id=user.id,
        email=user.email,
        username=user.username,
        is_active=user.is_active,
        is_verified=user.is_verified,
        role=user.role.name if user.role else None,
        created_at=user.created_at,
    )
