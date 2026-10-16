from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.auth import (
    MessageResponse,
    PasswordResetConfirm,
    PasswordResetRequest,
    RefreshTokenRequest,
    ResendVerificationRequest,
    Token,
    UserRegister,
    UserResponse,
    VerificationRequest,
)
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserRegister, db: Session = Depends(get_db)):
    """Register a new user. A verification email is sent automatically."""
    service = AuthService(db)
    return await service.register(user_data)

@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    """OAuth2-compatible login using a username or email and password."""
    service = AuthService(db)
    return await service.login(form_data.username, form_data.password)

@router.post("/verify-email", response_model=MessageResponse)
async def verify_email(
    verification: VerificationRequest,
    db: Session = Depends(get_db),
):
    """Verify a user's email with the token sent during registration."""
    service = AuthService(db)
    await service.verify_email(verification.token)
    return MessageResponse(message="Email successfully verified")

@router.post("/refresh", response_model=Token)
async def refresh_token(request: RefreshTokenRequest, db: Session = Depends(get_db)):
    """Obtain new access/refresh tokens using a valid refresh token."""
    service = AuthService(db)
    return await service.refresh_token(request.refresh_token)

@router.post("/resend-verification", response_model=MessageResponse)
async def resend_verification(
    data: ResendVerificationRequest,
    db: Session = Depends(get_db),
):
    """Resend the email verification link (if the email exists and is unverified)."""
    service = AuthService(db)
    await service.resend_verification(data.email)
    return MessageResponse(
        message="If the email exists and is not yet verified, a new link has been sent"
    )

@router.post("/forgot-password", response_model=MessageResponse)
async def forgot_password(
    data: PasswordResetRequest,
    db: Session = Depends(get_db),
):
    """Send a password reset link without revealing whether the email exists."""
    service = AuthService(db)
    await service.request_password_reset(data.email)
    return MessageResponse(
        message="If an active account exists for this email, a password reset link has been sent"
    )

@router.post("/reset-password", response_model=MessageResponse)
async def reset_password(
    data: PasswordResetConfirm,
    db: Session = Depends(get_db),
):
    """Set a new password using a valid, single-use reset token."""
    service = AuthService(db)
    service.reset_password(data)
    return MessageResponse(message="Password successfully reset")
