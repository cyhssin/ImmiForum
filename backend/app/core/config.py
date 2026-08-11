import os
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "postgresql://postgres:postgres@db:5432/forum_db"

    # JWT
    SECRET_KEY: str = os.getenv("SECRET_KEY")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # Email Verification
    VERIFICATION_TOKEN_EXPIRE_HOURS: int = 24

    # SMTP (Gmail)
    SMTP_HOST: Optional[str] = "smtp.gmail.com"
    SMTP_PORT: Optional[int] = 587
    SMTP_USER: Optional[str] = os.getenv("SMTP_USER")
    SMTP_PASSWORD: Optional[str] = None
    SMTP_STARTTLS: bool = True
    EMAILS_FROM_EMAIL: str = os.getenv("EMAILS_FROM_EMAIL")

    # App
    APP_NAME: str = "Immigrant Forum"
    APP_URL: str = "http://localhost:8000"
    API_V1_PREFIX: str = "/api/v1"

    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
