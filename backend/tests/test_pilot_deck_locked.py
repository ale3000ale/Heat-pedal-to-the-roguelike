from .race_fixtures import seed_game_deck_from_inventory_card
from .test_race_in_progress import (
    confirm_review,
    enrolled_pilot,
    finish_race,
    new_championship,
    setup_world,
)

LOCKED_MESSAGE = "Con una gara in corso il mazzo non si può modificare"
FULL_MESSAGE = "Il mazzo da gioco ha già 15 carte"


def first_path(player, pilot_id):
    # Percorso della prima carta dell'inventario del pilota.
    return player.get(f"/api/pilots/{pilot_id}").json()["inventory"][0]["path"]


def move(player, pilot_id, action, path):
    return player.post(f"/api/pilots/{pilot_id}/deck/{action}", json={"path": path})


def detail(player, pilot_id):
    return player.get(f"/api/pilots/{pilot_id}").json()


def start_race(admin, championship_id):
    r = admin.post(f"/api/championships/{championship_id}/races")
    assert r.status_code == 201
    return r.json()


def test_deck_is_editable_without_a_race(make_client, session_factory):
    admin, player = setup_world(make_client, session_factory)
    championship_id = new_championship(admin, "Estate")
    pilot_id = enrolled_pilot(player, championship_id, "Ayrton")
    path = first_path(player, pilot_id)
    assert detail(player, pilot_id)["deck_locked"] is False
    assert move(player, pilot_id, "add", path).status_code == 200
    assert move(player, pilot_id, "remove", path).status_code == 200


def test_deck_is_locked_while_a_race_is_in_progress(make_client, session_factory):
    admin, player = setup_world(make_client, session_factory)
    championship_id = new_championship(admin, "Estate")
    pilot_id = enrolled_pilot(player, championship_id, "Ayrton")
    path = first_path(player, pilot_id)
    seed_game_deck_from_inventory_card(session_factory, pilot_id, path=path, copies=15)
    start_race(admin, championship_id)
    before = detail(player, pilot_id)
    assert before["deck_locked"] is True
    r = move(player, pilot_id, "add", path)
    assert r.status_code == 409
    assert r.json()["detail"] == LOCKED_MESSAGE
    after = detail(player, pilot_id)
    assert after["game_deck"] == before["game_deck"]
    assert after["inventory"] == before["inventory"]


def test_remove_is_locked_too(make_client, session_factory):
    admin, player = setup_world(make_client, session_factory)
    championship_id = new_championship(admin, "Estate")
    pilot_id = enrolled_pilot(player, championship_id, "Ayrton")
    path = first_path(player, pilot_id)
    seed_game_deck_from_inventory_card(session_factory, pilot_id, path=path, copies=15)
    start_race(admin, championship_id)
    before = detail(player, pilot_id)
    r = move(player, pilot_id, "remove", path)
    assert r.status_code == 409
    assert r.json()["detail"] == LOCKED_MESSAGE
    after = detail(player, pilot_id)
    assert after["game_deck"] == before["game_deck"]
    assert after["inventory"] == before["inventory"]
    assert sum(card["copies"] for card in after["game_deck"]) == 15


def test_deck_stays_locked_until_the_review_is_confirmed(make_client, session_factory):
    admin, player = setup_world(make_client, session_factory)
    championship_id = new_championship(admin, "Estate")
    pilot_id = enrolled_pilot(player, championship_id, "Ayrton")
    path = first_path(player, pilot_id)
    seed_game_deck_from_inventory_card(session_factory, pilot_id, path=path, copies=15)
    race = start_race(admin, championship_id)
    finish_race(admin, championship_id, race["id"], pilot_id)
    assert detail(player, pilot_id)["deck_locked"] is True
    blocked = move(player, pilot_id, "add", path)
    assert blocked.status_code == 409
    assert blocked.json()["detail"] == LOCKED_MESSAGE
    confirm_review(admin, championship_id, race["id"])
    assert detail(player, pilot_id)["deck_locked"] is False
    full = move(player, pilot_id, "add", path)
    assert full.status_code == 409
    assert full.json()["detail"] == FULL_MESSAGE
    assert move(player, pilot_id, "remove", path).status_code == 200
    assert move(player, pilot_id, "add", path).status_code == 200
    assert sum(card["copies"] for card in detail(player, pilot_id)["game_deck"]) == 15


def test_a_race_in_another_championship_does_not_lock_the_deck(make_client, session_factory):
    admin, player = setup_world(make_client, session_factory)
    first = new_championship(admin, "Estate")
    second = new_championship(admin, "Inverno")
    pilot_id = enrolled_pilot(player, first, "Ayrton")
    path = first_path(player, pilot_id)
    start_race(admin, second)
    assert detail(player, pilot_id)["deck_locked"] is False
    assert move(player, pilot_id, "add", path).status_code == 200
