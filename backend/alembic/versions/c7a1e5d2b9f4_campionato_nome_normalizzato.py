"""campionato: nome normalizzato

Revision ID: c7a1e5d2b9f4
Revises: 9f4d32c3525f
Create Date: 2026-10-03 01:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'c7a1e5d2b9f4'
down_revision: Union[str, Sequence[str], None] = '9f4d32c3525f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _normalize(name: str) -> str:
    # Stessa regola del servizio: spazi doppi tolti, maiuscole azzerate.
    return " ".join(name.split()).casefold()


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column("championship", sa.Column("name_key", sa.String(), nullable=True))

    bind = op.get_bind()
    rows = bind.execute(sa.text("SELECT id, name FROM championship")).fetchall()
    for row_id, name in rows:
        bind.execute(
            sa.text("UPDATE championship SET name_key = :key WHERE id = :id"),
            {"key": _normalize(name), "id": row_id},
        )

    with op.batch_alter_table("championship") as batch_op:
        batch_op.alter_column("name_key", existing_type=sa.String(), nullable=False)
        batch_op.create_unique_constraint("uq_championship_name_key", ["name_key"])


def downgrade() -> None:
    """Downgrade schema."""
    with op.batch_alter_table("championship") as batch_op:
        batch_op.drop_constraint("uq_championship_name_key", type_="unique")
        batch_op.drop_column("name_key")