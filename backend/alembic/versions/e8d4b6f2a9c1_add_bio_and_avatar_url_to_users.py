"""add bio and avatar_url to users

Revision ID: e8d4b6f2a9c1
Revises: c7e9d1a4b2f3
Create Date: 2026-09-07
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "e8d4b6f2a9c1"
down_revision: Union[str, None] = "c7e9d1a4b2f3"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    op.add_column("users", sa.Column("bio", sa.Text(), nullable=True))
    op.add_column("users", sa.Column("avatar_url", sa.String(length=500), nullable=True))

def downgrade() -> None:
    op.drop_column("users", "avatar_url")
    op.drop_column("users", "bio")