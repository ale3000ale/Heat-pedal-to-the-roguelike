"""Lifecycle del timer con factory temporanea; nessun accesso al database reale."""
import asyncio
from datetime import datetime, timedelta, timezone
from importlib import import_module
from unittest.mock import AsyncMock

import pytest
from fastapi import FastAPI

from app.db.models import Race
from tests.test_race_review import CARD, closed_scenario, sponsor_inventory

main = import_module("app.main")
timer_module = import_module("app.services.review_timer")


@pytest.mark.parametrize("body_fails", [False, True])
def test_lifespan_starts_and_awaits_timer_on_exit(session_factory, monkeypatch, body_fails):
    monkeypatch.setattr(main, "SessionLocal", session_factory)

    async def exercise():
        started = asyncio.Event()
        stopped = asyncio.Event()

        async def controlled_timer(factory, stop):
            assert factory is session_factory
            started.set()
            await stop.wait()
            stopped.set()

        monkeypatch.setattr(main, "review_timer", controlled_timer)
        app = FastAPI()

        async def enter_and_leave():
            async with main.lifespan(app):
                await asyncio.wait_for(started.wait(), timeout=2)
                assert not app.state.review_timer_task.done()
                if body_fails:
                    raise RuntimeError("body failure")

        if body_fails:
            with pytest.raises(RuntimeError, match="body failure"):
                await enter_and_leave()
        else:
            await enter_and_leave()
        assert stopped.is_set()
        assert app.state.review_timer_stop.is_set()
        assert app.state.review_timer_task.done()
        assert not app.state.review_timer_task.cancelled()

    asyncio.run(exercise())


def test_startup_failure_does_not_launch_timer(session_factory, monkeypatch):
    monkeypatch.setattr(main, "SessionLocal", session_factory)
    worker = AsyncMock()
    monkeypatch.setattr(main, "review_timer", worker)

    def fail_startup(db):
        raise RuntimeError("startup failure")

    monkeypatch.setattr(main, "purge_expired", fail_startup)

    async def exercise():
        app = FastAPI()
        with pytest.raises(RuntimeError, match="startup failure"):
            async with main.lifespan(app):
                pytest.fail("Il lifespan non deve completare lo startup")
        assert worker.call_count == 0
        assert not hasattr(app.state, "review_timer_task")

    asyncio.run(exercise())


def test_lifespan_real_timer_closes_expired_review(make_client, session_factory, monkeypatch):
    _, _, _, pilot, race = closed_scenario(make_client, session_factory, plays=1)
    with session_factory() as db:
        db.get(Race, race).review_started_at = (
            datetime.now(timezone.utc) - timedelta(minutes=16)
        ).replace(tzinfo=None)
        db.commit()
    monkeypatch.setattr(main, "SessionLocal", session_factory)
    original_sweep = timer_module.run_review_sweep

    async def exercise():
        first_sweep = asyncio.Event()
        loop = asyncio.get_running_loop()
        results = []

        def observed_sweep(*args):
            result = original_sweep(*args)
            results.append(result)
            loop.call_soon_threadsafe(first_sweep.set)
            return result

        monkeypatch.setattr(timer_module, "run_review_sweep", observed_sweep)
        app = FastAPI()
        async with main.lifespan(app):
            await asyncio.wait_for(first_sweep.wait(), timeout=10)
        assert results[0] == 1
        assert app.state.review_timer_task.done()

    asyncio.run(exercise())
    with session_factory() as db:
        assert db.get(Race, race).review_closed_at is not None
    assert sponsor_inventory(session_factory, pilot) == {CARD: 2}
