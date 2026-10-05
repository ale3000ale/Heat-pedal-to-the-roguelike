from app.db.models.deck import Deck
from app.db.models.pilot import Pilot
from app.services.cards import CardEntry, dump_cards

from .test_pilots_api import create_pilot, enroll, register

FIRST = "cards/starter/velocita-1.webp"


def add(client, pilot_id, path=FIRST):
    return client.post(f"/api/pilots/{pilot_id}/deck/add", json={"path": path})


def remove(client, pilot_id, path=FIRST):
    return client.post(f"/api/pilots/{pilot_id}/deck/remove", json={"path": path})


def copies(cards, name):
    # Copie della carta indicata (0 se non c'è).
    return next((c["copies"] for c in cards if c["name"] == name), 0)


def give_extra_cards(session_factory, pilot_id, amount):
    # Sostituisce l'inventario con una sola carta in molte copie (serve per il limite).
    with session_factory() as db:
        pilot = db.get(Pilot, pilot_id)
        deck = db.get(Deck, pilot.inventory_deck_id)
        deck.cards = dump_cards(
            [CardEntry(name="Extra", path="cards/test/extra.webp", copies=amount)]
        )
        db.commit()


def test_deck_routes_require_login(client):
    assert add(client, 1).status_code == 401
    assert remove(client, 1).status_code == 401


def test_add_moves_one_copy_to_the_game_deck(client):
    register(client)
    pilot_id = create_pilot(client).json()["id"]
    r = add(client, pilot_id)
    assert r.status_code == 200
    body = r.json()
    assert copies(body["inventory"], "Velocità 1") == 2
    assert copies(body["game_deck"], "Velocità 1") == 1
    saved = client.get(f"/api/pilots/{pilot_id}").json()
    assert saved["game_deck"] == body["game_deck"]
    assert saved["inventory"] == body["inventory"]


def test_add_all_copies_removes_the_card_from_the_inventory(client):
    register(client)
    pilot_id = create_pilot(client).json()["id"]
    for _ in range(3):
        r = add(client, pilot_id)
        assert r.status_code == 200
    body = r.json()
    assert copies(body["inventory"], "Velocità 1") == 0
    assert copies(body["game_deck"], "Velocità 1") == 3
    assert add(client, pilot_id).status_code == 404


def test_remove_returns_one_copy_to_the_inventory(client):
    register(client)
    pilot_id = create_pilot(client).json()["id"]
    add(client, pilot_id)
    add(client, pilot_id)
    r = remove(client, pilot_id)
    assert r.status_code == 200
    body = r.json()
    assert copies(body["inventory"], "Velocità 1") == 2
    assert copies(body["game_deck"], "Velocità 1") == 1
    remove(client, pilot_id)
    r = remove(client, pilot_id)
    assert r.status_code == 404
    assert copies(client.get(f"/api/pilots/{pilot_id}").json()["inventory"], "Velocità 1") == 3


def test_unknown_card_is_404(client):
    register(client)
    pilot_id = create_pilot(client).json()["id"]
    assert add(client, pilot_id, "cards/nope.webp").status_code == 404
    assert remove(client, pilot_id, "cards/nope.webp").status_code == 404


def test_move_requires_the_path(client):
    register(client)
    pilot_id = create_pilot(client).json()["id"]
    r = client.post(f"/api/pilots/{pilot_id}/deck/add", json={})
    assert r.status_code == 422


def test_game_deck_is_limited_to_15_cards(client, session_factory):
    register(client)
    pilot_id = create_pilot(client).json()["id"]
    give_extra_cards(session_factory, pilot_id, 20)
    for _ in range(15):
        assert add(client, pilot_id, "cards/test/extra.webp").status_code == 200
    r = add(client, pilot_id, "cards/test/extra.webp")
    assert r.status_code == 409
    saved = client.get(f"/api/pilots/{pilot_id}").json()
    assert copies(saved["game_deck"], "Extra") == 15
    assert copies(saved["inventory"], "Extra") == 5
    assert remove(client, pilot_id, "cards/test/extra.webp").status_code == 200
    assert add(client, pilot_id, "cards/test/extra.webp").status_code == 200


def test_other_users_or_unknown_pilot_is_404(make_client):
    first, second = make_client(), make_client()
    register(first, "mario")
    register(second, "luigi")
    pilot_id = create_pilot(first).json()["id"]
    assert add(second, pilot_id).status_code == 404
    assert remove(second, pilot_id).status_code == 404
    assert add(first, 999).status_code == 404
    assert copies(first.get(f"/api/pilots/{pilot_id}").json()["game_deck"], "Velocità 1") == 0


def test_decks_can_be_changed_in_an_active_championship(client, session_factory):
    register(client)
    pilot_id = create_pilot(client).json()["id"]
    enroll(session_factory, pilot_id, closed=False)
    assert add(client, pilot_id).status_code == 200
    assert remove(client, pilot_id).status_code == 200


def test_active_championship_is_shown_in_detail_and_list(client, session_factory):
    register(client)
    free = create_pilot(client, "Libero").json()["id"]
    active = create_pilot(client, "Attivo").json()["id"]
    finished = create_pilot(client, "Concluso").json()["id"]
    enroll(session_factory, active, closed=False)
    enroll(session_factory, finished, closed=True)

    assert client.get(f"/api/pilots/{free}").json()["championship"] is None
    assert client.get(f"/api/pilots/{finished}").json()["championship"] is None
    detail = client.get(f"/api/pilots/{active}").json()["championship"]
    assert detail["name"] == f"Campionato {active}"

    listed = {p["name"]: p["championship"] for p in client.get("/api/pilots").json()}
    assert listed["Libero"] is None
    assert listed["Concluso"] is None
    assert listed["Attivo"]["name"] == f"Campionato {active}"
    assert listed["Attivo"]["id"] == detail["id"]
