"""notifiche delle carte sponsor regalate con il tasto S

Revision ID: e7a3c9d1f5b2
Revises: d4f8b2e6a0c3
Create Date: 2026-10-12 17:40:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'e7a3c9d1f5b2'
down_revision: Union[str, Sequence[str], None] = 'd4f8b2e6a0c3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    if "card_gift" in sa.inspect(op.get_bind()).get_table_names():
        return
    op.create_table(
        "card_gift",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("race_id", sa.Integer(), nullable=False),
        sa.Column("pilot_id", sa.Integer(), nullable=False),
        sa.Column("card_name", sa.String(), nullable=False),
        sa.Column("card_path", sa.String(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("seen_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["race_id"], ["race.id"]),
        sa.ForeignKeyConstraint(["pilot_id"], ["pilot.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_card_gift_id"), "card_gift", ["id"], unique=False)
    op.create_index("ix_card_gift_pilot_seen", "card_gift", ["pilot_id", "seen_at"], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index("ix_card_gift_pilot_seen", table_name="card_gift")
    op.drop_index(op.f("ix_card_gift_id"), table_name="card_gift")
    op.drop_table("card_gift")
