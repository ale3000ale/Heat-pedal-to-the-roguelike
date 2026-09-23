# backend/init_db.py
# Script standalone per inizializzare heat.db eseguendo lo schema HeatDB_extended.sql.
# Esegui con: python init_db.py  (dalla cartella backend/)

import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "heat.db"
SQL_SCHEMA_PATH = Path(__file__).parent / "HeatDB_extended.sql"


# init_database(db_path, sql_path)
# db_path: percorso del file SQLite da creare/aggiornare; sql_path: percorso dello script SQL schema.
# Legge lo script SQL e lo esegue sul DB, creando tutte le tabelle se non esistono gia'.
def init_database(db_path: Path, sql_path: Path) -> None:
    sql_script = sql_path.read_text(encoding="utf-8")
    conn = sqlite3.connect(db_path)
    try:
        conn.executescript(sql_script)
        conn.commit()
        print(f"Database inizializzato correttamente in: {db_path}")
    finally:
        conn.close()


if __name__ == "__main__":
    init_database(DB_PATH, SQL_SCHEMA_PATH)
