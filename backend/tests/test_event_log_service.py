"""Test su SQLite temporaneo; nessun collegamento al database del gioco."""
import json
from datetime import datetime, timedelta

import pytest
from sqlalchemy import select

from app.db.models import Championship, ChampionshipPilot, Deck, EventLog, Pilot, User
from app.schemas.core.events import EventCreate
from app.services.core.event_log import append_event, purge_expired_events, read_events


@pytest.fixture()
def event_db(session_factory):
    with session_factory() as db:
        users = [User(username=name, password="test-only", role=role) for name, role in
                 [("owner", "player"), ("other", "player"), ("admin", "admin"), ("judge", "judge")]]
        championship = Championship(name="Events", name_key="events")
        db.add_all([*users, championship])
        db.flush()
        decks = [Deck(cards="[]") for _ in range(3)]
        db.add_all(decks)
        db.flush()
        pilot = Pilot(name="Pilot", name_key="pilot", user_id=users[0].id,
                      inventory_deck_id=decks[0].id, sponsor_inventory_deck_id=decks[1].id,
                      game_deck_id=decks[2].id)
        db.add(pilot)
        db.flush()
        db.add(ChampionshipPilot(championship_id=championship.id, pilot_id=pilot.id))
        db.commit()
        yield db, users, championship, pilot


def test_private_events_never_reach_other_users_or_admin(event_db):
    db, users, championship, _ = event_db
    row = append_event(db, EventCreate(type="card.gifted", championship_id=championship.id,
                                      recipient_user_id=users[0].id, payload={"gift_id": 7}))
    db.commit()
    assert json.loads(row.payload) == {"gift_id": 7}
    assert [item.id for item in read_events(db, users[0].id, 0)] == [row.id]
    for user in users[1:]:
        assert read_events(db, user.id, 0) == []


def test_public_access_and_revocation(event_db):
    db, users, championship, pilot = event_db
    row = append_event(db, EventCreate(type="standings.changed", championship_id=championship.id))
    db.commit()
    assert read_events(db, users[0].id, 0) == [row]
    assert read_events(db, users[1].id, 0) == []
    assert read_events(db, users[2].id, 0) == [row]
    assert read_events(db, users[3].id, 0) == [row]
    pilot.deleted_at = datetime(2026, 1, 1)
    db.commit()
    assert read_events(db, users[0].id, 0) == []
    assert read_events(db, 99999, 0) == []


def test_cursor_limit_and_rollback(event_db):
    db, users, championship, _ = event_db
    for _ in range(3):
        append_event(db, EventCreate(type="race.started", championship_id=championship.id))
    db.commit()
    rows = read_events(db, users[0].id, 0, 2)
    assert len(rows) == 2
    assert rows[0].id < rows[1].id
    assert len(read_events(db, users[0].id, rows[-1].id)) == 1
    pending = append_event(db, EventCreate(type="cards.changed", championship_id=championship.id))
    db.flush()
    pending_id = pending.id
    db.rollback()
    assert db.get(EventLog, pending_id) is None


def test_purge_boundary_and_rollback(event_db):
    db, _, championship, _ = event_db
    now = datetime(2026, 10, 20, 12)
    for age in (25, 24, 23):
        db.add(EventLog(type="race.started", championship_id=championship.id, payload="{}",
                        created_at=now - timedelta(hours=age)))
    db.commit()
    assert purge_expired_events(db, now) == 1
    assert len(list(db.scalars(select(EventLog)))) == 2
    db.rollback()
    assert len(list(db.scalars(select(EventLog)))) == 3


@pytest.mark.parametrize("after,limit", [(-1, 10), (True, 10), (0, 0), (0, 101), (0, True)])
def test_invalid_cursor_and_limit(event_db, after, limit):
    db, users, _, _ = event_db
    with pytest.raises(ValueError):
        read_events(db, users[0].id, after, limit)
