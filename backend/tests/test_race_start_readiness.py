"""Vincolo di avvio su SQLite di prova: nessun accesso al database reale."""
import json
import sqlite3

import pytest
from sqlalchemy import func, select
from sqlalchemy.exc import OperationalError

from app.db.models import Deck, EventLog, Pilot, Race
from app.services.cards.cards import STARTER_INVENTORY
from app.services.core.event_log import append_event as real_append_event
from app.services.race.race_deck_readiness import GameDecksNotReadyError
from app.services.race.races import create_race
from tests.race_fixtures import seed_game_deck_from_inventory_card
from tests.test_races_api import make_judge, setup


def snapshot(factory):
    """Legge carte/versioni e conteggi per provare l'assenza di scritture."""
    with factory() as db:
        return (
            list(db.execute(select(Deck.id, Deck.cards, Deck.version).order_by(Deck.id))),
            db.scalar(select(func.count()).select_from(Race)),
            db.scalar(select(func.count()).select_from(EventLog)),
        )


def seed(factory, pilot_id, copies):
    seed_game_deck_from_inventory_card(
        factory, pilot_id, path=STARTER_INVENTORY[0].path, copies=copies
    )


@pytest.mark.parametrize("count", [None, 14, 16])
def test_http_rejection_lists_all_unready_and_writes_nothing(make_client, session_factory, count):
    admin, _, cid, pilots = setup(
        make_client, session_factory, ["Anna", "Beppe", "Carlo"], game_deck_copies=None
    )
    if count is not None:
        seed(session_factory, pilots["Anna"], count)
    seed(session_factory, pilots["Beppe"], 14)
    seed(session_factory, pilots["Carlo"], 15)
    before = snapshot(session_factory)
    response = admin.post(f"/api/championships/{cid}/races")
    assert response.status_code == 409
    detail = response.json()["detail"]
    assert f"Anna: {count or 0}/15" in detail
    assert "Beppe: 14/15" in detail and "Carlo" not in detail
    assert "cards/" not in detail
    assert snapshot(session_factory) == before


@pytest.mark.parametrize("role", ["admin", "judge"])
def test_ready_start_creates_one_event_and_keeps_decks(make_client, session_factory, role):
    admin, _, cid, _ = setup(make_client, session_factory, ["Anna", "Beppe"])
    manager = admin if role == "admin" else make_judge(make_client, session_factory)
    before = snapshot(session_factory)
    response = manager.post(f"/api/championships/{cid}/races")
    assert response.status_code == 201
    after = snapshot(session_factory)
    assert after[0] == before[0] and after[1] == before[1] + 1
    with session_factory() as db:
        events = list(db.scalars(select(EventLog).where(EventLog.type == "race.started")))
        assert len(events) == 1
        assert json.loads(events[0].payload) == {"race_id": response.json()["id"]}


def test_service_also_rejects_without_http(make_client, session_factory):
    _, _, cid, pilots = setup(make_client, session_factory, ["Anna"], game_deck_copies=14)
    before = snapshot(session_factory)
    with session_factory() as db:
        with pytest.raises(GameDecksNotReadyError) as error:
            create_race(db, cid)
        assert [(row.pilot_id, row.count) for row in error.value.unready] == [(pilots["Anna"], 14)]
    assert snapshot(session_factory) == before


def test_corrupt_game_deck_blocks_start_without_exposing_cards(make_client, session_factory):
    admin, _, cid, pilots = setup(make_client, session_factory, ["Anna"])
    with session_factory() as db:
        db.get(Deck, db.get(Pilot, pilots["Anna"]).game_deck_id).cards = "not json"
        db.commit()
    before = snapshot(session_factory)
    response = admin.post(f"/api/championships/{cid}/races")
    assert response.status_code == 409
    assert "Anna: mazzo non valido" in response.json()["detail"]
    assert "not json" not in response.json()["detail"]
    assert snapshot(session_factory) == before


def test_unenrolled_empty_deck_does_not_block_start(make_client, session_factory):
    admin, player, cid, _ = setup(make_client, session_factory, ["Anna"])
    outsider = player.post("/api/pilots", json={"name": "Fuori campionato"})
    assert outsider.status_code == 201
    assert outsider.json()["game_deck"] == []
    assert admin.post(f"/api/championships/{cid}/races").status_code == 201


def test_event_failure_rolls_back_ready_start(make_client, session_factory, monkeypatch):
    _, _, cid, _ = setup(make_client, session_factory, ["Anna"])
    before = snapshot(session_factory)

    def fail_event(db, data):
        real_append_event(db, data)
        db.flush()
        raise RuntimeError("event failure")

    monkeypatch.setattr("app.services.race.races.append_event", fail_event)
    with session_factory() as db:
        with pytest.raises(RuntimeError, match="event failure"):
            create_race(db, cid)
    assert snapshot(session_factory) == before


def test_busy_lock_is_http_conflict_without_writes(make_client, session_factory, monkeypatch):
    admin, _, cid, _ = setup(make_client, session_factory, ["Anna"])
    before = snapshot(session_factory)

    def busy(db):
        original = sqlite3.OperationalError("database is locked")
        original.sqlite_errorcode = sqlite3.SQLITE_BUSY
        raise OperationalError("BEGIN IMMEDIATE", {}, original)

    monkeypatch.setattr("app.services.core.sqlite_write_lock.acquire_sqlite_write_lock", busy)
    response = admin.post(f"/api/championships/{cid}/races")
    assert response.status_code == 409
    assert snapshot(session_factory) == before
