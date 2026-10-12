"""revisore unico della gara: utente che ha aperto la revisione

Revision ID: a9c3e7b1d5f0
Revises: f8a4d2c6e0b1
Create Date: 2026-10-12 22:10:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'a9c3e7b1d5f0'
down_revision: Union[str, Sequence[str], None] = 'f8a4d2c6e0b1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

TABLE = "race"
COLUMN = "review_started_by_user_id"
FOREIGN_KEY = "fk_race_review_started_by_user_id"


def upgrade() -> None:
    """Upgrade schema."""
    columns = [col["name"] for col in sa.inspect(op.get_bind()).get_columns(TABLE)]
    if COLUMN in columns:
        return
    with op.batch_alter_table(TABLE) as batch:
        batch.add_column(sa.Column(COLUMN, sa.Integer(), nullable=True))
        batch.create_foreign_key(FOREIGN_KEY, "user", [COLUMN], ["id"])


def downgrade() -> None:
    """Downgrade schema."""
    with op.batch_alter_table(TABLE) as batch:
        batch.drop_constraint(FOREIGN_KEY, type_="foreignkey")
        batch.drop_column(COLUMN)
