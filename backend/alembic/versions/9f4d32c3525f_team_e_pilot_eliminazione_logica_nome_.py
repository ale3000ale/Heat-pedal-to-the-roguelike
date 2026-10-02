"""team e pilot: eliminazione logica, nome normalizzato, team facoltativo

Revision ID: 9f4d32c3525f
Revises: 3daf355a6ffd
Create Date: 2026-10-02 18:39:04.614423

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9f4d32c3525f'
down_revision: Union[str, Sequence[str], None] = '3daf355a6ffd'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _normalize(name: str) -> str:
    # Stessa regola del servizio: spazi doppi tolti, maiuscole azzerate.
    return " ".join(name.split()).casefold()


def upgrade() -> None:
    """Upgrade schema."""
    # 1. Nuove colonne, per ora facoltative (le righe esistenti non hanno valori).
    for table in ("team", "pilot"):
        op.add_column(table, sa.Column("deleted_at", sa.DateTime(), nullable=True))
        op.add_column(table, sa.Column("name_key", sa.String(), nullable=True))

    # 2. Riempie name_key per le righe già presenti, prima di renderla obbligatoria.
    bind = op.get_bind()
    for table in ("team", "pilot"):
        rows = bind.execute(sa.text(f"SELECT id, name FROM {table}")).fetchall()
        for row_id, name in rows:
            bind.execute(
                sa.text(f"UPDATE {table} SET name_key = :key WHERE id = :id"),
                {"key": _normalize(name), "id": row_id},
            )

    # 3. Rende name_key obbligatoria e unica (SQLite ricrea la tabella: modalità batch).
    with op.batch_alter_table("team") as batch_op:
        batch_op.alter_column("name_key", existing_type=sa.String(), nullable=False)
        batch_op.create_unique_constraint("uq_team_name_key", ["name_key"])

    with op.batch_alter_table("pilot") as batch_op:
        batch_op.alter_column("name_key", existing_type=sa.String(), nullable=False)
        batch_op.alter_column("team_id", existing_type=sa.Integer(), nullable=True)
        batch_op.create_unique_constraint("uq_pilot_name_key", ["name_key"])


def downgrade() -> None:
    """Downgrade schema."""
    # Un pilota senza team non può tornare nello schema precedente.
    bind = op.get_bind()
    orphans = bind.execute(sa.text("SELECT COUNT(*) FROM pilot WHERE team_id IS NULL")).scalar()
    if orphans:
        raise RuntimeError("Downgrade impossibile: esistono piloti senza team")

    with op.batch_alter_table("pilot") as batch_op:
        batch_op.drop_constraint("uq_pilot_name_key", type_="unique")
        batch_op.alter_column("team_id", existing_type=sa.Integer(), nullable=False)
        batch_op.drop_column("name_key")
        batch_op.drop_column("deleted_at")

    with op.batch_alter_table("team") as batch_op:
        batch_op.drop_constraint("uq_team_name_key", type_="unique")
        batch_op.drop_column("name_key")
        batch_op.drop_column("deleted_at")