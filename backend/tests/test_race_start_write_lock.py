"""Avvio gara con lock condiviso: solo database SQLite temporaneo dei test."""
import pytest
from sqlalchemy import func, select

from app.db.models import Championship, EventLog, Race
from app.services.championship.championships import ChampionshipClosedError
from app.services.race.races import RaceStartConflictError, create_race
from app.services.core.sqlite_write_lock import SQLiteWriteLockError


def make_championship(factory):
    """Crea un campionato di prova senza iscritti; restituisce il suo ID."""
    with factory() as db:
        row = Championship(name="Lock avvio", name_key="lock avvio")
        db.add(row)
        db.commit()
        return row.id


def assert_no_race_or_event(factory):
    """Verifica che il rifiuto non abbia persistito gare o eventi."""
    with factory() as db:
        assert db.scalar(select(func.count()).select_from(Race)) == 0
        assert db.scalar(select(func.count()).select_from(EventLog)) == 0


def test_start_refreshes_cached_championship(session_factory):
    championship_id = make_championship(session_factory)
    with session_factory() as db:
        cached = db.get(Championship, championship_id)
        assert cached.is_closed is False
        with session_factory() as writer:
            writer.get(Championship, championship_id).is_closed = True
            writer.commit()
        assert cached.is_closed is False
        with pytest.raises(ChampionshipClosedError):
            create_race(db, championship_id)
    assert_no_race_or_event(session_factory)


def test_start_promotes_existing_native_transaction(session_factory):
    championship_id = make_championship(session_factory)
    with session_factory() as db:
        db.connection().exec_driver_sql("BEGIN")
        race = create_race(db, championship_id)
        assert race.number == 1
    with session_factory() as db:
        assert db.scalar(select(func.count()).select_from(Race)) == 1
        assert list(db.scalars(select(EventLog.type))) == ["race.started"]


def test_pending_changes_are_rejected_and_rolled_back(session_factory):
    championship_id = make_championship(session_factory)
    with session_factory() as db:
        db.get(Championship, championship_id).name = "Modifica pendente"
        with pytest.raises(RaceStartConflictError) as error:
            create_race(db, championship_id)
        assert isinstance(error.value.__cause__, SQLiteWriteLockError)
        assert "modifiche pendenti" in str(error.value.__cause__)
    with session_factory() as db:
        assert db.get(Championship, championship_id).name == "Lock avvio"
    assert_no_race_or_event(session_factory)
