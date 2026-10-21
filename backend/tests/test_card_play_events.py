"""Privacy e atomicita' degli eventi di giocata/annullo, con SQLite temporaneo."""
import json

import pytest
from sqlalchemy import func, select

from app.db.models import CardPlay, EventLog, Pilot, User
from app.services.card_events import record_card_action as real_record
from app.services.card_play import play_card, undo_last_play
from app.services.event_log import read_events
from tests.test_race_review import CARD, play, scenario, undo


def snapshot(factory):
    with factory() as db:
        events = list(db.scalars(select(EventLog.id).order_by(EventLog.id)))
        plays = list(db.execute(select(CardPlay.id, CardPlay.status).order_by(CardPlay.id)).tuples())
        return events, plays


def test_play_and_undo_notify_owner_without_leaking_details(make_client, session_factory):
    _, player, champ, pilot, race = scenario(make_client, session_factory, copies=2)
    with session_factory() as db:
        owner_id = db.get(Pilot, pilot).user_id
        admin_id = db.scalar(select(User.id).where(User.role == "admin"))
        cursor = db.scalar(select(func.max(EventLog.id))) or 0
    assert play(player, champ, pilot).status_code == 201
    assert undo(player, champ, pilot).status_code == 200
    with session_factory() as db:
        own = read_events(db, owner_id, cursor)
        assert [row.type for row in own] == [
            "card.played", "cards.changed", "card.play_undone", "cards.changed",
        ]
        public = read_events(db, admin_id, cursor)
        assert [row.type for row in public] == ["cards.changed", "cards.changed"]
        for row in public:
            assert json.loads(row.payload) == {"race_id": race, "pilot_id": pilot}
            assert row.recipient_user_id is None
        private = [row for row in own if row.type != "cards.changed"]
        assert all(row.recipient_user_id == owner_id for row in private)
        assert all(set(json.loads(row.payload)) == {"race_id", "play_id"} for row in private)
    before = snapshot(session_factory)
    assert undo(player, champ, pilot).status_code == 409
    assert snapshot(session_factory) == before


@pytest.mark.parametrize("operation", ["play", "undo"])
def test_event_failure_rolls_back_play_or_undo(make_client, session_factory, monkeypatch, operation):
    _, player, champ, pilot, _ = scenario(make_client, session_factory, copies=2)
    if operation == "undo":
        assert play(player, champ, pilot).status_code == 201
    before = snapshot(session_factory)

    def fail_after_flush(db, race, pilot, action, play_id):
        real_record(db, race, pilot, action, play_id)
        db.flush()
        raise RuntimeError("event failure")

    monkeypatch.setattr("app.services.card_play.record_card_action", fail_after_flush)
    with session_factory() as db:
        owner_id = db.get(Pilot, pilot).user_id
        owner = db.get(User, owner_id)
        with pytest.raises(RuntimeError, match="event failure"):
            if operation == "play":
                play_card(db, owner, champ, pilot, CARD)
            else:
                undo_last_play(db, owner, champ, pilot)
    assert snapshot(session_factory) == before
