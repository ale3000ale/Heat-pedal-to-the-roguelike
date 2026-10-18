"""intervallo di controllo delle notifiche delle carte nelle impostazioni generali

Revision ID: f8a4d2c6e0b1
Revises: e7a3c9d1f5b2
Create Date: 2026-10-12 18:10:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'f8a4d2c6e0b1'
down_revision: Union[str, Sequence[str], None] = 'e7a3c9d1f5b2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

TABLE = "championship_defaults"
COLUMN = "card_poll_seconds"


def upgrade() -> None:
    """Upgrade schema."""
    columns = [col["name"] for col in sa.inspect(op.get_bind()).get_columns(TABLE)]
    if COLUMN in columns:
        return
    op.add_column(
        TABLE,
        sa.Column(COLUMN, sa.Integer(), nullable=False, server_default="5"),
    )


def downgrade() -> None:
    """Downgrade schema."""
    with op.batch_alter_table(TABLE) as batch:
        batch.drop_column(COLUMN)
