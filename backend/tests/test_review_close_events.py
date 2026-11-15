"""Eventi atomici della chiusura legacy e della scadenza; SQLite temporaneo."""
import json
from datetime import datetime, timedelta, timezone

import pytest
from sqlalchemy import select

from app.db.models import EventLog, Race, User
from app.services.core.event_log import append_event
from app.schemas.core.events import EventCreate
from app.services.race.race_review import confirm_review, settle_expired_reviews
from tests.test_race_review import CARD, closed_scenario, sponsor_inventory, sponsor_pool


def read_events(factory):
    with factory() as db:
        return [(row.type, json.loads(row.payload)) for row in db.scalars(select(EventLog).order_by(EventLog.id))]


def test_legacy_confirmation_and_repeat(make_client, session_factory):
    _, _, champ, pilot, race = closed_scenario(make_client, session_factory, plays=1)
    before = len(read_events(session_factory))
    with session_factory() as db:
        owner = db.get(User, db.get(Race, race).review_started_by_user_id)
        confirm_review(db, champ, race, owner, True)
    events = read_events(session_factory)[before:]
    assert events == [
        ("race.review_changed", {"race_id": race, "action": "confirmed"}),
        ("cards.changed", {"race_id": race}),
    ]
    assert sponsor_inventory(session_factory, pilot) == {CARD: 2}
    with session_factory() as db:
        assert settle_expired_reviews(db, champ) == 0
    assert len(read_events(session_factory)) == before + 2


@pytest.mark.parametrize("fail", [False, True])
def test_expiry_events_and_atomic_failure(make_client, session_factory, monkeypatch, fail):
    _, _, champ, pilot, race = closed_scenario(make_client, session_factory, plays=1)
    now = datetime.now(timezone.utc)
    with session_factory() as db:
        db.get(Race, race).review_started_at = (now - timedelta(minutes=16)).replace(tzinfo=None)
        db.commit()
    before = len(read_events(session_factory))
    inventory_before = sponsor_inventory(session_factory, pilot)
    pool_before = sponsor_pool(session_factory, champ)
    if fail:
        def failing_record(db, row, action):
            append_event(db, EventCreate(type="race.review_changed", championship_id=champ,
                                        payload={"race_id": row.id, "action": action}))
            db.flush()
            raise RuntimeError("event failure")
        monkeypatch.setattr("app.services.race.race_review.record_review_closed", failing_record)
    with session_factory() as db:
        if fail:
            with pytest.raises(RuntimeError, match="event failure"):
                settle_expired_reviews(db, champ, now)
        else:
            assert settle_expired_reviews(db, champ, now) == 1
            assert settle_expired_reviews(db, champ, now) == 0
    events = read_events(session_factory)[before:]
    if fail:
        assert events == []
        assert sponsor_inventory(session_factory, pilot) == inventory_before
        assert sponsor_pool(session_factory, champ) == pool_before
        with session_factory() as db:
            assert db.get(Race, race).review_closed_at is None
    else:
        assert events == [
            ("race.review_changed", {"race_id": race, "action": "expired"}),
            ("cards.changed", {"race_id": race}),
        ]


def test_abandoned_between_scan_and_lock_is_not_closed(make_client, session_factory, monkeypatch):
    _, _, champ, _, race = closed_scenario(make_client, session_factory)
    now = datetime.now(timezone.utc)
    with session_factory() as db:
        db.get(Race, race).review_started_at = (now - timedelta(minutes=16)).replace(tzinfo=None)
        db.commit()
    from app.services.race.race_review import _lock_database as original_lock

    def abandon_before_lock(db):
        with session_factory() as other:
            other.get(Race, race).review_started_at = None
            other.commit()
        original_lock(db)

    monkeypatch.setattr("app.services.race.race_review._lock_database", abandon_before_lock)
    before = len(read_events(session_factory))
    with session_factory() as db:
        assert settle_expired_reviews(db, champ, now) == 0
    assert len(read_events(session_factory)) == before
    with session_factory() as db:
        assert db.get(Race, race).review_closed_at is None
