"""Primitive di ripristino sul solo database temporaneo dei test."""
import pytest

from app.db.models import Deck
from app.services.draft_snapshot import (
    DraftSnapshotConflictError, capture_snapshot, stage_snapshot_restore,
)


def seed_decks(factory):
    """Crea due contenitori vuoti di prova e ritorna gli ID."""
    with factory() as db:
        decks = [Deck(cards="[]"), Deck(cards=None)]
        db.add_all(decks)
        db.commit()
        return [deck.id for deck in decks]


def test_capture_preserves_requested_order_and_originals(session_factory):
    ids = seed_decks(session_factory)
    with session_factory() as db:
        snapshot = capture_snapshot(db, ids[::-1])
        assert [item.deck_id for item in snapshot.decks] == ids[::-1]
        assert [item.cards for item in snapshot.decks] == [None, "[]"]
        assert not db.dirty


def test_restore_preserves_monotonic_version_and_is_rollbackable(session_factory):
    ids = seed_decks(session_factory)
    with session_factory() as db:
        snapshot = capture_snapshot(db, ids)
        deck = db.get(Deck, ids[0])
        deck.cards = ' [{"name":"Turbo","path":"cards/t.webp","copies":1}] '
        db.commit()
        changed = deck.cards
        assert deck.version == 2
        stage_snapshot_restore(db, snapshot, {ids[0]: 2, ids[1]: 1})
        db.flush()
        assert deck.cards == "[]"
        assert deck.version == 3
        db.rollback()
        assert db.get(Deck, ids[0]).cards == changed
        assert db.get(Deck, ids[0]).version == 2
        stage_snapshot_restore(db, snapshot, {ids[0]: 2, ids[1]: 1})
        db.commit()
    with session_factory() as db:
        assert db.get(Deck, ids[0]).cards == "[]"
        assert db.get(Deck, ids[0]).version == 3


def test_conflict_checks_every_deck_before_changing_any(session_factory):
    ids = seed_decks(session_factory)
    with session_factory() as db:
        snapshot = capture_snapshot(db, ids)
        first = db.get(Deck, ids[0])
        first.cards = " [] "
        db.commit()
        with pytest.raises(DraftSnapshotConflictError):
            stage_snapshot_restore(db, snapshot, {ids[0]: 2, ids[1]: 999})
        assert first.cards == " [] "
        assert not db.dirty


@pytest.mark.parametrize("ids", [[0], [True], ["1"], [1, 1], [999999]])
def test_capture_rejects_invalid_or_missing_decks(session_factory, ids):
    with session_factory() as db:
        with pytest.raises(DraftSnapshotConflictError):
            capture_snapshot(db, ids)


def test_restore_rejects_incomplete_versions(session_factory):
    ids = seed_decks(session_factory)
    with session_factory() as db:
        snapshot = capture_snapshot(db, ids)
        with pytest.raises(DraftSnapshotConflictError):
            stage_snapshot_restore(db, snapshot, {ids[0]: 1})
        assert not db.dirty


def test_pending_changes_are_not_flushed(session_factory):
    ids = seed_decks(session_factory)
    with session_factory() as db:
        snapshot = capture_snapshot(db, ids)
        pending = Deck(cards="[]")
        db.add(pending)
        with pytest.raises(DraftSnapshotConflictError):
            capture_snapshot(db, ids)
        with pytest.raises(DraftSnapshotConflictError):
            stage_snapshot_restore(db, snapshot, {key: 1 for key in ids})
        assert pending.id is None
        db.rollback()
