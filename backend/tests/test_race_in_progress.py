from app.db.models import User
from app.db.models.deck import DeckPrototype
from app.security import hash_password
from app.services.cards import CardEntry, dump_cards

PASSWORD = "password123"


def setup_world(make_client, session_factory):
    with session_factory() as db:
        db.add(
            DeckPrototype(
                name="default",
                base_cards=dump_cards([CardEntry(name="Turbo", path="cards/base/turbo.webp", copies=1)]),
            )
        )
        db.commit()
    admin = make_client()
    with session_factory() as db:
        db.add(User(username="capo", password=hash_password(PASSWORD), role="admin"))
        db.commit()
    assert (
        admin.post("/api/auth/login", json={"username": "capo", "password": PASSWORD}).status_code
        == 200
    )
    player = make_client()
    assert (
        player.post(
            "/api/auth/register", json={"username": "mario", "password": PASSWORD}
        ).status_code
        == 201
    )
    return admin, player


def new_championship(admin, name):
    r = admin.post("/api/championships", json={"name": name})
    assert r.status_code == 201
    return r.json()["id"]


def enrolled_pilot(player, championship_id, name):
    team_id = player.post("/api/teams", json={"name": f"Team {name}"}).json()["id"]
    pilot_id = player.post("/api/pilots", json={"name": name, "team_id": team_id}).json()["id"]
    r = player.post(f"/api/championships/{championship_id}/pilots", json={"pilot_id": pilot_id})
    assert r.status_code == 201
    return pilot_id


def finish_race(admin, championship_id, race_id, pilot_id):
    r = admin.put(
        f"/api/championships/{championship_id}/races/{race_id}/results",
        json={"results": [{"pilot_id": pilot_id, "sponsor_points": 0}]},
    )
    assert r.status_code == 200


def test_cannot_create_a_race_while_another_is_in_progress(make_client, session_factory):
    admin, _ = setup_world(make_client, session_factory)
    championship_id = new_championship(admin, "Estate")
    assert admin.post(f"/api/championships/{championship_id}/races").status_code == 201
    second = admin.post(f"/api/championships/{championship_id}/races")
    assert second.status_code == 409
    races = admin.get(f"/api/championships/{championship_id}/races").json()
    assert [race["number"] for race in races] == [1]


def test_can_create_a_race_after_the_previous_one_is_finished(make_client, session_factory):
    admin, player = setup_world(make_client, session_factory)
    championship_id = new_championship(admin, "Estate")
    pilot_id = enrolled_pilot(player, championship_id, "Ayrton")
    first = admin.post(f"/api/championships/{championship_id}/races").json()
    finish_race(admin, championship_id, first["id"], pilot_id)
    second = admin.post(f"/api/championships/{championship_id}/races")
    assert second.status_code == 201
    assert second.json()["number"] == 2


def test_a_race_in_progress_does_not_block_other_championships(make_client, session_factory):
    admin, _ = setup_world(make_client, session_factory)
    first = new_championship(admin, "Estate")
    second = new_championship(admin, "Inverno")
    assert admin.post(f"/api/championships/{first}/races").status_code == 201
    assert admin.post(f"/api/championships/{second}/races").status_code == 201


def test_new_race_gets_the_creation_date(make_client, session_factory):
    admin, _ = setup_world(make_client, session_factory)
    championship_id = new_championship(admin, "Estate")
    race = admin.post(f"/api/championships/{championship_id}/races").json()
    assert race["date"] is not None
