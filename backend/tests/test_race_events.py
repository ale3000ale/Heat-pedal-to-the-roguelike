"""Eventi di gara e risultati, atomicita' e correzioni su SQLite temporaneo."""
import json

import pytest
from sqlalchemy import select

from app.db.models import Championship, EventLog, Pilot, Race, RaceResult
from app.services.event_log import append_event as real_append
from app.services.races import create_race, set_results
from tests.test_race_review import finish_race, scenario


def events(factory):
    with factory() as db:
        return [(row.type, json.loads(row.payload)) for row in db.scalars(select(EventLog).order_by(EventLog.id))]


def test_creation_finish_and_correction(make_client, session_factory):
    admin, _, champ, pilot, race = scenario(make_client, session_factory)
    assert ("race.started", {"race_id": race}) in events(session_factory)
    before = len(events(session_factory))
    finish_race(admin, champ, race, pilot)
    assert events(session_factory)[before:] == [
        ("race.review_changed", {"race_id": race, "action": "opened"}),
        ("race.results_changed", {"race_id": race}),
        ("standings.changed", {"race_id": race}),
    ]
    with session_factory() as db:
        row = db.get(Race, race)
        owner_id = row.review_started_by_user_id
        started_at = row.review_started_at
        gold = db.get(Pilot, pilot).gold
    before = len(events(session_factory))
    with session_factory() as db:
        set_results(db, champ, race, [(pilot, 2)], can_correct=True, reviewer_id=owner_id)
    assert events(session_factory)[before:] == [
        ("race.results_changed", {"race_id": race}),
        ("standings.changed", {"race_id": race}),
    ]
    with session_factory() as db:
        assert db.get(Pilot, pilot).gold == gold
        assert db.get(Pilot, pilot).sponsor == 2
        row = db.get(Race, race)
        assert row.review_started_at == started_at
        assert row.review_started_by_user_id == owner_id


def fail_event(db, data):
    real_append(db, data)
    db.flush()
    raise RuntimeError("event failure")


def test_result_event_failure_rolls_back_all_changes(make_client, session_factory, monkeypatch):
    _, _, champ, pilot, race = scenario(make_client, session_factory)
    before = len(events(session_factory))
    with session_factory() as db:
        row = db.get(Pilot, pilot)
        balances = (row.gold, row.sponsor, row.point)
    monkeypatch.setattr("app.services.races.append_event", fail_event)
    with session_factory() as db:
        with pytest.raises(RuntimeError, match="event failure"):
            set_results(db, champ, race, [(pilot, 3)])
    assert len(events(session_factory)) == before
    with session_factory() as db:
        row = db.get(Pilot, pilot)
        assert (row.gold, row.sponsor, row.point) == balances
        assert db.scalar(select(RaceResult).where(RaceResult.race_id == race)) is None
        assert db.get(Race, race).review_started_at is None


def test_creation_event_failure_rolls_back_race(session_factory, monkeypatch):
    with session_factory() as db:
        championship = Championship(name="Rollback race", name_key="rollback race")
        db.add(championship)
        db.commit()
        champ = championship.id
    monkeypatch.setattr("app.services.races.append_event", fail_event)
    with session_factory() as db:
        with pytest.raises(RuntimeError, match="event failure"):
            create_race(db, champ)
    with session_factory() as db:
        assert db.scalar(select(Race).where(Race.championship_id == champ)) is None
        assert db.scalar(select(EventLog)) is None
