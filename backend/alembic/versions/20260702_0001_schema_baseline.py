"""Baseline schema extensions: chunk text FTS, live_cache, audit_logs indexes."""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect

revision: str = "20260702_0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _has_column(table: str, column: str) -> bool:
    inspector = inspect(op.get_bind())
    return column in {col["name"] for col in inspector.get_columns(table)}


def _has_index(table: str, index_name: str) -> bool:
    inspector = inspect(op.get_bind())
    return index_name in {idx["name"] for idx in inspector.get_indexes(table)}


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm")
    if not _has_column("chunks", "text"):
        op.add_column("chunks", sa.Column("text", sa.Text(), nullable=True))
    op.execute(
        """
        ALTER TABLE chunks
        ADD COLUMN IF NOT EXISTS search_vector tsvector
        GENERATED ALWAYS AS (
            to_tsvector('simple', coalesce(text, '') || ' ' || coalesce(article_ref, ''))
        ) STORED
        """
    )
    if not _has_index("chunks", "ix_chunks_search_vector"):
        op.create_index("ix_chunks_search_vector", "chunks", ["search_vector"], postgresql_using="gin")
    if not _has_index("live_cache", "ix_live_cache_expires_at"):
        op.create_index("ix_live_cache_expires_at", "live_cache", ["expires_at"], unique=False)
    if not _has_index("audit_logs", "ix_audit_logs_created_at"):
        op.create_index("ix_audit_logs_created_at", "audit_logs", ["created_at"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_audit_logs_created_at", table_name="audit_logs")
    op.drop_index("ix_live_cache_expires_at", table_name="live_cache")
    op.drop_index("ix_chunks_search_vector", table_name="chunks")
    op.execute("ALTER TABLE chunks DROP COLUMN IF EXISTS search_vector")
    op.drop_column("chunks", "text")
