"""regole dell'oro per gara e impostazioni generali dei campionati

Revision ID: c9f3a1b6d8e4
Revises: b8e2f0a5c3d7
Create Date: 2026-10-06 15:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'c9f3a1b6d8e4'
down_revision: Union[str, Sequence[str], None] = 'b8e2f0a5c3d7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# Colonne con il loro valore predefinito: base 20, tutti i modificatori a 0.
GOLD_COLUMNS = [
    ("gold_base", "20"),
    ("gold_pos_1", "0"),
    ("gold_pos_2", "0"),
    ("gold_pos_3", "0"),
    ("gold_pos_4", "0"),
    ("gold_pos_5", "0"),
    ("gold_pos_6", "0"),
    ("gold_pos_other", "0"),
]


def _gold_columns() -> list[sa.Column]:
    return [
        sa.Column(name, sa.Integer(), nullable=False, server_default=default)
        for name, default in GOLD_COLUMNS
    ]


def upgrade() -> None:
    """Upgrade schema."""
    inspector = sa.inspect(op.get_bind())
    existing = {column["name"] for column in inspector.get_columns("championship")}
    # I campionati esistenti ricevono i valori predefiniti.
    for column in _gold_columns():
        if column.name not in existing:
            op.add_column("championship", column)
    if "championship_defaults" not in inspector.get_table_names():
        op.create_table(
            "championship_defaults",
            sa.Column("id", sa.Integer(), primary_key=True),
            *_gold_columns(),
        )
        op.execute(sa.text("INSERT INTO championship_defaults (id) VALUES (1)"))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("championship_defaults")
    with op.batch_alter_table("championship") as batch_op:
        for name, _ in GOLD_COLUMNS:
            batch_op.drop_column(name)
