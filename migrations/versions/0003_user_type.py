"""add user_type to users

Revision ID: 0003_user_type
Revises: 0002_user_name_fields
Create Date: 2026-01-29 00:00:00.000000
"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa

revision = "0003_user_type"
down_revision = "0002_user_name_fields"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "users",
        sa.Column(
            "user_type",
            sa.Integer(),
            nullable=False,
            server_default=sa.text("1"),
        ),
    )


def downgrade() -> None:
    op.drop_column("users", "user_type")
