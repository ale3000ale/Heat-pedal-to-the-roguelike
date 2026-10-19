from pathlib import Path

from alembic import command
from alembic.config import Config
from alembic.script import ScriptDirectory
from sqlalchemy import create_engine, inspect, text

import app.config

BACKEND_DIR = Path(__file__).resolve().parents[1]
REVISION = "a2e6c0d4f8b3"
PREVIOUS = "b4d8f2a6c0e3"


def test_review_draft_has_one_head():
    config = Config(str(BACKEND_DIR / "alembic.ini"))
    assert ScriptDirectory.from_config(config).get_heads() == [REVISION]


def test_upgrade_preserves_rows_and_draft_on_repeat(tmp_path, monkeypatch):
    url = f"sqlite:///{(tmp_path / 'review.db').as_posix()}"
    monkeypatch.setattr(app.config, "DATABASE_URL", url)
    config = Config(str(BACKEND_DIR / "alembic.ini"))
    command.upgrade(config, PREVIOUS)
    engine = create_engine(url)
    try:
        with engine.begin() as connection:
            connection.execute(text(
                "INSERT INTO championship (id, name, name_key, date, is_closed) "
                "VALUES (1, 'Test', 'test', CURRENT_TIMESTAMP, 0)"
            ))
            connection.execute(text(
                "INSERT INTO race (id, championship_id, number) VALUES (1, 1, 1)"
            ))
        command.upgrade(config, REVISION)
        column = next(c for c in inspect(engine).get_columns("race") if c["name"] == "review_draft")
        assert column["nullable"] is True
        with engine.begin() as connection:
            row = connection.execute(text(
                "SELECT championship_id, number, review_draft FROM race WHERE id = 1"
            )).one()
            assert tuple(row) == (1, 1, None)
            connection.execute(text(
                "UPDATE race SET review_draft = :draft WHERE id = 1"
            ), {"draft": "[]"})
        command.upgrade(config, REVISION)
        with engine.connect() as connection:
            assert connection.scalar(text("SELECT review_draft FROM race WHERE id = 1")) == "[]"
        command.downgrade(config, PREVIOUS)
        assert "review_draft" not in {c["name"] for c in inspect(engine).get_columns("race")}
        with engine.connect() as connection:
            assert connection.scalar(text("SELECT number FROM race WHERE id = 1")) == 1
    finally:
        engine.dispose()
