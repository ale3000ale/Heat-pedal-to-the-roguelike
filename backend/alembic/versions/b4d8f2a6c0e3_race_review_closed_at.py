"""conferma della revisione delle carte: data di chiusura della revisione della gara

Revision ID: b4d8f2a6c0e3
Revises: a9c3e7b1d5f0
Create Date: 2026-10-12 22:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'b4d8f2a6c0e3'
down_revision: Union[str, Sequence[str], None] = 'a9c3e7b1d5f0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

TABLE = "race"
COLUMN = "review_closed_at"


def upgrade() -> None:
    """Upgrade schema."""
    columns = [col["name"] for col in sa.inspect(op.get_bind()).get_columns(TABLE)]
    if COLUMN in columns:
        return
    op.add_column(TABLE, sa.Column(COLUMN, sa.DateTime(), nullable=True))
    # Le gare che hanno già i risultati sono state chiuse prima di questa regola: le carte
    # giocate sono già state consumate, quindi la revisione risulta conclusa.
    op.execute(
        "UPDATE race SET review_closed_at = CURRENT_TIMESTAMP "
        "WHERE id IN (SELECT race_id FROM race_result)"
    )


def downgrade() -> None:
    """Downgrade schema."""
    with op.batch_alter_table(TABLE) as batch:
        batch.drop_column(COLUMN)
