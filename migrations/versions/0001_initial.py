"""initial schema

Revision ID: 0001_initial
Revises: None
Create Date: 2024-01-01 00:00:00.000000
"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from pgvector.sqlalchemy import Vector
from sqlalchemy.dialects import postgresql

revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")

    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("username", sa.String(length=128), nullable=False, unique=True),
        sa.Column("hashed_password", sa.Text(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    op.create_table(
        "items",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("metadata", postgresql.JSONB(), nullable=True),
        sa.Column("embedding", Vector(384), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    op.execute(
        """
        DO $$
        BEGIN
            BEGIN
                EXECUTE 'CREATE INDEX IF NOT EXISTS items_embedding_hnsw ON items USING hnsw (embedding vector_cosine_ops)';
            EXCEPTION WHEN undefined_object OR feature_not_supported THEN
                EXECUTE 'CREATE INDEX IF NOT EXISTS items_embedding_ivfflat ON items USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100)';
            END;
        END $$;
        """
    )


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS items_embedding_hnsw")
    op.execute("DROP INDEX IF EXISTS items_embedding_ivfflat")
    op.drop_table("items")
    op.drop_table("users")
