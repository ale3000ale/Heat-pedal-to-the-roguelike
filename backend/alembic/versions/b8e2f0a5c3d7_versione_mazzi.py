"""colonna version sui mazzi per il blocco ottimistico

Revision ID: b8e2f0a5c3d7
Revises: a7d1e9c4b2f6
Create Date: 2026-10-06 01:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'b8e2f0a5c3d7'
down_revision: Union[str, Sequence[str], None] = 'a7d1e9c4b2f6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    columns = sa.inspect(op.get_bind()).get_columns("deck")
    if any(column["name"] == "version" for column in columns):
        return
    # I mazzi esistenti partono dalla versione 1.
    op.add_column(
        "deck",
        sa.Column("version", sa.Integer(), nullable=False, server_default="1"),
    )


def downgrade() -> None:
    """Downgrade schema."""
    with op.batch_alter_table("deck") as batch_op:
        batch_op.drop_column("version")
