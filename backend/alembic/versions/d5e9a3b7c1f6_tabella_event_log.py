"""Registro SSE persistente; eseguire backup prima della migrazione sul database reale."""
from alembic import op
import sqlalchemy as sa

revision = "d5e9a3b7c1f6"
down_revision = "a2e6c0d4f8b3"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Crea solo event_log e gli indici; non modifica le tabelle del gioco."""
    op.create_table(
        "event_log",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("type", sa.String(64), nullable=False),
        sa.Column("championship_id", sa.Integer(), nullable=False),
        sa.Column("pilot_id", sa.Integer(), nullable=True),
        sa.Column("recipient_user_id", sa.Integer(), nullable=True),
        sa.Column("payload", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["championship_id"], ["championship.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["pilot_id"], ["pilot.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["recipient_user_id"], ["user.id"], ondelete="CASCADE"),
        sqlite_autoincrement=True,
    )
    op.create_index("ix_event_log_championship_id_id", "event_log", ["championship_id", "id"])
    op.create_index("ix_event_log_recipient_user_id_id", "event_log", ["recipient_user_id", "id"])
    op.create_index("ix_event_log_created_at", "event_log", ["created_at"])


def downgrade() -> None:
    """Elimina il registro eventi: richiede backup e conferma prima dell'esecuzione reale."""
    op.drop_table("event_log")
