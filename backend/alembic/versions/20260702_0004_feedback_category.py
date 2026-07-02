"""Add feedback category taxonomy column."""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect

revision: str = "20260702_0004"
down_revision: Union[str, None] = "20260702_0003"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    columns = {col["name"] for col in inspect(op.get_bind()).get_columns("query_feedback")}
    if "category" in columns:
        return
    op.add_column("query_feedback", sa.Column("category", sa.String(length=32), nullable=True))


def downgrade() -> None:
    op.drop_column("query_feedback", "category")
