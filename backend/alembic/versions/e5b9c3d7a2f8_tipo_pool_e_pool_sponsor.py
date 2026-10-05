"""tipo della pool e seconda pool del campionato (sponsor)

Revision ID: e5b9c3d7a2f8
Revises: d4e8a2b6c1f7
Create Date: 2026-10-05 19:40:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'e5b9c3d7a2f8'
down_revision: Union[str, Sequence[str], None] = 'd4e8a2b6c1f7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Le pool esistenti sono tutte di modifiche (valore predefinito).
    with op.batch_alter_table("deck_prototype") as batch_op:
        batch_op.add_column(
            sa.Column("kind", sa.String(), server_default="modifiche", nullable=False)
        )

    with op.batch_alter_table("championship") as batch_op:
        batch_op.add_column(sa.Column("sponsor_pool_deck_id", sa.Integer(), nullable=True))
        batch_op.create_foreign_key(
            "fk_championship_sponsor_pool_deck", "deck", ["sponsor_pool_deck_id"], ["id"]
        )

    # Pool di base degli sponsor: parte vuota, si riempie con la ricarica.
    op.execute(
        sa.text(
            "INSERT INTO deck_prototype (name, base_cards, kind) "
            "SELECT 'sponsor', '[]', 'sponsor' "
            "WHERE NOT EXISTS (SELECT 1 FROM deck_prototype WHERE name = 'sponsor')"
        )
    )


def downgrade() -> None:
    """Downgrade schema."""
    with op.batch_alter_table("championship") as batch_op:
        batch_op.drop_constraint("fk_championship_sponsor_pool_deck", type_="foreignkey")
        batch_op.drop_column("sponsor_pool_deck_id")

    # Le pool degli sponsor non esistono nello schema precedente.
    op.execute(sa.text("DELETE FROM deck WHERE id_prototype IN "
                       "(SELECT id FROM deck_prototype WHERE kind = 'sponsor')"))
    op.execute(sa.text("DELETE FROM deck_prototype WHERE kind = 'sponsor'"))
    with op.batch_alter_table("deck_prototype") as batch_op:
        batch_op.drop_column("kind")
