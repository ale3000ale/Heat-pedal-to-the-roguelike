"""Test del salvataggio admin: copie, versioni, blocchi e rollback."""
from datetime import datetime, timezone
import pytest
from sqlalchemy import select

from app.db.models import EventLog, User
from app.db.models.championship import Championship
from app.db.models.deck import Deck
from app.db.models.pilot import Pilot
from app.db.models.race import Race
from app.services.cards import CardEntry, dump_cards
from .test_admin_pilot_cards_api import admin_cards, url

NAMES = ("game_deck", "modification_inventory", "sponsor_inventory", "modification_pool", "sponsor_pool")
PATH = "cards/test/admin-turbo.webp"


@pytest.fixture()
def card_setup(client, session_factory, admin_cards):
    with session_factory() as db:
        pilot = db.get(Pilot, admin_cards[1])
        championship = db.get(Championship, admin_cards[2])
        pools = [Deck(cards="[]"), Deck(cards="[]")]
        db.add_all(pools)
        db.flush()
        championship.pool_deck_id, championship.sponsor_pool_deck_id = [pool.id for pool in pools]
        ids = [pilot.game_deck_id, pilot.inventory_deck_id, pilot.sponsor_inventory_deck_id] + [p.id for p in pools]
        for copies, deck_id in enumerate(ids, start=2):
            db.get(Deck, deck_id).cards = dump_cards([CardEntry(name="Turbo", path=PATH, copies=copies)])
        db.commit()
    return admin_cards


def payload(client, setup, source="game_deck"):
    snapshot = client.get(url(setup)).json()
    return {"versions": {
        name: {"id": c["id"], "version": c["version"]} if c["available"] else None
        for name, c in snapshot["containers"].items()
    }, "transfers": [{"source": source, "path": PATH}]}


def state(session_factory):
    with session_factory() as db:
        decks = list(db.execute(select(Deck.id, Deck.cards, Deck.version).order_by(Deck.id)))
        events = list(db.execute(select(EventLog.id, EventLog.type, EventLog.payload).order_by(EventLog.id)))
        return decks, events


@pytest.mark.parametrize("source,target", [
    ("game_deck", "modification_pool"),
    ("modification_inventory", "modification_pool"),
    ("sponsor_inventory", "sponsor_pool"),
    ("modification_pool", "modification_inventory"),
    ("sponsor_pool", "sponsor_inventory"),
])
def test_five_allowed_directions(client, card_setup, source, target):
    before = client.get(url(card_setup)).json()["containers"]
    response = client.put(url(card_setup), json=payload(client, card_setup, source))
    assert response.status_code == 200
    after = response.json()["containers"]
    for name in NAMES:
        expected = before[name]["cards"][0]["copies"] + (1 if name == target else -1 if name == source else 0)
        assert after[name]["cards"][0]["copies"] == expected
        assert after[name]["cards"][0]["path"] == PATH
        assert after[name]["version"] == before[name]["version"] + (name in (source, target))
    assert after["game_deck"]["cards"][0]["copies"] < 15


@pytest.mark.parametrize("name", NAMES)
def test_any_stale_version_rejects_whole_save(client, session_factory, card_setup, name):
    data = payload(client, card_setup)
    with session_factory() as db:
        deck = db.get(Deck, data["versions"][name]["id"])
        deck.cards = dump_cards([CardEntry(name="Turbo", path=PATH, copies=9)])
        db.commit()
    before = state(session_factory)
    assert client.put(url(card_setup), json=data).status_code == 409
    assert state(session_factory) == before


@pytest.mark.parametrize("blocked", ["closed", "race", "review"])
def test_state_is_rechecked_at_save(client, session_factory, card_setup, blocked):
    data = payload(client, card_setup)
    with session_factory() as db:
        if blocked == "closed":
            db.get(Championship, card_setup[2]).is_closed = True
        else:
            db.add(Race(championship_id=card_setup[2], number=1,
                review_started_at=datetime.now(timezone.utc) if blocked == "review" else None))
        db.commit()
    before = state(session_factory)
    assert client.put(url(card_setup), json=data).status_code == 409
    assert state(session_factory) == before


@pytest.mark.parametrize("role", ["player", "judge"])
def test_role_is_rechecked(client, session_factory, card_setup, role):
    data = payload(client, card_setup)
    with session_factory() as db:
        db.get(User, card_setup[0]).role = role
        db.commit()
    before = state(session_factory)
    assert client.put(url(card_setup), json=data).status_code == 403
    assert state(session_factory) == before


def test_anonymous_cannot_save(make_client, client, card_setup):
    data = payload(client, card_setup)
    assert make_client().put(url(card_setup), json=data).status_code == 401


def test_failed_later_move_rolls_back_everything(client, session_factory, card_setup):
    data = payload(client, card_setup)
    data["transfers"].append({"source": "game_deck", "path": "cards/missing.webp"})
    before = state(session_factory)
    assert client.put(url(card_setup), json=data).status_code == 422
    assert state(session_factory) == before


def test_event_failure_rolls_back_cards_and_events(client, session_factory, card_setup, monkeypatch):
    from app.services import admin_pilot_card_save as service
    original = service.append_event
    calls = []
    def fail_second(db, event):
        calls.append(event)
        if len(calls) == 2:
            raise RuntimeError("injected event failure")
        return original(db, event)
    monkeypatch.setattr(service, "append_event", fail_second)
    data = payload(client, card_setup)
    before = state(session_factory)
    with pytest.raises(RuntimeError, match="injected event failure"):
        client.put(url(card_setup), json=data)
    assert state(session_factory) == before


def test_no_net_change_keeps_versions_and_events(client, session_factory, card_setup):
    data = payload(client, card_setup, "modification_inventory")
    data["transfers"].append({"source": "modification_pool", "path": PATH})
    before = state(session_factory)
    assert client.put(url(card_setup), json=data).status_code == 200
    assert state(session_factory) == before


def test_signals_have_no_card_data_or_gift_events(client, session_factory, card_setup):
    assert client.put(url(card_setup), json=payload(client, card_setup)).status_code == 200
    with session_factory() as db:
        events = list(db.scalars(select(EventLog).order_by(EventLog.id)))
        assert len(events) == 2
        assert all(e.type == "cards.changed" and e.payload == "{}" for e in events)
        assert events[0].recipient_user_id is None and events[0].pilot_id is None
        assert events[1].recipient_user_id == card_setup[0] and events[1].pilot_id == card_setup[1]


@pytest.mark.parametrize("field", ["game_deck", "modification_pool"])
def test_missing_version_is_rejected(client, card_setup, field):
    data = payload(client, card_setup)
    del data["versions"][field]
    assert client.put(url(card_setup), json=data).status_code == 422


def test_client_cannot_choose_destination_or_replacement_cards(client, card_setup):
    data = payload(client, card_setup)
    data["transfers"][0]["destination"] = "game_deck"
    assert client.put(url(card_setup), json=data).status_code == 422
    data = payload(client, card_setup)
    data["cards"] = []
    assert client.put(url(card_setup), json=data).status_code == 422


def test_reassigned_pool_with_same_version_is_conflict(client, session_factory, card_setup):
    data = payload(client, card_setup)
    with session_factory() as db:
        replacement = Deck(cards="[]")
        db.add(replacement)
        db.flush()
        db.get(Championship, card_setup[2]).pool_deck_id = replacement.id
        db.commit()
    before = state(session_factory)
    assert client.put(url(card_setup), json=data).status_code == 409
    assert state(session_factory) == before


@pytest.mark.parametrize("pool,source", [
    ("pool_deck_id", "game_deck"), ("sponsor_pool_deck_id", "sponsor_inventory"),
])
def test_absent_pool_never_discards_cards(client, session_factory, card_setup, pool, source):
    with session_factory() as db:
        setattr(db.get(Championship, card_setup[2]), pool, None)
        db.commit()
    data = payload(client, card_setup, source)
    before = state(session_factory)
    assert client.put(url(card_setup), json=data).status_code == 409
    assert state(session_factory) == before


def test_two_concurrent_saves_do_not_overwrite(client, session_factory, card_setup, tmp_path):
    import sqlite3
    from concurrent.futures import ThreadPoolExecutor
    from threading import Barrier
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    from app.schemas.admin_pilot_cards import AdminPilotCardsSave
    from app.services.admin_pilot_card_save import CardAdminConflictError, save_admin_pilot_cards
    data = payload(client, card_setup)
    path = tmp_path / "concurrent-admin.sqlite"
    target = sqlite3.connect(path)
    with session_factory() as db:
        db.connection().connection.driver_connection.backup(target)
    target.close()
    engine = create_engine(f"sqlite:///{path}", connect_args={"check_same_thread": False, "timeout": 5})
    factory = sessionmaker(bind=engine, autoflush=False)
    barrier = Barrier(2, timeout=10)
    def attempt():
        with factory() as db:
            actor = db.get(User, card_setup[0])
            request = AdminPilotCardsSave.model_validate(data)
            barrier.wait()
            try:
                save_admin_pilot_cards(db, actor, card_setup[2], card_setup[1], request)
                return "saved"
            except CardAdminConflictError:
                return "conflict"
    try:
        with ThreadPoolExecutor(max_workers=2) as executor:
            futures = [executor.submit(attempt) for _ in range(2)]
            outcomes = [future.result(timeout=20) for future in futures]
        assert sorted(outcomes) == ["conflict", "saved"]
        with factory() as db:
            from app.services.cards import parse_cards
            game = db.get(Deck, data["versions"]["game_deck"]["id"])
            pool = db.get(Deck, data["versions"]["modification_pool"]["id"])
            assert parse_cards(game.cards)[0].copies == 1
            assert parse_cards(pool.cards)[0].copies == 6
            assert len(list(db.scalars(select(EventLog)))) == 2
    finally:
        engine.dispose()
