from .test_race_in_progress import (
    confirm_review,
    enrolled_pilot,
    finish_race,
    new_championship,
    setup_world,
)


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
    start_race(admin, championship_id)
    before = detail(player, pilot_id)
    assert before["deck_locked"] is True
    r = move(player, pilot_id, "add", path)
    assert r.status_code == 409
    after = detail(player, pilot_id)
    assert after["game_deck"] == before["game_deck"]
    assert after["inventory"] == before["inventory"]


def test_remove_is_locked_too(make_client, session_factory):
    admin, player = setup_world(make_client, session_factory)
    championship_id = new_championship(admin, "Estate")
    pilot_id = enrolled_pilot(player, championship_id, "Ayrton")
    path = first_path(player, pilot_id)
    assert move(player, pilot_id, "add", path).status_code == 200
    start_race(admin, championship_id)
    assert move(player, pilot_id, "remove", path).status_code == 409
    assert len(detail(player, pilot_id)["game_deck"]) == 1


def test_deck_stays_locked_until_the_review_is_confirmed(make_client, session_factory):
    admin, player = setup_world(make_client, session_factory)
    championship_id = new_championship(admin, "Estate")
    pilot_id = enrolled_pilot(player, championship_id, "Ayrton")
    path = first_path(player, pilot_id)
    race = start_race(admin, championship_id)
    finish_race(admin, championship_id, race["id"], pilot_id)
    assert detail(player, pilot_id)["deck_locked"] is True
    assert move(player, pilot_id, "add", path).status_code == 409
    confirm_review(admin, championship_id, race["id"])
    assert detail(player, pilot_id)["deck_locked"] is False
    assert move(player, pilot_id, "add", path).status_code == 200


def test_a_race_in_another_championship_does_not_lock_the_deck(make_client, session_factory):
    admin, player = setup_world(make_client, session_factory)
    first = new_championship(admin, "Estate")
    second = new_championship(admin, "Inverno")
    pilot_id = enrolled_pilot(player, first, "Ayrton")
    path = first_path(player, pilot_id)
    start_race(admin, second)
    assert detail(player, pilot_id)["deck_locked"] is False
    assert move(player, pilot_id, "add", path).status_code == 200
