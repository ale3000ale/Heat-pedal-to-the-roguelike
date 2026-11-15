"""Test predisposti delle transazioni; mai eseguiti dall'assistente in locale."""
import pytest
from sqlalchemy import select

from app.db.models import Deck, DraftPreparation, Race
from app.schemas.draft.draft_snapshot import DraftSnapshot
from app.services.draft.draft_preparation import DraftPreparationError, open_preparation
from app.services.draft.draft_snapshot import DraftSnapshotConflictError
from app.services.draft.draft_transaction import cancel_preparation, draft_mutation
from tests.test_draft_preparation import seed


def test_track_versions_restore_original_and_keep_versions_monotonic(session_factory):
    cid, judge, _, _, _ = seed(session_factory)
    with session_factory() as db:
        row = open_preparation(db, cid, judge)
        key = row.id
        initial = DraftSnapshot.model_validate_json(row.snapshot_json)
        target = initial.decks[0].deck_id
        with draft_mutation(db, key, judge, row.version, creator_only=True) as work:
            work.decks[target].cards = " [] "
        saved = db.get(DraftPreparation, key)
        tracked = DraftSnapshot.model_validate_json(saved.snapshot_json)
        item = next(item for item in tracked.decks if item.deck_id == target)
        assert (item.cards, item.version, item.current_version) == ("[]", 1, 2)
        cancel_preparation(db, key, judge, saved.version)
        assert db.get(DraftPreparation, key) is None
        assert db.get(Deck, target).cards == "[]"
        assert db.get(Deck, target).version == 3
        assert db.scalar(select(Race)) is None


def test_body_error_rolls_back_every_write(session_factory):
    cid, judge, _, _, _ = seed(session_factory)
    with session_factory() as db:
        row = open_preparation(db, cid, judge)
        key, version = row.id, row.version
        target = DraftSnapshot.model_validate_json(row.snapshot_json).decks[0].deck_id
        with pytest.raises(RuntimeError):
            with draft_mutation(db, key, judge, version) as work:
                work.decks[target].cards = " [] "
                raise RuntimeError("Errore simulato")
        assert db.get(Deck, target).cards == "[]"
        assert db.get(DraftPreparation, key).version == version


def test_external_change_is_not_absorbed_or_overwritten(session_factory):
    cid, judge, _, _, _ = seed(session_factory)
    with session_factory() as db:
        row = open_preparation(db, cid, judge)
        key, version = row.id, row.version
        target = DraftSnapshot.model_validate_json(row.snapshot_json).decks[0].deck_id
        db.get(Deck, target).cards = " [] "
        db.commit()
        with pytest.raises(DraftSnapshotConflictError):
            cancel_preparation(db, key, judge, version)
        assert db.get(Deck, target).cards == " [] "
        assert db.get(DraftPreparation, key) is not None


def test_stale_request_does_not_enter_body(session_factory):
    cid, judge, _, _, _ = seed(session_factory)
    with session_factory() as db:
        row = open_preparation(db, cid, judge)
        with pytest.raises(DraftPreparationError):
            with draft_mutation(db, row.id, judge, row.version + 1):
                raise AssertionError("Corpo non autorizzato")
