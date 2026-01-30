"""add user name fields

Revision ID: 0002_user_name_fields
Revises: 0001_initial
Create Date: 2026-01-29 00:00:00.000000
"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa

revision = "0002_user_name_fields"
down_revision = "0001_initial"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "users",
        sa.Column(
            "first_name",
            sa.String(length=128),
            nullable=False,
            server_default=sa.text("''"),
        ),
    )
    op.add_column(
        "users",
        sa.Column(
            "last_name",
            sa.String(length=128),
            nullable=False,
            server_default=sa.text("''"),
        ),
    )


def downgrade() -> None:
    op.drop_column("users", "last_name")
    op.drop_column("users", "first_name")
