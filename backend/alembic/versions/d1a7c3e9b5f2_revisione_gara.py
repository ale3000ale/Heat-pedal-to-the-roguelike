"""revisione della gara: giudice che la sta chiudendo

Revision ID: d1a7c3e9b5f2
Revises: b2d6f0a4c8e1
Create Date: 2026-10-12 07:10:00.000000

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op


revision: str = 'd1a7c3e9b5f2'
down_revision: Union[str, Sequence[str], None] = 'b2d6f0a4c8e1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema: aggiunge a race il giudice in revisione e l'ora del blocco."""
    with op.batch_alter_table("race") as batch_op:
        batch_op.add_column(sa.Column("reviewer_id", sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column("review_started_at", sa.DateTime(), nullable=True))
        batch_op.create_foreign_key("fk_race_reviewer_id_user", "user", ["reviewer_id"], ["id"])


def downgrade() -> None:
    """Downgrade schema: toglie le due colonne."""
    with op.batch_alter_table("race") as batch_op:
        batch_op.drop_constraint("fk_race_reviewer_id_user", type_="foreignkey")
        batch_op.drop_column("review_started_at")
        batch_op.drop_column("reviewer_id")
