"""Aggiunge la bozza della revisione senza alterare i dati esistenti."""
from alembic import op
import sqlalchemy as sa

revision = "a2e6c0d4f8b3"
down_revision = "b4d8f2a6c0e3"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Aggiunge la colonna nullable; non sovrascrive bozze esistenti."""
    columns = sa.inspect(op.get_bind()).get_columns("race")
    if not any(column["name"] == "review_draft" for column in columns):
        op.add_column("race", sa.Column("review_draft", sa.Text(), nullable=True))


def downgrade() -> None:
    """Rimuove la colonna e le bozze: richiede backup prima dell'esecuzione."""
    with op.batch_alter_table("race") as batch:
        batch.drop_column("review_draft")
