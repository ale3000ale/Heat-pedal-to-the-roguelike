"""Persistenza e rollback su SQLite temporaneo della fixture, mai sui dati del gioco."""
from sqlalchemy import delete, inspect, select

from app.db.models import Championship, EventLog


def test_event_log_indexes(session_factory):
    with session_factory() as db:
        indexes = {item["name"] for item in inspect(db.get_bind()).get_indexes("event_log")}
        assert indexes == {
            "ix_event_log_championship_id_id", "ix_event_log_recipient_user_id_id",
            "ix_event_log_created_at",
        }


def test_event_rolls_back_with_action(session_factory):
    with session_factory() as db:
        championship = Championship(name="Rollback", name_key="rollback")
        db.add(championship)
        db.flush()
        db.add(EventLog(type="race.started", championship_id=championship.id, payload="{}"))
        db.flush()
        db.rollback()
        assert db.scalar(select(EventLog)) is None
        assert db.scalar(select(Championship)) is None


def test_ids_are_not_reused_after_cleanup(session_factory):
    with session_factory() as db:
        championship = Championship(name="Events", name_key="events")
        db.add(championship)
        db.flush()
        first = EventLog(type="race.started", championship_id=championship.id, payload="{}")
        db.add(first)
        db.commit()
        first_id = first.id
        championship_id = championship.id
        db.execute(delete(EventLog))
        db.commit()
        second = EventLog(type="standings.changed", championship_id=championship_id, payload="{}")
        db.add(second)
        db.commit()
        assert second.id > first_id
        assert second.created_at is not None


def test_deleting_championship_removes_events(session_factory):
    with session_factory() as db:
        championship = Championship(name="Delete", name_key="delete")
        db.add(championship)
        db.flush()
        db.add(EventLog(type="race.started", championship_id=championship.id, payload="{}"))
        db.commit()
        db.delete(championship)
        db.commit()
        assert db.scalar(select(EventLog)) is None
