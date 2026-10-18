"""registro delle carte sponsor giocate in gara

Revision ID: c3e7a1d5b9f2
Revises: b2d6f0a4c8e1
Create Date: 2026-10-12 08:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'c3e7a1d5b9f2'
down_revision: Union[str, Sequence[str], None] = 'b2d6f0a4c8e1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    if "card_play" in sa.inspect(op.get_bind()).get_table_names():
        return
    op.create_table(
        "card_play",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("race_id", sa.Integer(), nullable=False),
        sa.Column("pilot_id", sa.Integer(), nullable=False),
        sa.Column("card_name", sa.String(), nullable=False),
        sa.Column("card_path", sa.String(), nullable=False),
        sa.Column("status", sa.String(), nullable=False, server_default="giocata"),
        sa.Column("played_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.CheckConstraint(
            "status IN ('giocata', 'annullata', 'consumata')", name="ck_card_play_status"
        ),
        sa.ForeignKeyConstraint(["race_id"], ["race.id"]),
        sa.ForeignKeyConstraint(["pilot_id"], ["pilot.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_card_play_id"), "card_play", ["id"], unique=False)
    op.create_index("ix_card_play_race_pilot", "card_play", ["race_id", "pilot_id"], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index("ix_card_play_race_pilot", table_name="card_play")
    op.drop_index(op.f("ix_card_play_id"), table_name="card_play")
    op.drop_table("card_play")
