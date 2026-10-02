import json

from app.db.models import User
from app.db.models.championship import Championship
from app.db.models.deck import Deck, DeckPrototype
from app.db.models.pilot import Pilot
from app.security import hash_password
from app.services.cards import STARTER_INVENTORY, CardEntry, dump_cards, parse_cards

PASSWORD = "password123"
BASE_CARDS = [
    CardEntry(name="Velocità 1", path="cards/starter/velocita-1.webp", copies=3),
    CardEntry(name="Ruota da bagnato", path="cards/base/ruota-da-bagnato.webp", copies=2),
    CardEntry(name="Turbo", path="cards/base/turbo.webp", copies=1),
]


def seed_base_pool(session_factory):
    # Pool di base di prova: il prototipo "default" con tre carte.
    with session_factory() as db:
        db.add(DeckPrototype(name="default", base_cards=dump_cards(BASE_CARDS)))
        db.commit()


def make_admin(make_client, session_factory):
    client = make_client()
    with session_factory() as db:
        db.add(User(username="capo", password=hash_password(PASSWORD), role="admin"))
        db.commit()
    r = client.post("/api/auth/login", json={"username": "capo", "password": PASSWORD})
    assert r.status_code == 200
    return client


def make_player(make_client, username="mario"):
    client = make_client()
    r = client.post("/api/auth/register", json={"username": username, "password": PASSWORD})
    assert r.status_code == 201
    return client


def make_pilot(player, name="Ayrton", with_team=True):
    team_id = None
    if with_team:
        team_id = player.post("/api/teams", json={"name": f"Team {name}"}).json()["id"]
    r = player.post("/api/pilots", json={"name": name, "team_id": team_id})
    assert r.status_code == 201
    return r.json()["id"]


def new_championship(admin, name="Estate", pool_id=None):
    return admin.post("/api/championships", json={"name": name, "pool_id": pool_id})


def enroll(player, championship_id, pilot_id):
    return player.post(f"/api/championships/{championship_id}/pilots", json={"pilot_id": pilot_id})


def test_pools_are_admin_only(make_client, session_factory):
    seed_base_pool(session_factory)
    anonymous = make_client()
    assert anonymous.get("/api/pools").status_code == 401
    player = make_player(make_client)
    assert player.get("/api/pools").status_code == 403
    assert player.post("/api/pools", json={"name": "Mia", "cards": []}).status_code == 403
    assert player.delete("/api/pools/1").status_code == 403


def test_create_pool_from_base_keeps_base_spelling_and_paths(make_client, session_factory):
    seed_base_pool(session_factory)
    admin = make_admin(make_client, session_factory)
    r = admin.post(
        "/api/pools",
        json={
            "name": "  Pool   corta ",
            "cards": [{"name": "turbo", "copies": 1}, {"name": "RUOTA DA BAGNATO", "copies": 1}],
        },
    )
    assert r.status_code == 201
    assert r.json()["name"] == "Pool corta"
    assert r.json()["cards"] == [
        {"name": "Turbo", "path": "cards/base/turbo.webp", "copies": 1},
        {"name": "Ruota da bagnato", "path": "cards/base/ruota-da-bagnato.webp", "copies": 1},
    ]
    assert [p["name"] for p in admin.get("/api/pools").json()] == ["default", "Pool corta"]


def test_create_pool_rejects_bad_choices(make_client, session_factory):
    seed_base_pool(session_factory)
    admin = make_admin(make_client, session_factory)

    def create(cards, name="Prova"):
        return admin.post("/api/pools", json={"name": name, "cards": cards})

    assert create([{"name": "Inesistente", "copies": 1}]).status_code == 422
    assert create([{"name": "Turbo", "copies": 2}]).status_code == 422
    assert create([{"name": "Turbo", "copies": 1}, {"name": "turbo", "copies": 1}]).status_code == 422
    assert create([]).status_code == 422
    assert create([{"name": "Turbo", "copies": 0}]).status_code == 422
    assert create([{"name": "Turbo", "copies": 1}], name="DEFAULT").status_code == 409


def test_pool_name_is_unique_ignoring_case(make_client, session_factory):
    seed_base_pool(session_factory)
    admin = make_admin(make_client, session_factory)
    cards = [{"name": "Turbo", "copies": 1}]
    assert admin.post("/api/pools", json={"name": "Gioconda", "cards": cards}).status_code == 201
    assert admin.post("/api/pools", json={"name": "gioconda", "cards": cards}).status_code == 409


def test_delete_pool_but_not_the_base_one(make_client, session_factory):
    seed_base_pool(session_factory)
    admin = make_admin(make_client, session_factory)
    pool_id = admin.post(
        "/api/pools", json={"name": "Extra", "cards": [{"name": "Turbo", "copies": 1}]}
    ).json()["id"]
    assert admin.delete(f"/api/pools/{pool_id}").status_code == 204
    assert admin.get(f"/api/pools/{pool_id}").status_code == 404
    base_id = admin.get("/api/pools").json()[0]["id"]
    assert admin.delete(f"/api/pools/{base_id}").status_code == 409
    assert admin.delete("/api/pools/999").status_code == 404


def test_create_championship_is_admin_only(make_client, session_factory):
    seed_base_pool(session_factory)
    assert new_championship(make_client()).status_code == 401
    player = make_player(make_client)
    assert new_championship(player).status_code == 403


def test_championship_gets_independent_copy_of_base_pool(make_client, session_factory):
    seed_base_pool(session_factory)
    admin = make_admin(make_client, session_factory)
    r = new_championship(admin, "Gioconda")
    assert r.status_code == 201
    assert r.json()["name"] == "Gioconda"
    assert r.json()["is_closed"] is False
    assert r.json()["pilots_count"] == 0
    with session_factory() as db:
        championship = db.get(Championship, r.json()["id"])
        deck = db.get(Deck, championship.pool_deck_id)
        assert parse_cards(deck.cards) == BASE_CARDS
        base = db.query(DeckPrototype).one()
        assert deck.id_prototype == base.id
        base.base_cards = dump_cards(BASE_CARDS[:1])
        db.commit()
        assert parse_cards(db.get(Deck, championship.pool_deck_id).cards) == BASE_CARDS


def test_championship_with_chosen_pool(make_client, session_factory):
    seed_base_pool(session_factory)
    admin = make_admin(make_client, session_factory)
    pool = admin.post(
        "/api/pools", json={"name": "Corta", "cards": [{"name": "Turbo", "copies": 1}]}
    ).json()
    r = new_championship(admin, "Inverno", pool["id"])
    assert r.status_code == 201
    with session_factory() as db:
        deck = db.get(Deck, db.get(Championship, r.json()["id"]).pool_deck_id)
        assert [c.name for c in parse_cards(deck.cards)] == ["Turbo"]
        assert deck.id_prototype == pool["id"]


def test_championship_rejects_unknown_pool_invalid_and_duplicate_names(make_client, session_factory):
    seed_base_pool(session_factory)
    admin = make_admin(make_client, session_factory)
    assert new_championship(admin, "Estate", 999).status_code == 404
    assert new_championship(admin, "a").status_code == 422
    assert new_championship(admin, "Gioconda").status_code == 201
    assert new_championship(admin, "GIOCONDA").status_code == 409
    assert new_championship(admin, "  gioconda ").status_code == 409


def test_championship_without_base_pool_is_404(make_client, session_factory):
    admin = make_admin(make_client, session_factory)
    assert new_championship(admin).status_code == 404


def test_players_can_list_and_read_championships(make_client, session_factory):
    seed_base_pool(session_factory)
    admin = make_admin(make_client, session_factory)
    first = new_championship(admin, "Estate").json()["id"]
    new_championship(admin, "Inverno")
    player = make_player(make_client)
    names = [c["name"] for c in player.get("/api/championships").json()]
    assert sorted(names) == ["Estate", "Inverno"]
    detail = player.get(f"/api/championships/{first}")
    assert detail.status_code == 200
    assert detail.json()["pilots"] == []
    assert player.get("/api/championships/999").status_code == 404
    assert make_client().get("/api/championships").status_code == 401


def test_close_championship(make_client, session_factory):
    seed_base_pool(session_factory)
    admin = make_admin(make_client, session_factory)
    player = make_player(make_client)
    championship_id = new_championship(admin).json()["id"]
    assert player.post(f"/api/championships/{championship_id}/close").status_code == 403
    r = admin.post(f"/api/championships/{championship_id}/close")
    assert r.status_code == 200
    assert r.json()["is_closed"] is True
    assert admin.post(f"/api/championships/{championship_id}/close").status_code == 409
    assert admin.post("/api/championships/999/close").status_code == 404


def test_enroll_resets_the_pilot(make_client, session_factory):
    seed_base_pool(session_factory)
    admin = make_admin(make_client, session_factory)
    player = make_player(make_client)
    pilot_id = make_pilot(player)
    with session_factory() as db:
        pilot = db.get(Pilot, pilot_id)
        pilot.gold, pilot.sponsor, pilot.point = 50, 4, 7
        db.get(Deck, pilot.game_deck_id).cards = dump_cards(BASE_CARDS[:1])
        db.get(Deck, pilot.inventory_deck_id).cards = dump_cards(BASE_CARDS)
        db.commit()
    championship_id = new_championship(admin).json()["id"]
    r = enroll(player, championship_id, pilot_id)
    assert r.status_code == 201
    assert r.json()["name"] == "Ayrton"
    after = player.get(f"/api/pilots/{pilot_id}").json()
    assert (after["gold"], after["sponsor"], after["point"]) == (0, 0, 0)
    assert after["game_deck"] == []
    assert after["inventory"] == [card.model_dump() for card in STARTER_INVENTORY]
    detail = player.get(f"/api/championships/{championship_id}").json()
    assert detail["pilots_count"] == 1
    assert [p["name"] for p in detail["pilots"]] == ["Ayrton"]


def test_enroll_requires_login_team_and_ownership(make_client, session_factory):
    seed_base_pool(session_factory)
    admin = make_admin(make_client, session_factory)
    championship_id = new_championship(admin).json()["id"]
    player = make_player(make_client, "mario")
    other = make_player(make_client, "luigi")
    no_team = make_pilot(player, "Senza", with_team=False)
    with_team = make_pilot(player, "Con")
    assert enroll(make_client(), championship_id, with_team).status_code == 401
    assert enroll(player, championship_id, no_team).status_code == 409
    assert enroll(other, championship_id, with_team).status_code == 404
    assert enroll(player, championship_id, 999).status_code == 404
    assert enroll(player, 999, with_team).status_code == 404


def test_pilot_cannot_be_in_two_active_championships(make_client, session_factory):
    seed_base_pool(session_factory)
    admin = make_admin(make_client, session_factory)
    player = make_player(make_client)
    pilot_id = make_pilot(player)
    first = new_championship(admin, "Estate").json()["id"]
    second = new_championship(admin, "Inverno").json()["id"]
    assert enroll(player, first, pilot_id).status_code == 201
    assert enroll(player, first, pilot_id).status_code == 409
    assert enroll(player, second, pilot_id).status_code == 409


def test_pilot_can_enroll_again_after_closing(make_client, session_factory):
    seed_base_pool(session_factory)
    admin = make_admin(make_client, session_factory)
    player = make_player(make_client)
    pilot_id = make_pilot(player)
    first = new_championship(admin, "Estate").json()["id"]
    second = new_championship(admin, "Inverno").json()["id"]
    enroll(player, first, pilot_id)
    admin.post(f"/api/championships/{first}/close")
    assert enroll(player, second, pilot_id).status_code == 201
    assert player.get(f"/api/championships/{first}").json()["pilots_count"] == 1


def test_cannot_enroll_in_closed_championship(make_client, session_factory):
    seed_base_pool(session_factory)
    admin = make_admin(make_client, session_factory)
    player = make_player(make_client)
    pilot_id = make_pilot(player)
    championship_id = new_championship(admin).json()["id"]
    admin.post(f"/api/championships/{championship_id}/close")
    assert enroll(player, championship_id, pilot_id).status_code == 409


def test_enrolled_pilot_is_locked(make_client, session_factory):
    seed_base_pool(session_factory)
    admin = make_admin(make_client, session_factory)
    player = make_player(make_client)
    pilot_id = make_pilot(player)
    championship_id = new_championship(admin).json()["id"]
    enroll(player, championship_id, pilot_id)
    assert player.put(f"/api/pilots/{pilot_id}/team", json={"team_id": None}).status_code == 409
    assert player.delete(f"/api/pilots/{pilot_id}").status_code == 409
    admin.post(f"/api/championships/{championship_id}/close")
    assert player.delete(f"/api/pilots/{pilot_id}").status_code == 204
    detail = player.get(f"/api/championships/{championship_id}").json()
    assert [p["name"] for p in detail["pilots"]] == ["Ayrton"]
    