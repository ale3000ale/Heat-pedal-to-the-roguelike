"""Test predisposti dei controlli puri di blocco; esecuzione affidata alla CI."""
import pytest

from app.db.models import Championship
from app.services.draft_guards import (
    DraftLockedError, has_draft, pilot_has_draft,
    require_no_draft, require_no_pilot_draft,
)
from app.services.draft_preparation import open_preparation
from tests.test_draft_preparation import seed


def test_guards_are_isolated_and_do_not_mutate_or_rollback(session_factory):
    cid, judge, _, _, pid = seed(session_factory)
    with session_factory() as db:
        other = Championship(name="Altro", name_key="altro")
        db.add(other)
        db.commit()
        other_id = other.id
        open_preparation(db, cid, judge)
        assert has_draft(db, cid)
        assert not has_draft(db, other_id)
        assert pilot_has_draft(db, pid)
        require_no_draft(db, other_id)
        before = db.get(Championship, cid).name
        with pytest.raises(DraftLockedError):
            require_no_draft(db, cid)
        with pytest.raises(DraftLockedError):
            require_no_pilot_draft(db, pid)
        assert db.in_transaction()
        assert not db.new and not db.dirty and not db.deleted
        assert db.get(Championship, cid).name == before
