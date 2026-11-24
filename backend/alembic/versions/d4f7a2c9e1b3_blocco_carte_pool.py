"""blocco delle carte nelle pool di mappe ed eventi

Revision ID: d4f7a2c9e1b3
Revises: c1d5e9f3a7b2
Create Date: 2026-11-24 21:30:00.000000

"""
import json

from alembic import op
import sqlalchemy as sa


revision = "d4f7a2c9e1b3"
down_revision = "c1d5e9f3a7b2"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Aggiunge le colonne degli ID bloccati, vuote per i campionati esistenti."""
    op.add_column("championship", sa.Column("map_blocked_ids", sa.Text(), nullable=True))
    op.add_column("championship", sa.Column("event_blocked_ids", sa.Text(), nullable=True))
    bind = op.get_bind()
    for column in ("map_blocked_ids", "event_blocked_ids"):
        bind.execute(
            sa.text(f"UPDATE championship SET {column} = :ids"),
            {"ids": json.dumps([])},
        )


def downgrade() -> None:
    """Rimuove le colonne degli ID bloccati."""
    op.drop_column("championship", "event_blocked_ids")
    op.drop_column("championship", "map_blocked_ids")
