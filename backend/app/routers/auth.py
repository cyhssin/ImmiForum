from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.auth import (
    MessageResponse,
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
    """OAuth2-compatible login. Use **email** as the username field."""
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
