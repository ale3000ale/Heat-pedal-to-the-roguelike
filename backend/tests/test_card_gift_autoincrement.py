"""Non riuso ID e migrazione su SQLite temporanei, mai sul database del gioco."""
from datetime import datetime
from pathlib import Path

from alembic import command
from alembic.config import Config
from alembic.script import ScriptDirectory
from sqlalchemy import create_engine, inspect, select, text
from sqlalchemy.orm import Session

import app.config
from app.db.models import CardGift, Championship, Deck, Pilot, Race, User
from tests.test_card_gifts import gift, scenario

BACKEND_DIR = Path(__file__).resolve().parents[1]
REVISION = "d6f0a4b8c2e7"
PREVIOUS = "d5e9a3b7c1f6"


def _rows(engine):
    with engine.connect() as connection:
        return [tuple(row) for row in connection.execute(text(
            "SELECT id, race_id, pilot_id, card_name, card_path, created_at, seen_at "
            "FROM card_gift ORDER BY id"
        ))]


def _shape(engine):
    inspector = inspect(engine)
    columns = {(c["name"], str(c["type"]), c["nullable"]) for c in inspector.get_columns("card_gift")}
    indexes = {(i["name"], tuple(i["column_names"]), i["unique"]) for i in inspector.get_indexes("card_gift")}
    keys = {(tuple(f["constrained_columns"]), f["referred_table"], tuple(f["referred_columns"]))
            for f in inspector.get_foreign_keys("card_gift")}
    return columns, indexes, keys


def _sql(engine):
    with engine.connect() as connection:
        return connection.scalar(text(
            "SELECT sql FROM sqlite_master WHERE type = 'table' AND name = 'card_gift'"
        ))


def _seed(engine):
    with Session(engine) as db:
        user = User(username="migration", password="unused-test-hash", role="player")
        championship = Championship(name="Migration", name_key="migration")
        decks = [Deck(cards="[]") for _ in range(3)]
        db.add_all([user, championship, *decks])
        db.flush()
        pilot = Pilot(
            name="Migration Pilot", name_key="migration pilot", user_id=user.id,
            inventory_deck_id=decks[0].id, sponsor_inventory_deck_id=decks[1].id,
            game_deck_id=decks[2].id,
        )
        race = Race(championship_id=championship.id, number=1)
        db.add_all([pilot, race])
        db.flush()
        for gift_id, seen_at in [(7, None), (41, datetime(2026, 10, 20, 12, 30))]:
            db.add(CardGift(
                id=gift_id, race_id=race.id, pilot_id=pilot.id,
                card_name="Test Sponsor", card_path="cards/test.webp",
                created_at=datetime(2026, 10, 20, 12, 0), seen_at=seen_at,
            ))
        db.commit()
        return race.id, pilot.id


def _insert(engine, race_id, pilot_id):
    with engine.begin() as connection:
        result = connection.execute(text(
            "INSERT INTO card_gift (race_id, pilot_id, card_name, card_path) "
            "VALUES (:race, :pilot, 'Test Sponsor', 'cards/test.webp')"
        ), {"race": race_id, "pilot": pilot_id})
        return result.lastrowid


def test_revision_is_in_single_head_chain():
    scripts = ScriptDirectory.from_config(Config(str(BACKEND_DIR / "alembic.ini")))
    heads = scripts.get_heads()
    assert len(heads) == 1
    assert scripts.get_revision(REVISION).down_revision == PREVIOUS
    assert REVISION in {r.revision for r in scripts.walk_revisions(base="base", head=heads[0])}


def test_migration_preserves_rows_indexes_keys_and_prevents_reuse(tmp_path, monkeypatch):
    url = f"sqlite:///{(tmp_path / 'gift-ids.db').as_posix()}"
    monkeypatch.setattr(app.config, "DATABASE_URL", url)
    config = Config(str(BACKEND_DIR / "alembic.ini"))
    command.upgrade(config, PREVIOUS)
    engine = create_engine(url)
    try:
        race_id, pilot_id = _seed(engine)
        before_rows, before_shape = _rows(engine), _shape(engine)
        assert "AUTOINCREMENT" not in _sql(engine).upper()
        command.upgrade(config, REVISION)
        assert "AUTOINCREMENT" in _sql(engine).upper()
        assert _rows(engine) == before_rows
        assert _shape(engine) == before_shape
        with engine.connect() as connection:
            assert list(connection.execute(text("PRAGMA foreign_key_check"))) == []
        with engine.begin() as connection:
            connection.execute(text("DELETE FROM card_gift WHERE id = 41"))
        next_id = _insert(engine, race_id, pilot_id)
        assert next_id > 41
        with engine.begin() as connection:
            connection.execute(text("DELETE FROM card_gift"))
        command.upgrade(config, REVISION)
        after_empty = _insert(engine, race_id, pilot_id)
        assert after_empty > next_id
        preserved = _rows(engine)
        command.downgrade(config, PREVIOUS)
        assert "AUTOINCREMENT" not in _sql(engine).upper()
        assert _rows(engine) == preserved
        assert _shape(engine) == before_shape
        command.upgrade(config, REVISION)
        assert _rows(engine) == preserved
        assert _insert(engine, race_id, pilot_id) > after_empty
    finally:
        engine.dispose()


def test_model_does_not_reuse_id_after_real_gift_undo(make_client, session_factory):
    admin, player, champ, pilot, _ = scenario(make_client, session_factory)
    response = gift(player, champ, pilot)
    assert response.status_code == 201
    first_id = response.json()["id"]
    assert admin.post(f"/api/championships/{champ}/card-gifts/{first_id}/undo").status_code == 204
    with session_factory() as db:
        assert db.scalar(select(CardGift.id)) is None
    response = gift(player, champ, pilot)
    assert response.status_code == 201
    assert response.json()["id"] > first_id
