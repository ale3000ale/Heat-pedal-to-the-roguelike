"""Vincoli e versioni sul solo SQLite temporaneo delle fixture."""
import pytest
from sqlalchemy import inspect, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import StaleDataError

from app.db.models import Championship, DraftPreparation, Race, User


def seed_preparation(factory):
    """Crea riferimenti e stato minimo di prova; ritorna gli ID persistiti."""
    with factory() as db:
        user = User(username="draft-test", password="fixture-not-a-real-credential", role="judge")
        championship = Championship(name="Draft", name_key="draft")
        db.add_all([user, championship])
        db.flush()
        draft = DraftPreparation(championship_id=championship.id, creator_user_id=user.id,
                                 phase="attendance", state_json="{}", snapshot_json="{}")
        db.add(draft)
        db.commit()
        return draft.id, championship.id, user.id


def test_persistence_does_not_create_race(session_factory):
    draft_id, _, _ = seed_preparation(session_factory)
    with session_factory() as db:
        draft = db.get(DraftPreparation, draft_id)
        assert draft.phase == "attendance"
        assert draft.version == 1
        assert draft.created_at is not None
        assert db.scalar(select(Race)) is None
        assert "ix_draft_preparation_creator_user_id" in {
            item["name"] for item in inspect(db.get_bind()).get_indexes("draft_preparation")
        }


def test_only_one_preparation_per_championship(session_factory):
    _, championship_id, user_id = seed_preparation(session_factory)
    with session_factory() as db:
        db.add(DraftPreparation(championship_id=championship_id, creator_user_id=user_id,
                                phase="decks", state_json="{}", snapshot_json="{}"))
        with pytest.raises(IntegrityError):
            db.commit()
        db.rollback()


@pytest.mark.parametrize("field,value", [("phase", "unknown"), ("version", 0),
                                         ("creator_user_id", 999999),
                                         ("championship_id", 999999)])
def test_database_rejects_invalid_state(session_factory, field, value):
    draft_id, _, _ = seed_preparation(session_factory)
    with session_factory() as db:
        draft = db.get(DraftPreparation, draft_id)
        setattr(draft, field, value)
        with pytest.raises(IntegrityError):
            db.commit()
        db.rollback()


def test_stale_preparation_update_is_rejected(session_factory):
    draft_id, _, _ = seed_preparation(session_factory)
    with session_factory() as first, session_factory() as second:
        a = first.get(DraftPreparation, draft_id)
        b = second.get(DraftPreparation, draft_id)
        a.phase = "order"
        first.commit()
        assert a.version == 2
        b.phase = "decks"
        with pytest.raises(StaleDataError):
            second.commit()
        second.rollback()
    with session_factory() as db:
        assert db.get(DraftPreparation, draft_id).phase == "order"
