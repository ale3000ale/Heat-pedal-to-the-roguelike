from app.db.models import User
from app.db.models.deck import Deck, DeckPrototype
from app.db.models.pilot import Pilot
from app.security import hash_password
from app.services.cards import STARTER_INVENTORY, CardEntry, dump_cards

PASSWORD = "password123"
BASE_CARDS = [
    CardEntry(name="Velocità 1", path="cards/starter/velocita-1.webp", copies=3),
    CardEntry(name="Turbo", path="cards/base/turbo.webp", copies=1),
]


def setup_world(make_client, session_factory):
    with session_factory() as db:
        db.add(DeckPrototype(name="default", base_cards=dump_cards(BASE_CARDS)))
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


def make_pilot(player, name):
    team_id = player.post("/api/teams", json={"name": f"Team {name}"}).json()["id"]
    r = player.post("/api/pilots", json={"name": name, "team_id": team_id})
    assert r.status_code == 201
    return r.json()["id"]


def make_dirty(session_factory, pilot_id):
    with session_factory() as db:
        pilot = db.get(Pilot, pilot_id)
        pilot.gold, pilot.sponsor, pilot.point = 50, 4, 7
        db.get(Deck, pilot.game_deck_id).cards = dump_cards(BASE_CARDS[:1])
        db.get(Deck, pilot.inventory_deck_id).cards = dump_cards(BASE_CARDS)
        db.commit()


def test_close_resets_only_the_entrants_of_that_championship(make_client, session_factory):
    admin, player = setup_world(make_client, session_factory)
    first = admin.post("/api/championships", json={"name": "Estate"}).json()["id"]
    second = admin.post("/api/championships", json={"name": "Inverno"}).json()["id"]
    inside = make_pilot(player, "Ayrton")
    other = make_pilot(player, "Alain")
    outside = make_pilot(player, "Niki")
    for pilot_id, championship_id in ((inside, first), (other, second)):
        r = player.post(
            f"/api/championships/{championship_id}/pilots", json={"pilot_id": pilot_id}
        )
        assert r.status_code == 201
    for pilot_id in (inside, other, outside):
        make_dirty(session_factory, pilot_id)

    assert admin.post(f"/api/championships/{first}/close").status_code == 200

    reset = player.get(f"/api/pilots/{inside}").json()
    assert (reset["gold"], reset["sponsor"], reset["point"]) == (0, 0, 0)
    assert reset["game_deck"] == []
    assert reset["inventory"] == [card.model_dump() for card in STARTER_INVENTORY]
    for untouched_id in (other, outside):
        untouched = player.get(f"/api/pilots/{untouched_id}").json()
        assert (untouched["gold"], untouched["sponsor"], untouched["point"]) == (50, 4, 7)
        assert untouched["game_deck"] != []


def test_close_keeps_the_frozen_standings_of_a_reset_pilot(make_client, session_factory):
    admin, player = setup_world(make_client, session_factory)
    championship_id = admin.post("/api/championships", json={"name": "Estate"}).json()["id"]
    pilot_id = make_pilot(player, "Ayrton")
    player.post(f"/api/championships/{championship_id}/pilots", json={"pilot_id": pilot_id})
    make_dirty(session_factory, pilot_id)
    admin.post(f"/api/championships/{championship_id}/close")
    rows = player.get(f"/api/championships/{championship_id}/standings").json()
    assert [row["pilot_name"] for row in rows] == ["Ayrton"]
