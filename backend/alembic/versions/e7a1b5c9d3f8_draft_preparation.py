"""Preparazione draft separata da race; backup prima dell'uso su dati reali."""
from alembic import op
import sqlalchemy as sa

revision = "e7a1b5c9d3f8"
down_revision = "d6f0a4b8c2e7"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Crea il contenitore draft senza modificare gare, mazzi o pool esistenti."""
    op.create_table(
        "draft_preparation",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("championship_id", sa.Integer(), nullable=False),
        sa.Column("creator_user_id", sa.Integer(), nullable=False),
        sa.Column("phase", sa.String(16), nullable=False),
        sa.Column("state_json", sa.Text(), nullable=False),
        sa.Column("snapshot_json", sa.Text(), nullable=False),
        sa.Column("version", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["championship_id"], ["championship.id"]),
        sa.ForeignKeyConstraint(["creator_user_id"], ["user.id"]),
        sa.UniqueConstraint("championship_id", name="uq_draft_preparation_championship"),
        sa.CheckConstraint("phase IN ('attendance', 'order', 'picking', 'decks')", name="ck_draft_preparation_phase"),
        sa.CheckConstraint("version >= 1", name="ck_draft_preparation_version"),
        sqlite_autoincrement=True,
    )
    op.create_index("ix_draft_preparation_creator_user_id", "draft_preparation", ["creator_user_id"])


def downgrade() -> None:
    """Rimuove le preparazioni: prima dell'uso reale servono backup e conferma."""
    op.drop_index("ix_draft_preparation_creator_user_id", table_name="draft_preparation")
    op.drop_table("draft_preparation")
