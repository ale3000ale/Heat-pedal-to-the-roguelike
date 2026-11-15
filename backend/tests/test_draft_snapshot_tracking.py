"""Test aggiuntivi predisposti per le versioni tracciate; non eseguiti localmente."""
import pytest
from pydantic import ValidationError

from app.schemas.draft_snapshot import DraftDeckSnapshot, DraftSnapshot


def test_initial_snapshot_without_current_version_remains_readable():
    raw = '{"format_version":1,"decks":[{"deck_id":1,"version":3,"cards":"[]"}]}'
    snapshot = DraftSnapshot.model_validate_json(raw)
    assert snapshot.decks[0].current_version is None
    assert snapshot.decks[0].version == 3


def test_tracking_preserves_original_content_and_version():
    snapshot = DraftSnapshot(format_version=1, decks=[
        DraftDeckSnapshot(deck_id=1, version=3, cards=" [] ", current_version=5),
    ])
    restored = DraftSnapshot.model_validate_json(snapshot.model_dump_json())
    item = restored.decks[0]
    assert (item.version, item.current_version, item.cards) == (3, 5, " [] ")


@pytest.mark.parametrize("current", [0, -1, True, "5", 2])
def test_invalid_or_regressing_current_version_is_rejected(current):
    with pytest.raises(ValidationError):
        DraftDeckSnapshot(deck_id=1, version=3, cards="[]", current_version=current)


def test_same_version_is_valid_before_any_card_write():
    item = DraftDeckSnapshot(deck_id=1, version=3, cards=None, current_version=3)
    assert item.cards is None
