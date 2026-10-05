"""ruolo giudice e punti sponsor

Revision ID: d4e8a2b6c1f7
Revises: c7a1e5d2b9f4
Create Date: 2026-10-05 14:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'd4e8a2b6c1f7'
down_revision: Union[str, Sequence[str], None] = 'c7a1e5d2b9f4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    with op.batch_alter_table("user") as batch_op:
        batch_op.drop_constraint("ck_user_role", type_="check")
        batch_op.create_check_constraint(
            "ck_user_role", "role IN ('admin', 'judge', 'player')"
        )

    with op.batch_alter_table("race_result") as batch_op:
        batch_op.add_column(
            sa.Column("sponsor_points", sa.Integer(), server_default="0", nullable=False)
        )
        batch_op.create_check_constraint(
            "ck_race_result_sponsor", "sponsor_points >= 0"
        )


def downgrade() -> None:
    """Downgrade schema."""
    with op.batch_alter_table("race_result") as batch_op:
        batch_op.drop_constraint("ck_race_result_sponsor", type_="check")
        batch_op.drop_column("sponsor_points")

    # I giudici tornano giocatori prima di rimettere il vincolo vecchio.
    op.execute(sa.text("UPDATE \"user\" SET role = 'player' WHERE role = 'judge'"))
    with op.batch_alter_table("user") as batch_op:
        batch_op.drop_constraint("ck_user_role", type_="check")
        batch_op.create_check_constraint("ck_user_role", "role IN ('admin', 'player')")
