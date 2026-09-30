import logging
from email.message import EmailMessage
from urllib.parse import urlencode

from aiosmtplib import SMTP

from app.core.config import settings

logger = logging.getLogger(__name__)

class EmailService:
    """Sends emails via SMTP. Falls back to console logging if SMTP is not configured."""

    @staticmethod
    async def send_verification_email(email: str, token: str) -> None:
        verification_url = (
            f"{settings.FRONTEND_URL.rstrip('/')}"
            f"/auth/verify-email?{urlencode({'token': token})}"
        )

        subject = "Verify your email — Forum"

        body = (
            f"Hey there!\n\n"
            f"Thank you for joining our community. We’re excited to have you with us!\n\n"
            f"To get started, please verify your email address by clicking the button below:\n\n"
            f"{verification_url}\n\n"
            f"This link expires in "
            f"{settings.VERIFICATION_TOKEN_EXPIRE_HOURS} hours.\n\n"
            f"If you didn’t create an account with us, you can safely ignore this email.\n\n"
            f"Welcome to the community! 🎉\n\n"
            f"Best regards,\n"
            f"The Immigrants Team"
        )

        # SMTP is not configured
        if not settings.SMTP_HOST:
            logger.info(
                "SMTP not configured — printing verification email to console"
            )

            print(
                f"\n{'=' * 50}\n"
                f"  VERIFICATION EMAIL\n"
                f"  To:      {email}\n"
                f"  Subject: {subject}\n"
                f"  URL:     {verification_url}\n"
                f"{'=' * 50}\n"
            )

            return

        message = EmailMessage()
        message["From"] = settings.EMAILS_FROM_EMAIL
        message["To"] = email
        message["Subject"] = subject
        message.set_content(body)

        smtp = SMTP(
            hostname=settings.SMTP_HOST,
            port=settings.SMTP_PORT or 587,
            start_tls=settings.SMTP_STARTTLS,
        )

        try:
            await smtp.connect()

            await smtp.login(
                settings.SMTP_USER,
                settings.SMTP_PASSWORD,
            )

            await smtp.send_message(message)

            logger.info(
                "Verification email sent to %s",
                email,
            )

        except Exception:
            logger.exception(
                "Failed to send verification email to %s",
                email,
            )

            raise

        finally:
            try:
                await smtp.quit()
            except Exception:
                pass