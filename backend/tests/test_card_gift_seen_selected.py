"""Conferme selettive su fixture sintetiche: sicurezza, idempotenza e rollback."""
import pytest
from sqlalchemy import event, select

from app.db.models import CardGift, Deck, EventLog, Pilot, User
from app.schemas.cards.card_gift_seen import GiftSeenSelection
from app.services.cards.card_gift_seen import mark_selected_gifts_seen
from app.services.cards.cards import STARTER_INVENTORY
from tests.race_fixtures import seed_game_deck_from_inventory_card
from tests.test_card_gifts import (
    enrolled_pilot, gift, give_sponsor_pool, login_judge, register_player,
    scenario, start_race, unseen,
)


def selected(client, champ, pilot, ids):
    return client.post(
        f"/api/championships/{champ}/card-gifts/seen-selected",
        json={"pilot_id": pilot, "gift_ids": ids},
    )


def give(client, champ, pilot):
    response = gift(client, champ, pilot)
    assert response.status_code == 201
    return response.json()["id"]


def snapshot(factory):
    with factory() as db:
        statements = (
            select(CardGift.id, CardGift.seen_at).order_by(CardGift.id),
            select(Deck.id, Deck.cards, Deck.version).order_by(Deck.id),
            select(EventLog.id, EventLog.payload).order_by(EventLog.id),
        )
        return tuple([tuple(row) for row in db.execute(stmt)] for stmt in statements)


def test_selected_does_not_consume_new_gifts_and_is_idempotent(make_client, session_factory):
    _, player, champ, pilot, _ = scenario(make_client, session_factory)
    first = give(player, champ, pilot)
    assert [row["id"] for row in unseen(player, champ, pilot).json()] == [first]
    second = give(player, champ, pilot)
    before = snapshot(session_factory)
    response = selected(player, champ, pilot, [first, first, 999999])
    assert response.status_code == 204
    assert response.content == b""
    assert [row["id"] for row in unseen(player, champ, pilot).json()] == [second]
    after = snapshot(session_factory)
    assert after[1:] == before[1:]
    assert selected(player, champ, pilot, [first]).status_code == 204
    assert snapshot(session_factory) == after


def test_delayed_ack_after_undo_does_not_mark_new_gift(make_client, session_factory):
    admin, player, champ, pilot, _ = scenario(make_client, session_factory)
    first = give(player, champ, pilot)
    assert admin.post(f"/api/championships/{champ}/card-gifts/{first}/undo").status_code == 204
    second = give(player, champ, pilot)
    assert second > first
    before = snapshot(session_factory)
    assert selected(player, champ, pilot, [first]).status_code == 204
    assert snapshot(session_factory) == before
    assert [row["id"] for row in unseen(player, champ, pilot).json()] == [second]


def test_ids_outside_pilot_or_championship_are_ignored(make_client, session_factory):
    admin, player, champ, pilot, _ = scenario(make_client, session_factory)
    own = give(player, champ, pilot)
    second_pilot = enrolled_pilot(player, champ, "Prost")
    other_pilot_gift = give(player, champ, second_pilot)
    response = admin.post("/api/championships", json={"name": "Inverno"})
    assert response.status_code == 201
    other_champ = response.json()["id"]
    third_pilot = enrolled_pilot(player, other_champ, "Lauda")
    give_sponsor_pool(session_factory, other_champ, 1)
    seed_game_deck_from_inventory_card(
        session_factory, third_pilot, path=STARTER_INVENTORY[0].path, copies=15
    )
    start_race(admin, other_champ)
    other_champ_gift = give(player, other_champ, third_pilot)
    assert selected(player, champ, pilot, [own, other_pilot_gift, other_champ_gift]).status_code == 204
    assert [row["id"] for row in unseen(player, champ, second_pilot).json()] == [other_pilot_gift]
    assert [row["id"] for row in unseen(player, other_champ, third_pilot).json()] == [other_champ_gift]
    before = snapshot(session_factory)
    assert selected(player, other_champ, pilot, [other_champ_gift]).status_code == 204
    assert snapshot(session_factory) == before


@pytest.mark.parametrize("role", ["admin", "judge", "other", "anonymous"])
def test_cannot_ack_someone_elses_pilot(make_client, session_factory, role):
    admin, player, champ, pilot, _ = scenario(make_client, session_factory)
    gift_id = give(player, champ, pilot)
    if role == "admin":
        actor = admin
    elif role == "judge":
        actor = login_judge(make_client, session_factory)
    elif role == "other":
        actor = register_player(make_client, "altro")
    else:
        actor = make_client()
    before = snapshot(session_factory)
    assert selected(actor, champ, pilot, [gift_id]).status_code == (401 if role == "anonymous" else 404)
    assert snapshot(session_factory) == before


@pytest.mark.parametrize("ids", [[], [True], [0], [-1], [1.5], ["1"], [9223372036854775808], [1] * 101])
def test_invalid_selections_are_rejected(make_client, session_factory, ids):
    _, player, champ, pilot, _ = scenario(make_client, session_factory)
    before = snapshot(session_factory)
    assert selected(player, champ, pilot, ids).status_code == 422
    assert snapshot(session_factory) == before


def test_missing_extra_fields_and_unknown_targets(make_client, session_factory):
    _, player, champ, pilot, _ = scenario(make_client, session_factory)
    url = f"/api/championships/{champ}/card-gifts/seen-selected"
    assert player.post(url, json={"pilot_id": pilot}).status_code == 422
    assert player.post(url, json={"pilot_id": pilot, "gift_ids": [1], "all": True}).status_code == 422
    assert selected(player, 999999, pilot, [1]).status_code == 404
    assert selected(player, champ, 999999, [1]).status_code == 404


def test_failure_after_flush_rolls_back_seen_dates(make_client, session_factory):
    _, player, champ, pilot, _ = scenario(make_client, session_factory)
    first = give(player, champ, pilot)
    before = snapshot(session_factory)

    def fail_after_flush(db, context):
        raise RuntimeError("seen failure")

    with session_factory() as db:
        owner = db.get(User, db.get(Pilot, pilot).user_id)
        event.listen(db, "after_flush", fail_after_flush)
        with pytest.raises(RuntimeError, match="seen failure"):
            mark_selected_gifts_seen(db, owner, champ, GiftSeenSelection(pilot_id=pilot, gift_ids=[first]))
    assert snapshot(session_factory) == before


def test_legacy_seen_endpoint_still_marks_all(make_client, session_factory):
    _, player, champ, pilot, _ = scenario(make_client, session_factory)
    give(player, champ, pilot)
    give(player, champ, pilot)
    response = player.post(f"/api/championships/{champ}/card-gifts/seen", json={"pilot_id": pilot})
    assert response.status_code == 204
    assert unseen(player, champ, pilot).json() == []
