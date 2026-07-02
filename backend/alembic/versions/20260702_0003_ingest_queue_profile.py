"""Add ingest queue profile column."""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "20260702_0003"
down_revision: Union[str, None] = "20260702_0002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "ingestion_jobs",
        sa.Column("queue_profile", sa.String(length=32), server_default="high", nullable=False),
    )


def downgrade() -> None:
    op.drop_column("ingestion_jobs", "queue_profile")
