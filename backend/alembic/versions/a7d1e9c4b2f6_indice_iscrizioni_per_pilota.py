"""indice sulle iscrizioni ai campionati per pilota

Revision ID: a7d1e9c4b2f6
Revises: f6c0d4e8b3a9
Create Date: 2026-10-06 01:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'a7d1e9c4b2f6'
down_revision: Union[str, Sequence[str], None] = 'f6c0d4e8b3a9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

INDEX_NAME = "ix_championship_pilot_pilot_id"


def upgrade() -> None:
    """Upgrade schema."""
    # Il vincolo unico esistente parte da championship_id: le ricerche per pilota
    # (campionato attivo di uno o più piloti) avevano bisogno di un indice proprio.
    indexes = sa.inspect(op.get_bind()).get_indexes("championship_pilot")
    if any(index["name"] == INDEX_NAME for index in indexes):
        return
    op.create_index(INDEX_NAME, "championship_pilot", ["pilot_id"], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(INDEX_NAME, table_name="championship_pilot")
