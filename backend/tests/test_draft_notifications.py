"""Test predisposti dei segnali privati; esecuzione affidata alla CI."""
import json

import pytest
from pydantic import ValidationError
from sqlalchemy import select

from app.db.models import EventLog
from app.schemas.draft.draft_state import DraftState
from app.schemas.core.events import EventCreate
from app.services.draft.draft_notifications import signal_draft_changed
from app.services.draft.draft_preparation import open_preparation
from tests.test_draft_preparation import seed


@pytest.mark.parametrize("changes", [
    {"recipient_user_id": None}, {"pilot_id": 2}, {"payload": {}},
    {"payload": {"preparation_id": True}},
    {"payload": {"preparation_id": 0}},
    {"payload": {"preparation_id": 1, "cards": []}},
])
def test_public_or_sensitive_draft_signal_is_rejected(changes):
    values = dict(type="draft.changed", championship_id=1, recipient_user_id=2,
                  payload={"preparation_id": 3})
    values.update(changes)
    with pytest.raises(ValidationError):
        EventCreate(**values)


def test_signal_recipients_and_payload_without_commit(session_factory):
    cid, judge, _, player, _ = seed(session_factory)
    with session_factory() as db:
        row = open_preparation(db, cid, judge)
        key = row.id
        state = DraftState.model_validate_json(row.state_json)
        before = set(db.scalars(select(EventLog.id)))
        signal_draft_changed(db, row, state)
        db.flush()
        fresh = list(db.scalars(select(EventLog).where(EventLog.id.not_in(before))))
        assert [event.recipient_user_id for event in fresh] == [judge]
        db.rollback()
        assert set(db.scalars(select(EventLog.id))) == before
        state.phase = "decks"
        signal_draft_changed(db, row, state)
        db.flush()
        fresh = list(db.scalars(select(EventLog).where(EventLog.id.not_in(before))))
        assert {event.recipient_user_id for event in fresh} == {judge, player}
        assert len(fresh) == 2
        assert all(json.loads(event.payload) == {"preparation_id": key} for event in fresh)
        db.rollback()
