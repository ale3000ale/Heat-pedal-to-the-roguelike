"""ID notifiche non riutilizzabili; backup verificato prima dell'uso sui dati reali."""
from alembic import context, op
import sqlalchemy as sa

revision = "d6f0a4b8c2e7"
down_revision = "d5e9a3b7c1f6"
branch_labels = None
depends_on = None


def _rebuild(autoincrement: bool) -> None:
    """Ricrea card_gift riflettendo colonne, FK e indici e copiando le righe.

    Parametro: presenza di AUTOINCREMENT esplicito SQLite. Ritorno: None.
    Richiede connessione online: la riflessione preserva lo schema esistente.
    Errori di lettura, copia o DDL propagano; nessun errore viene ignorato.
    Non esegue backup: arresto dell'app, backup e prova su copia sono prerequisiti
    operativi prima di eseguire questa migrazione sui dati del gioco.
    """
    if context.is_offline_mode():
        raise RuntimeError("Migrazione card_gift: richiesta connessione SQLite online")
    if op.get_bind().dialect.name != "sqlite":
        raise RuntimeError("Migrazione card_gift prevista esclusivamente per SQLite")
    with op.batch_alter_table(
        "card_gift",
        recreate="always",
        table_kwargs={"sqlite_autoincrement": autoincrement},
    ) as batch:
        batch.alter_column("id", existing_type=sa.Integer(), nullable=False)


def upgrade() -> None:
    """Conserva righe/ID e abilita sqlite_sequence per i nuovi inserimenti."""
    _rebuild(True)


def downgrade() -> None:
    """Conserva righe/ID ma rimuove la garanzia di non riuso: richiede coordinamento."""
    _rebuild(False)
