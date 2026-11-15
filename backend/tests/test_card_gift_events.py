"""Privacy e rollback degli eventi tasto S; nessun database reale."""
import json

import pytest
from sqlalchemy import func, select

from app.db.models import CardGift, EventLog, Pilot, User
from app.services.cards.card_gift import draw_gift, undo_gift
from app.services.core.event_log import read_events
from app.services.cards.gift_events import record_gift_action as real_record
from tests.test_race_review import scenario, sponsor_inventory, sponsor_pool


def snapshot(factory, champ, pilot):
    with factory() as db:
        event_ids = list(db.scalars(select(EventLog.id).order_by(EventLog.id)))
        gifts = list(db.execute(select(CardGift.id, CardGift.pilot_id, CardGift.card_name).order_by(CardGift.id)))
    return event_ids, gifts, sponsor_inventory(factory, pilot), sponsor_pool(factory, champ)


def give(admin, champ, pilot):
    response = admin.post(f"/api/championships/{champ}/card-gifts", json={"pilot_id": pilot})
    assert response.status_code == 201
    return response.json()["id"]


def test_gift_and_undo_are_private_and_rejected_actions_emit_nothing(make_client, session_factory):
    admin, player, champ, pilot, race = scenario(make_client, session_factory)
    initial_inventory = sponsor_inventory(session_factory, pilot)
    initial_pool = sponsor_pool(session_factory, champ)
    with session_factory() as db:
        owner_id = db.get(Pilot, pilot).user_id
        admin_id = db.scalar(select(User.id).where(User.role == "admin"))
        cursor = db.scalar(select(func.max(EventLog.id))) or 0
    gift_id = give(admin, champ, pilot)
    url = f"/api/championships/{champ}/card-gifts/{gift_id}/undo"
    before = snapshot(session_factory, champ, pilot)
    assert player.post(url).status_code == 403
    assert snapshot(session_factory, champ, pilot) == before
    assert admin.post(url).status_code == 204
    with session_factory() as db:
        own = read_events(db, owner_id, cursor)
        assert [row.type for row in own] == [
            "card.gifted", "cards.changed", "card.gift_undone", "cards.changed",
        ]
        for row in own:
            if row.type != "cards.changed":
                assert row.recipient_user_id == owner_id
                assert json.loads(row.payload) == {"race_id": race, "gift_id": gift_id}
        public = read_events(db, admin_id, cursor)
        assert [row.type for row in public] == ["cards.changed", "cards.changed"]
        assert all(json.loads(row.payload) == {"race_id": race, "pilot_id": pilot} for row in public)
        assert db.get(CardGift, gift_id) is None
    assert sponsor_inventory(session_factory, pilot) == initial_inventory
    assert sponsor_pool(session_factory, champ) == initial_pool
    before = snapshot(session_factory, champ, pilot)
    assert admin.post(url).status_code == 404
    assert snapshot(session_factory, champ, pilot) == before


@pytest.mark.parametrize("operation", ["gift", "undo"])
def test_gift_event_failure_rolls_back_everything(make_client, session_factory, monkeypatch, operation):
    admin, _, champ, pilot, _ = scenario(make_client, session_factory)
    gift_id = give(admin, champ, pilot) if operation == "undo" else None
    before = snapshot(session_factory, champ, pilot)

    def fail_after_flush(db, race, pilot, gift, action):
        real_record(db, race, pilot, gift, action)
        db.flush()
        raise RuntimeError("event failure")

    monkeypatch.setattr("app.services.cards.card_gift.record_gift_action", fail_after_flush)
    with session_factory() as db:
        admin_user = db.scalar(select(User).where(User.role == "admin"))
        with pytest.raises(RuntimeError, match="event failure"):
            if operation == "gift":
                draw_gift(db, admin_user, champ, pilot)
            else:
                undo_gift(db, admin_user, champ, gift_id)
    assert snapshot(session_factory, champ, pilot) == before
