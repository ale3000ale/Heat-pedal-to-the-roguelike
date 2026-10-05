"""tabella della classifica finale congelata alla chiusura del campionato

Revision ID: f6c0d4e8b3a9
Revises: e5b9c3d7a2f8
Create Date: 2026-10-05 21:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'f6c0d4e8b3a9'
down_revision: Union[str, Sequence[str], None] = 'e5b9c3d7a2f8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Il modello esisteva ma nessuna migrazione creava la tabella: se qualcuno l'ha già
    # creata a mano, non si fa nulla.
    if "championship_standing" in sa.inspect(op.get_bind()).get_table_names():
        return
    op.create_table(
        "championship_standing",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("championship_id", sa.Integer(), nullable=False),
        sa.Column("pilot_name", sa.String(), nullable=False),
        sa.Column("rank", sa.Integer(), nullable=False),
        sa.Column("points", sa.Integer(), nullable=False),
        sa.Column("races_played", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["championship_id"], ["championship.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_championship_standing_id"), "championship_standing", ["id"], unique=False
    )
    op.create_index(
        op.f("ix_championship_standing_championship_id"),
        "championship_standing",
        ["championship_id"],
        unique=False,
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(
        op.f("ix_championship_standing_championship_id"), table_name="championship_standing"
    )
    op.drop_index(op.f("ix_championship_standing_id"), table_name="championship_standing")
    op.drop_table("championship_standing")
