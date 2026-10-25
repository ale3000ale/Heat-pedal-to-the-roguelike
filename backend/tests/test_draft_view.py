"""Test predisposti delle letture; nessuna esecuzione locale attestata."""
import pytest
from pydantic import ValidationError

from app.schemas.draft import DraftReadyCommand
from app.services.draft_commands import confirm_attendance
from app.services.draft_preparation import DraftPermissionError, open_preparation
from app.services.draft_view import list_my_drafts, read_draft, read_draft_deck
from tests.test_draft_preparation import seed


def test_initial_modal_is_creator_only(session_factory):
    cid, judge, other, player, _ = seed(session_factory)
    with session_factory() as db:
        row = open_preparation(db, cid, judge)
        assert [d.id for d in list_my_drafts(db, judge)] == [row.id]
        assert list_my_drafts(db, other) == []
        assert list_my_drafts(db, player) == []
        with pytest.raises(DraftPermissionError):
            read_draft(db, row.id, player)


def test_shared_phase_recovers_without_originals_or_owner_ids(session_factory):
    cid, judge, other, player, pid = seed(session_factory)
    with session_factory() as db:
        row = open_preparation(db, cid, judge)
        row = confirm_attendance(db, row.id, judge, row.version)
        views = list_my_drafts(db, player)
        assert len(views) == 1 and views[0].phase == "decks"
        assert views[0].my_pilot_ids == [pid] and not views[0].can_manage
        body = views[0].model_dump()
        assert "snapshot_json" not in body and "state_json" not in body
        assert "user_id" not in body["participants"][0]
        assert list_my_drafts(db, other) == []
        own = read_draft_deck(db, row.id, player, pid)
        assert own.inventory == [] and own.game_deck == []
        with pytest.raises(DraftPermissionError):
            read_draft_deck(db, row.id, judge, pid)


@pytest.mark.parametrize("version", [True, "1", 0])
def test_commands_reject_coercible_versions(version):
    with pytest.raises(ValidationError):
        DraftReadyCommand(version=version, pilot_id=1, ready=True)
