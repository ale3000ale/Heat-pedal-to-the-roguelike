"""Verifica lo schema del database creato dalle migrazioni Alembic.

Uso (dalla cartella backend, con PYTHONPATH=.):
    python ../.github/scripts/check_migrations.py schema   # tabelle, colonne e indici come nei modelli
    python ../.github/scripts/check_migrations.py empty    # dopo il downgrade resta solo alembic_version

Il database è quello indicato da app.config.DATABASE_URL (file ./heat.db relativo alla
cartella corrente): in CI è un file nuovo del runner, mai il database locale.
"""

import sys

from sqlalchemy import create_engine, inspect

import app.db.models  # noqa: F401  registra tutti i modelli
from app.config import DATABASE_URL
from app.db.base import Base

VERSION_TABLE = "alembic_version"


def check_schema(inspector) -> list[str]:
    # Confronta il database con i modelli e ritorna l'elenco dei problemi trovati.
    problems = []
    db_tables = set(inspector.get_table_names()) - {VERSION_TABLE}
    model_tables = set(Base.metadata.tables)
    for name in sorted(model_tables - db_tables):
        problems.append(f"Tabella mancante nel database: {name}")
    for name in sorted(db_tables - model_tables):
        problems.append(f"Tabella nel database ma non nei modelli: {name}")
    for name in sorted(model_tables & db_tables):
        table = Base.metadata.tables[name]
        db_columns = {column["name"] for column in inspector.get_columns(name)}
        model_columns = {column.name for column in table.columns}
        for column in sorted(model_columns - db_columns):
            problems.append(f"Colonna mancante nel database: {name}.{column}")
        for column in sorted(db_columns - model_columns):
            problems.append(f"Colonna nel database ma non nei modelli: {name}.{column}")
        db_indexes = {index["name"] for index in inspector.get_indexes(name)}
        for index in sorted(index.name for index in table.indexes):
            if index not in db_indexes:
                problems.append(f"Indice mancante nel database: {name}.{index}")
    return problems


def check_empty(inspector) -> list[str]:
    # Dopo il downgrade non devono restare tabelle oltre alla versione di Alembic.
    leftovers = set(inspector.get_table_names()) - {VERSION_TABLE}
    return [f"Tabella rimasta dopo il downgrade: {name}" for name in sorted(leftovers)]


def main(mode: str) -> int:
    inspector = inspect(create_engine(DATABASE_URL))
    if mode == "schema":
        problems = check_schema(inspector)
    elif mode == "empty":
        problems = check_empty(inspector)
    else:
        print(f"Modalità sconosciuta: {mode}")
        return 2
    for problem in problems:
        print(f"::error::{problem}")
    print("OK" if not problems else f"{len(problems)} problemi")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else "schema"))
