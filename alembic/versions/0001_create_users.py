"""Create users table for email and password authentication.

Revision ID: 0001_create_users
Revises:
Create Date: 2026-09-26
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0001_create_users"
down_revision: str | Sequence[str] | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column(
            "email",
            sa.String(length=254, collation="utf8mb4_0900_ai_ci"),
            nullable=False,
        ),
        sa.Column(
            "nickname",
            sa.String(length=16, collation="utf8mb4_0900_ai_ci"),
            nullable=False,
        ),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("email", name="uq_users_email"),
        sa.UniqueConstraint("nickname", name="uq_users_nickname"),
    )


def downgrade() -> None:
    op.drop_table("users")
