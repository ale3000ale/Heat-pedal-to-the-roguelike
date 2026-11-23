"""Estrazione mappa ed evento per la prossima gara."""
from alembic import op
import sqlalchemy as sa

revision = "b8f4e2a1c7d9"
down_revision = "e7a1b5c9d3f8"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Aggiunge i percorsi del setup senza modificare campionati o gare esistenti."""
    op.add_column("championship", sa.Column("next_map_path", sa.String(), nullable=True))
    op.add_column("championship", sa.Column("next_event_path", sa.String(), nullable=True))


def downgrade() -> None:
    """Rimuove i percorsi del setup."""
    op.drop_column("championship", "next_event_path")
    op.drop_column("championship", "next_map_path")
