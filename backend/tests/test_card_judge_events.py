"""Eventi del revisore: privacy, rifiuti e atomicita' su database sintetici."""
import json

import pytest
from sqlalchemy import func, select

from app.db.models import CardGift, CardPlay, Deck, EventLog, Pilot, User
from app.services.cards.card_judge import cancel_play, grant_bonus, remove_card
from app.services.core.event_log import read_events
from tests.test_card_judge import (
    CARD, bonus, cancel, confirm_review, leave_review, other_judge, play,
    removal, reviewing, scenario, sponsor_inventory, sponsor_pool, summary,
)
from tests.test_race_review_reopen import reopen_review


def prepared(make_client, factory, consumed=False):
    """Crea una giocata e la revisione; opzionalmente consuma e riapre."""
    admin, player, champ, pilot, race = scenario(make_client, factory)
    assert play(player, champ, pilot).status_code == 201
    response = summary(admin, champ, race)
    assert response.status_code == 200
    play_id = response.json()[0]["plays"][0]["id"]
    reviewing(admin, champ, race, pilot)
    if consumed:
        assert confirm_review(admin, champ, race).status_code == 200
        assert reopen_review(admin, champ, race).status_code == 200
    return admin, player, champ, pilot, race, play_id


def cursor(factory):
    with factory() as db:
        return db.scalar(select(func.max(EventLog.id))) or 0


def snapshot(factory):
    """Fotografa mazzi/versioni, giocate, notifiche ed eventi per il rollback."""
    statements = (
        select(Deck.id, Deck.cards, Deck.version).order_by(Deck.id),
        select(CardPlay.id, CardPlay.status).order_by(CardPlay.id),
        select(CardGift.id, CardGift.seen_at).order_by(CardGift.id),
        select(EventLog.id, EventLog.type, EventLog.payload,
               EventLog.recipient_user_id).order_by(EventLog.id),
    )
    with factory() as db:
        return tuple([tuple(row) for row in db.execute(stmt)] for stmt in statements)


def invoke(client, action, champ, pilot, race, play_id):
    if action == "cancel":
        return cancel(client, champ, race, play_id)
    if action == "bonus":
        return bonus(client, champ, race, pilot)
    return removal(client, champ, race, pilot)


@pytest.mark.parametrize("consumed", [False, True])
def test_cancel_private_event_and_public_invalidation(make_client, session_factory, consumed):
    admin, _, champ, pilot, race, play_id = prepared(make_client, session_factory, consumed)
    judge = other_judge(make_client, session_factory)
    assert judge is not None
    after = cursor(session_factory)
    assert cancel(admin, champ, race, play_id).status_code == 200
    with session_factory() as db:
        owner_id = db.get(Pilot, pilot).user_id
        own = read_events(db, owner_id, after)
        assert [row.type for row in own] == ["card.play_undone", "cards.changed"]
        assert own[0].recipient_user_id == owner_id
        assert json.loads(own[0].payload) == {"race_id": race, "play_id": play_id}
        assert own[1].recipient_user_id is None
        for user_id in db.scalars(select(User.id).where(User.role.in_(["admin", "judge"]))):
            public = read_events(db, user_id, after)
            assert [row.type for row in public] == ["cards.changed"]
            assert json.loads(public[0].payload) == {"race_id": race, "pilot_id": pilot}
        assert db.get(CardPlay, play_id).status == "annullata"
    assert sponsor_inventory(session_factory, pilot) == {CARD: 2}
    assert sponsor_pool(session_factory, champ) == {CARD: 2}


@pytest.mark.parametrize("action,delta,status", [("bonus", 1, 201), ("removal", -1, 200)])
def test_inventory_correction_emits_only_public_event_without_gift(
    make_client, session_factory, action, delta, status
):
    admin, player, champ, pilot, race, play_id = prepared(make_client, session_factory)
    outsider = make_client()
    response = outsider.post("/api/auth/register", json={"username": "esterno", "password": "password123"})
    assert response.status_code == 201
    after = cursor(session_factory)
    assert invoke(admin, action, champ, pilot, race, play_id).status_code == status
    with session_factory() as db:
        rows = list(db.scalars(select(EventLog).where(EventLog.id > after).order_by(EventLog.id)))
        assert [row.type for row in rows] == ["cards.changed"]
        assert rows[0].recipient_user_id is None
        assert json.loads(rows[0].payload) == {"race_id": race, "pilot_id": pilot}
        owner_id = db.get(Pilot, pilot).user_id
        assert [row.id for row in read_events(db, owner_id, after)] == [rows[0].id]
        outsider_id = db.scalar(select(User.id).where(User.username == "esterno"))
        assert read_events(db, outsider_id, after) == []
        assert db.scalar(select(func.count()).select_from(CardGift)) == 0
    assert sponsor_inventory(session_factory, pilot) == {CARD: 2 + delta}
    assert sponsor_pool(session_factory, champ) == {CARD: 2 - delta}
    response = player.get(f"/api/championships/{champ}/card-gifts", params={"pilot_id": pilot})
    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.parametrize("action", ["cancel", "bonus", "removal"])
@pytest.mark.parametrize("reason", ["player", "other", "inactive"])
def test_rejected_corrections_change_neither_state_nor_events(
    make_client, session_factory, action, reason
):
    admin, player, champ, pilot, race, play_id = prepared(make_client, session_factory)
    actor, status = admin, 409
    if reason == "player":
        actor, status = player, 403
    elif reason == "other":
        actor = other_judge(make_client, session_factory)
    else:
        assert leave_review(admin, champ, race).status_code == 200
    before = snapshot(session_factory)
    assert invoke(actor, action, champ, pilot, race, play_id).status_code == status
    assert snapshot(session_factory) == before


@pytest.mark.parametrize("action", ["cancel", "bonus", "removal"])
def test_invalid_card_or_repeated_cancel_emits_nothing(make_client, session_factory, action):
    admin, _, champ, pilot, race, play_id = prepared(make_client, session_factory)
    if action == "cancel":
        assert cancel(admin, champ, race, play_id).status_code == 200
    before = snapshot(session_factory)
    if action == "cancel":
        response = cancel(admin, champ, race, play_id)
    elif action == "bonus":
        response = bonus(admin, champ, race, pilot, "Inesistente")
    else:
        response = removal(admin, champ, race, pilot, "Inesistente")
    assert response.status_code == 409
    assert snapshot(session_factory) == before


@pytest.mark.parametrize("action", ["cancel", "consumed", "bonus", "removal"])
def test_event_failure_after_flush_rolls_back_correction(
    make_client, session_factory, monkeypatch, action
):
    from app.services.cards import card_judge

    _, _, champ, pilot, race, play_id = prepared(make_client, session_factory, action == "consumed")
    target = "record_card_action" if action in ("cancel", "consumed") else "record_inventory_correction"
    original = getattr(card_judge, target)

    def fail_after_flush(db, *args):
        original(db, *args)
        db.flush()
        raise RuntimeError("event failure")

    monkeypatch.setattr(card_judge, target, fail_after_flush)
    before = snapshot(session_factory)
    with session_factory() as db:
        reviewer = db.scalar(select(User).where(User.role == "admin"))
        with pytest.raises(RuntimeError, match="event failure"):
            if action in ("cancel", "consumed"):
                cancel_play(db, champ, race, play_id, reviewer)
            elif action == "bonus":
                grant_bonus(db, champ, race, pilot, CARD, reviewer)
            else:
                remove_card(db, champ, race, pilot, CARD, reviewer)
    assert snapshot(session_factory) == before
