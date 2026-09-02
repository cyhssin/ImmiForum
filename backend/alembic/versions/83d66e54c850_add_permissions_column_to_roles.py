"""add permissions column to roles

Revision ID: 83d66e54c850
Revises: fd495a809df0
Create Date: 2026-08-11 ...
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '83d66e54c850'
down_revision: Union[str, None] = 'fd495a809df0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# Default permissions for existing roles (used for backfilling)
ROLE_PERMISSIONS_BACKFILL = {
    "user": [
        "create_question",
        "create_comment",
        "like_question",
        "bookmark_question",
        "follow_user",
    ],
    "moderator": [
        "create_question",
        "create_comment",
        "like_question",
        "bookmark_question",
        "follow_user",
        "close_question",
        "pin_question",
        "delete_comment",
    ],
    "admin": [
        "create_question",
        "create_comment",
        "like_question",
        "bookmark_question",
        "follow_user",
        "close_question",
        "pin_question",
        "delete_comment",
        "delete_question",
        "manage_users",
        "manage_roles",
    ],
}

def upgrade() -> None:
    # 1. Add column as nullable first
    op.add_column('roles', sa.Column('permissions', sa.JSON(), nullable=True))

    # 2. Backfill existing rows with default permissions
    roles_table = sa.table(
        'roles',
        sa.column('name', sa.String),
        sa.column('permissions', sa.JSON),
    )
    for role_name, permissions in ROLE_PERMISSIONS_BACKFILL.items():
        op.execute(
            roles_table.update()
            .where(roles_table.c.name == role_name)
            .values(permissions=permissions)
        )

    # 3. Any other roles get empty permissions list (safety net)
    op.execute("UPDATE roles SET permissions = '[]' WHERE permissions IS NULL")

    # 4. Now set NOT NULL constraint
    op.alter_column('roles', 'permissions', nullable=False)

def downgrade() -> None:
    op.drop_column('roles', 'permissions')
