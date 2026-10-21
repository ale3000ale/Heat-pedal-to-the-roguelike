"""Test del modulo timer non ancora avviato dal lifespan."""
import asyncio
from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock

import pytest
from sqlalchemy import select

from app.db.models import EventLog, Race
from app.services.review_timer import review_timer, run_review_sweep
from tests.test_race_review import CARD, closed_scenario, sponsor_inventory, sponsor_pool


def test_sweep_expires_once_without_an_http_request(make_client, session_factory):
    _, _, championship_id, pilot_id, race_id = closed_scenario(
        make_client, session_factory, copies=3, pool_copies=1, plays=2
    )
    now = datetime.now(timezone.utc)
    with session_factory() as db:
        race = db.get(Race, race_id)
        race.review_started_at = (now - timedelta(minutes=16)).replace(tzinfo=None)
        db.commit()
    assert run_review_sweep(session_factory, now) == 1
    assert run_review_sweep(session_factory, now) == 0
    assert sponsor_inventory(session_factory, pilot_id) == {CARD: 1}
    assert sponsor_pool(session_factory, championship_id) == {CARD: 3}
    with session_factory() as db:
        assert db.get(Race, race_id).review_closed_at is not None


def test_sweep_keeps_live_review_and_purges_old_events(make_client, session_factory):
    _, _, championship_id, _, race_id = closed_scenario(make_client, session_factory)
    now = datetime.now(timezone.utc)
    with session_factory() as db:
        recent_ids = list(db.scalars(select(EventLog.id)))
        expired = EventLog(type="race.started", championship_id=championship_id, payload="{}",
                           created_at=(now - timedelta(hours=25)).replace(tzinfo=None))
        db.add(expired)
        db.commit()
        expired_id = expired.id
    assert run_review_sweep(session_factory, now, cleanup=True) == 0
    with session_factory() as db:
        assert db.get(Race, race_id).review_closed_at is None
        assert db.get(EventLog, expired_id) is None
        assert list(db.scalars(select(EventLog.id).order_by(EventLog.id))) == sorted(recent_ids)


def test_timer_stop_after_one_sweep(monkeypatch):
    async def exercise():
        stop = asyncio.Event()

        async def run_and_stop(*args):
            stop.set()
            return 0

        worker = AsyncMock(side_effect=run_and_stop)
        monkeypatch.setattr("app.services.review_timer.run_in_threadpool", worker)
        await review_timer(object(), stop)
        assert worker.await_count == 1

    asyncio.run(exercise())


def test_timer_already_stopped_does_not_touch_database(monkeypatch):
    async def exercise():
        stop = asyncio.Event()
        stop.set()
        worker = AsyncMock()
        monkeypatch.setattr("app.services.review_timer.run_in_threadpool", worker)
        await review_timer(object(), stop)
        assert worker.await_count == 0

    asyncio.run(exercise())


@pytest.mark.parametrize("interval", [0, -1, float("inf"), float("nan")])
def test_timer_rejects_invalid_interval(interval):
    async def exercise():
        with pytest.raises(ValueError):
            await review_timer(object(), asyncio.Event(), interval=interval)
    asyncio.run(exercise())
