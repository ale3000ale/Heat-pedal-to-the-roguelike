from pathlib import Path

from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, inspect

import app.config
import app.db.models  # noqa: F401
from app.db.base import Base

BACKEND_DIR = Path(__file__).resolve().parents[1]


def test_migrazioni_riproducono_i_modelli(tmp_path, monkeypatch):
    # Gli altri test creano le tabelle dai modelli: qui si applicano invece le migrazioni
    # a un database vuoto, come succede sul database vero, e si confronta il risultato.
    url = f"sqlite:///{(tmp_path / 'migrazioni.db').as_posix()}"
    monkeypatch.setattr(app.config, "DATABASE_URL", url)

    command.upgrade(Config(str(BACKEND_DIR / "alembic.ini")), "head")

    engine = create_engine(url)
    try:
        inspector = inspect(engine)
        tables = set(inspector.get_table_names()) - {"alembic_version"}
        assert tables == set(Base.metadata.tables), "tabelle diverse tra migrazioni e modelli"
        for name, table in Base.metadata.tables.items():
            columns = {column["name"] for column in inspector.get_columns(name)}
            assert columns == {column.name for column in table.columns}, (
                f"colonne diverse nella tabella {name}"
            )
    finally:
        engine.dispose()
