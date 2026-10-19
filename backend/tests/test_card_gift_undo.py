from datetime import timedelta

from app.db.models.card_gift import CardGift
from tests.test_card_gifts import (
    CARD,
    finish_race,
    gift,
    login_judge,
    play,
    scenario,
    sponsor_inventory,
    sponsor_pool,
    unseen,
)


def undo(client, championship_id, gift_id):
    return client.post(f"/api/championships/{championship_id}/card-gifts/{gift_id}/undo")


def given(client, championship_id, pilot_id):
    r = gift(client, championship_id, pilot_id)
    assert r.status_code == 201
    return r.json()["id"]


def age_gift(session_factory, gift_id, seconds):
    with session_factory() as db:
        row = db.get(CardGift, gift_id)
        row.created_at = row.created_at - timedelta(seconds=seconds)
        db.commit()


def test_an_admin_can_undo_a_gift_and_the_card_goes_back_to_the_pool(make_client, session_factory):
    admin, player, champ, pilot, _ = scenario(make_client, session_factory, copies=1, pool_copies=2)
    gift_id = given(admin, champ, pilot)
    assert sponsor_inventory(session_factory, pilot) == {CARD: 2}
    assert sponsor_pool(session_factory, champ) == {CARD: 1}
    assert undo(admin, champ, gift_id).status_code == 204
    assert sponsor_inventory(session_factory, pilot) == {CARD: 1}
    assert sponsor_pool(session_factory, champ) == {CARD: 2}
    assert unseen(player, champ, pilot).json() == []


def test_a_judge_can_undo_a_gift(make_client, session_factory):
    _, _, champ, pilot, _ = scenario(make_client, session_factory, copies=1, pool_copies=2)
    judge = login_judge(make_client, session_factory)
    gift_id = given(judge, champ, pilot)
    assert undo(judge, champ, gift_id).status_code == 204
    assert sponsor_inventory(session_factory, pilot) == {CARD: 1}
    assert sponsor_pool(session_factory, champ) == {CARD: 2}


def test_a_player_cannot_undo_a_gift(make_client, session_factory):
    admin, player, champ, pilot, _ = scenario(make_client, session_factory, copies=1, pool_copies=2)
    gift_id = given(admin, champ, pilot)
    assert undo(player, champ, gift_id).status_code == 403
    assert sponsor_inventory(session_factory, pilot) == {CARD: 2}
    assert sponsor_pool(session_factory, champ) == {CARD: 1}


def test_an_anonymous_user_cannot_undo_a_gift(make_client, session_factory):
    admin, _, champ, pilot, _ = scenario(make_client, session_factory, copies=1, pool_copies=2)
    gift_id = given(admin, champ, pilot)
    assert undo(make_client(), champ, gift_id).status_code == 401


def test_undo_is_refused_after_sixty_seconds(make_client, session_factory):
    admin, _, champ, pilot, _ = scenario(make_client, session_factory, copies=1, pool_copies=2)
    gift_id = given(admin, champ, pilot)
    age_gift(session_factory, gift_id, 61)
    assert undo(admin, champ, gift_id).status_code == 409
    assert sponsor_inventory(session_factory, pilot) == {CARD: 2}
    assert sponsor_pool(session_factory, champ) == {CARD: 1}


def test_undo_is_refused_when_the_card_was_already_played(make_client, session_factory):
    admin, player, champ, pilot, _ = scenario(make_client, session_factory, copies=1, pool_copies=2)
    gift_id = given(admin, champ, pilot)
    assert play(player, champ, pilot).status_code == 201
    assert play(player, champ, pilot).status_code == 201
    assert undo(admin, champ, gift_id).status_code == 409
    assert sponsor_inventory(session_factory, pilot) == {CARD: 2}
    assert sponsor_pool(session_factory, champ) == {CARD: 1}


def test_undo_is_allowed_when_another_copy_is_still_unplayed(make_client, session_factory):
    admin, player, champ, pilot, _ = scenario(make_client, session_factory, copies=1, pool_copies=2)
    gift_id = given(admin, champ, pilot)
    assert play(player, champ, pilot).status_code == 201
    assert undo(admin, champ, gift_id).status_code == 204
    assert sponsor_inventory(session_factory, pilot) == {CARD: 1}
    assert sponsor_pool(session_factory, champ) == {CARD: 2}


def test_undo_of_an_unknown_gift_gives_404(make_client, session_factory):
    admin, _, champ, _, _ = scenario(make_client, session_factory)
    assert undo(admin, champ, 99999).status_code == 404


def test_undo_of_a_gift_from_another_championship_gives_404(make_client, session_factory):
    admin, _, champ, pilot, _ = scenario(make_client, session_factory, copies=1, pool_copies=2)
    gift_id = given(admin, champ, pilot)
    other = admin.post("/api/championships", json={"name": "Inverno"}).json()["id"]
    assert undo(admin, other, gift_id).status_code == 404
    assert sponsor_inventory(session_factory, pilot) == {CARD: 2}


def test_undo_is_refused_when_the_race_is_finished(make_client, session_factory):
    admin, _, champ, pilot, race = scenario(make_client, session_factory, copies=1, pool_copies=2)
    gift_id = given(admin, champ, pilot)
    finish_race(admin, champ, race, pilot)
    assert undo(admin, champ, gift_id).status_code == 409
