"""stato in revisione della gara

Revision ID: d4f8b2e6a0c3
Revises: c3e7a1d5b9f2
Create Date: 2026-10-12 17:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'd4f8b2e6a0c3'
down_revision: Union[str, Sequence[str], None] = 'c3e7a1d5b9f2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    columns = [c["name"] for c in sa.inspect(op.get_bind()).get_columns("race")]
    if "review_started_at" in columns:
        return
    with op.batch_alter_table("race") as batch:
        batch.add_column(sa.Column("review_started_at", sa.DateTime(), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    with op.batch_alter_table("race") as batch:
        batch.drop_column("review_started_at")
