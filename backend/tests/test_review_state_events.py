"""Eventi di stato delle revisioni, con rollback atomico su SQLite temporaneo."""
import json

import pytest
from sqlalchemy import select

from app.db.models import EventLog, Race, User
from app.schemas.events import EventCreate
from app.services.event_log import append_event as real_append_event
from app.services.race_review import abandon_review, cancel_review, start_review
from tests.test_race_review import (
    closed_scenario, confirm_review, leave_review, open_review, scenario,
)


def review_events(factory):
    with factory() as db:
        rows = db.scalars(select(EventLog).where(EventLog.type == "race.review_changed").order_by(EventLog.id))
        return [json.loads(row.payload) for row in rows]


def test_open_leave_and_open_again_emit_only_state_changes(make_client, session_factory):
    admin, _, champ, _, race = closed_scenario(make_client, session_factory)
    before = len(review_events(session_factory))
    assert open_review(admin, champ, race).status_code == 200
    assert len(review_events(session_factory)) == before
    assert leave_review(admin, champ, race).status_code == 200
    assert open_review(admin, champ, race).status_code == 200
    assert open_review(admin, champ, race).status_code == 200
    assert review_events(session_factory)[before:] == [
        {"race_id": race, "action": "abandoned"},
        {"race_id": race, "action": "opened"},
    ]


def test_reopen_emits_state_event(make_client, session_factory):
    admin, _, champ, _, race = closed_scenario(make_client, session_factory)
    assert confirm_review(admin, champ, race).status_code == 200
    before = len(review_events(session_factory))
    assert admin.post(f"/api/championships/{champ}/races/{race}/review/reopen").status_code == 200
    assert review_events(session_factory)[before:] == [{"race_id": race, "action": "reopened"}]


def test_pre_results_start_and_cancel_are_idempotent(make_client, session_factory):
    _, _, champ, _, race = scenario(make_client, session_factory)
    before = len(review_events(session_factory))
    with session_factory() as db:
        assert start_review(db, champ, race).review_started_at is not None
        start_review(db, champ, race)
        cancel_review(db, champ, race)
        cancel_review(db, champ, race)
    assert review_events(session_factory)[before:] == [
        {"race_id": race, "action": "started"},
        {"race_id": race, "action": "cancelled"},
    ]


def test_state_change_rolls_back_when_event_fails(make_client, session_factory, monkeypatch):
    _, _, champ, _, race = closed_scenario(make_client, session_factory)
    before = len(review_events(session_factory))

    def fail_after_flush(db, row, action):
        real_append_event(db, EventCreate(
            type="race.review_changed", championship_id=champ,
            payload={"race_id": row.id, "action": action},
        ))
        db.flush()
        raise RuntimeError("event failure")

    monkeypatch.setattr("app.services.race_review.record_review_changed", fail_after_flush)
    with session_factory() as db:
        owner = db.get(User, db.get(Race, race).review_started_by_user_id)
        # Il rollback scade gli attributi ORM: conserviamo il valore prima.
        owner_id = owner.id
        with pytest.raises(RuntimeError, match="event failure"):
            abandon_review(db, champ, race, owner)
    assert len(review_events(session_factory)) == before
    with session_factory() as db:
        row = db.get(Race, race)
        assert row.review_started_at is not None
        assert row.review_started_by_user_id == owner_id
