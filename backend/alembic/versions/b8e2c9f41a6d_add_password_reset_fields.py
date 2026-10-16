"""add password reset token fields to users

Revision ID: b8e2c9f41a6d
Revises: f1a8d72c4b90
Create Date: 2026-10-16
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "b8e2c9f41a6d"
down_revision: Union[str, None] = "f1a8d72c4b90"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("users", sa.Column("password_reset_token_hash", sa.String(length=64), nullable=True))
    op.add_column("users", sa.Column("password_reset_expires_at", sa.DateTime(timezone=True), nullable=True))


def downgrade() -> None:
    op.drop_column("users", "password_reset_expires_at")
    op.drop_column("users", "password_reset_token_hash")