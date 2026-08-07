import logging

from app.core.config import settings

logger = logging.getLogger(__name__)

class EmailService:
    """Console-based email service for development.

    Replace the send_verification_email method with a real
    SMTP call (e.g. FastAPI-Mail) when moving to production.
    """

    @staticmethod
    async def send_verification_email(email: str, token: str) -> None:
        verification_url = f"{settings.APP_URL}{settings.API_V1_PREFIX}/auth/verify-email?token={token}"

        # ── Development: log to console ──
        logger.info("Verification email for %s", email)
        print(
            f"\n{'='*40}\n"
            f"  VERIFICATION EMAIL\n"
            f"  To:   {email}\n"
            f"  URL:  {verification_url}\n"
            f"{'='*40}\n"
        )

        # ── Production placeholder ──
        # await smtp_client.send_message(...)
