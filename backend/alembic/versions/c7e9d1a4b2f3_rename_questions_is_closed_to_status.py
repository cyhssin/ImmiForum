"""rename questions.is_closed to status

Revision ID: c7e9d1a4b2f3
Revises: 83d66e54c850
Create Date: 2026-09-07
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "c7e9d1a4b2f3"
down_revision: Union[str, None] = "83d66e54c850"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    op.alter_column(
        "questions",
        "is_closed",
        new_column_name="status",
        existing_type=sa.String(length=20),
        existing_nullable=False,
    )

def downgrade() -> None:
    op.alter_column(
        "questions",
        "status",
        new_column_name="is_closed",
        existing_type=sa.String(length=20),
        existing_nullable=False,
    )