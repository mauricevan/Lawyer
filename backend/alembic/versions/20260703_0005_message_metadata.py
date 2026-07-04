"""Add JSONB metadata column to messages."""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect
from sqlalchemy.dialects.postgresql import JSONB

revision: str = "20260703_0005"
down_revision: Union[str, None] = "20260702_0004"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    columns = {col["name"] for col in inspect(op.get_bind()).get_columns("messages")}
    if "metadata" in columns:
        return
    op.add_column("messages", sa.Column("metadata", JSONB, nullable=True))


def downgrade() -> None:
    op.drop_column("messages", "metadata")
