"""pool di mappe ed eventi per campionato

Revision ID: c1d5e9f3a7b2
Revises: b8f4e2a1c7d9
Create Date: 2026-11-24 20:00:00.000000

"""
import json
from pathlib import Path

from alembic import op
import sqlalchemy as sa


revision = "c1d5e9f3a7b2"
down_revision = "b8f4e2a1c7d9"
branch_labels = None
depends_on = None

BACKEND_DIR = Path(__file__).resolve().parents[2]
JSON_DIR_NAMES = ("JSON", "json")


def _catalog_ids(filename: str) -> list[int]:
    """ID del catalogo letto dai JSON; lista vuota se il file non è disponibile."""
    for name in JSON_DIR_NAMES:
        path = BACKEND_DIR / name / filename
        if not path.is_file():
            continue
        try:
            items = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, UnicodeError, json.JSONDecodeError):
            return []
        if not isinstance(items, list):
            return []
        ids: list[int] = []
        for item in items:
            if not isinstance(item, dict):
                continue
            value = item.get("id")
            if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
                continue
            if value not in ids:
                ids.append(value)
        return ids
    return []


def upgrade() -> None:
    """Aggiunge le due pool e le inizializza per i campionati esistenti."""
    op.add_column("championship", sa.Column("map_pool_ids", sa.Text(), nullable=True))
    op.add_column("championship", sa.Column("event_pool_ids", sa.Text(), nullable=True))
    map_ids = _catalog_ids("maps.json")
    event_ids = _catalog_ids("events.json")
    # Con catalogo non disponibile la colonna resta NULL: la pool verrà inizializzata
    # alla prima operazione che ne ha bisogno.
    if map_ids:
        op.get_bind().execute(
            sa.text("UPDATE championship SET map_pool_ids = :ids"),
            {"ids": json.dumps(map_ids)},
        )
    if event_ids:
        op.get_bind().execute(
            sa.text("UPDATE championship SET event_pool_ids = :ids"),
            {"ids": json.dumps(event_ids)},
        )


def downgrade() -> None:
    """Rimuove le due pool."""
    op.drop_column("championship", "event_pool_ids")
    op.drop_column("championship", "map_pool_ids")
