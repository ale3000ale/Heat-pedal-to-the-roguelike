"""Atomicita' tra conferma conteggi e registro SSE su database temporaneo."""
import json

import pytest
from sqlalchemy import func, select

from app.db.models import EventLog, Race
from app.services.event_log import append_event as real_append_event
from app.services.review_commit import ReviewPlanConflict, commit_review_counts
from tests.test_card_judge import CARD, reviewing, scenario, sponsor_inventory, sponsor_pool
from tests.test_review_commit import request, reviewer


def event_count(factory):
    with factory() as db:
        return db.scalar(select(func.count()).select_from(EventLog))


def test_counts_confirmation_records_only_public_invalidations(make_client, session_factory):
    admin, _, champ, pilot, race = scenario(make_client, session_factory, copies=2)
    reviewing(admin, champ, race, pilot)
    before = event_count(session_factory)
    with session_factory() as db:
        commit_review_counts(db, champ, race, reviewer(db, race), request(pilot, 0))
    with session_factory() as db:
        events = list(db.scalars(select(EventLog).order_by(EventLog.id.desc()).limit(2)))
        assert event_count(session_factory) == before + 2
        assert {row.type for row in events} == {"race.review_changed", "cards.changed"}
        for row in events:
            assert row.recipient_user_id is None
            payload = json.loads(row.payload)
            assert payload["race_id"] == race
            assert set(payload) <= {"race_id", "action"}
    assert sponsor_inventory(session_factory, pilot) == {}


def test_conflict_does_not_record_confirmation(make_client, session_factory):
    admin, _, champ, pilot, race = scenario(make_client, session_factory, copies=2)
    reviewing(admin, champ, race, pilot)
    before = event_count(session_factory)
    with session_factory() as db:
        with pytest.raises(ReviewPlanConflict):
            commit_review_counts(db, champ, race, reviewer(db, race), request(pilot, 3))
    assert event_count(session_factory) == before
    assert sponsor_inventory(session_factory, pilot) == {CARD: 2}
    with session_factory() as db:
        row = db.get(Race, race)
        assert row.review_draft is not None
        assert row.review_closed_at is None


def test_event_failure_rolls_back_even_after_flush(make_client, session_factory, monkeypatch):
    admin, _, champ, pilot, race = scenario(make_client, session_factory, copies=2)
    reviewing(admin, champ, race, pilot)
    before = event_count(session_factory)
    original_inventory = sponsor_inventory(session_factory, pilot)
    original_pool = sponsor_pool(session_factory, champ)

    def fail_after_flush(db, data):
        real_append_event(db, data)
        db.flush()
        raise RuntimeError("simulated event failure")

    monkeypatch.setattr("app.services.review_commit.append_event", fail_after_flush)
    with session_factory() as db:
        with pytest.raises(RuntimeError, match="simulated event failure"):
            commit_review_counts(db, champ, race, reviewer(db, race), request(pilot, 0))
    assert event_count(session_factory) == before
    assert sponsor_inventory(session_factory, pilot) == original_inventory
    assert sponsor_pool(session_factory, champ) == original_pool
    with session_factory() as db:
        assert db.get(Race, race).review_closed_at is None
