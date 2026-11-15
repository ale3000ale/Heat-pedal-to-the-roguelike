"""Due processi reali sullo stesso SQLite temporaneo, mai sul database del gioco."""
import json
import multiprocessing
import sqlite3
from datetime import datetime, timedelta, timezone

import pytest
from sqlalchemy import create_engine, event, select
from sqlalchemy.orm import sessionmaker

from app.db.models import EventLog, Race
from tests.test_race_review import CARD, closed_scenario, sponsor_inventory, sponsor_pool


def _close_worker(path, championship_id, race_id, owner_id, now_iso, mode, barrier, output):
    """Worker spawn: sincronizza prima del lock e riporta esito o traceback al padre."""
    import traceback
    from app.db.models import User
    import app.services.race.race_review as reviews

    engine = create_engine(f"sqlite:///{path}", connect_args={"timeout": 10})

    @event.listens_for(engine, "connect")
    def enable_fk(connection, _):
        connection.execute("PRAGMA foreign_keys=ON")

    factory = sessionmaker(bind=engine, autoflush=False)
    original_lock = reviews._lock_database

    def synchronized_lock(db):
        # Entrambi hanno gia' letto i candidati (o caricato l'utente manuale).
        # Nessun processo puo' scrivere prima che anche l'altro sia arrivato qui.
        barrier.wait(timeout=20)
        original_lock(db)

    reviews._lock_database = synchronized_lock
    try:
        with factory() as db:
            if mode == "expiry":
                settled = reviews.settle_expired_reviews(db, championship_id, datetime.fromisoformat(now_iso))
            else:
                owner = db.get(User, owner_id)
                try:
                    reviews.confirm_review(db, championship_id, race_id, owner, True)
                    settled = 1
                except reviews.ReviewAlreadyConfirmedError:
                    settled = 0
        output.put(("ok", settled))
    except Exception:
        output.put(("error", traceback.format_exc()))
    finally:
        engine.dispose()


@pytest.mark.parametrize("second_mode", ["expiry", "manual"])
def test_concurrent_closures_consume_and_emit_only_once(
    make_client, session_factory, tmp_path, second_mode
):
    _, _, champ, pilot, race = closed_scenario(
        make_client, session_factory, copies=3, pool_copies=1, plays=1
    )
    now = datetime.now(timezone.utc)
    with session_factory() as db:
        row = db.get(Race, race)
        row.review_started_at = (now - timedelta(minutes=16)).replace(tzinfo=None)
        owner_id = row.review_started_by_user_id
        db.commit()
        previous_ids = list(db.scalars(select(EventLog.id)))
        last_id = max(previous_ids, default=0)
        source_engine = db.get_bind()
    path = (tmp_path / "concurrent-review.db").as_posix()
    raw = source_engine.raw_connection()
    try:
        with sqlite3.connect(path) as destination:
            raw.driver_connection.backup(destination)
    finally:
        raw.close()
    context = multiprocessing.get_context("spawn")
    barrier = context.Barrier(2)
    output = context.Queue()
    processes = [context.Process(target=_close_worker, args=(
        path, champ, race, owner_id, now.isoformat(), mode, barrier, output,
    )) for mode in ("expiry", second_mode)]
    started = []
    try:
        for process in processes:
            process.start()
            started.append(process)
        for process in started:
            process.join(timeout=35)
        assert all(not process.is_alive() for process in started), "Worker non terminati entro il timeout"
        assert [process.exitcode for process in started] == [0, 0]
        results = [output.get(timeout=5) for _ in started]
        assert all(status == "ok" for status, _ in results), results
        assert sorted(value for _, value in results) == [0, 1]
    finally:
        for process in started:
            if process.is_alive():
                process.terminate()
            process.join(timeout=5)
            if process.is_alive():
                process.kill()
                process.join(timeout=5)
            process.close()
        output.close()
        output.join_thread()
    engine = create_engine(f"sqlite:///{path}")
    factory = sessionmaker(bind=engine)
    try:
        assert sponsor_inventory(factory, pilot) == {CARD: 2}
        assert sponsor_pool(factory, champ) == {CARD: 2}
        with factory() as db:
            assert db.get(Race, race).review_closed_at is not None
            rows = list(db.scalars(select(EventLog).where(EventLog.id > last_id).order_by(EventLog.id)))
            assert [row.type for row in rows] == ["race.review_changed", "cards.changed"]
            payload = json.loads(rows[0].payload)
            assert payload["race_id"] == race
            assert payload["action"] in {"expired", "confirmed"}
    finally:
        engine.dispose()
