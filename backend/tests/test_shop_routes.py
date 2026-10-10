from datetime import datetime

from app.db.models.championship import Championship, ChampionshipPilot
from app.db.models.deck import Deck
from app.db.models.pilot import Pilot
from app.db.models.race import Race
from app.db.models.shop import Pack
from app.services.cards import STARTER_INVENTORY, CardEntry, dump_cards
from app.services.users import register_user

PASSWORD = "password123"


def card(name, copies):
    return CardEntry(name=name, path=f"cards/{name}.webp", copies=copies)


def new_deck(db, cards=()):
    deck = Deck(cards=dump_cards(list(cards)))
    db.add(deck)
    db.flush()
    return deck


def seed(session_factory):
    # Giocatore con il pilota Anna (15 oro), altro giocatore con Bruno, un admin; un
    # campionato con 5 copie di "Freni" e un pacchetto da 10 oro che ne estrae 3.
    with session_factory() as db:
        user = register_user(db, "giocatore", PASSWORD)
        other = register_user(db, "altro", PASSWORD)
        admin = register_user(db, "capo", PASSWORD)
        admin.role = "admin"
        db.commit()
        anna = Pilot(
            name="Anna",
            name_key="anna",
            gold=15,
            user_id=user.id,
            inventory_deck_id=new_deck(db, [card("Turbo", 2), *STARTER_INVENTORY]).id,
            sponsor_inventory_deck_id=new_deck(db).id,
            game_deck_id=new_deck(db).id,
        )
        bruno = Pilot(
            name="Bruno",
            name_key="bruno",
            user_id=other.id,
            inventory_deck_id=new_deck(db).id,
            sponsor_inventory_deck_id=new_deck(db).id,
            game_deck_id=new_deck(db).id,
        )
        db.add_all([anna, bruno])
        championship = Championship(
            name="Camp",
            name_key="camp",
            pool_deck_id=new_deck(db, [card("Freni", 5)]).id,
            sponsor_pool_deck_id=new_deck(db).id,
        )
        db.add(championship)
        db.flush()
        for pilot in (anna, bruno):
            db.add(ChampionshipPilot(championship_id=championship.id, pilot_id=pilot.id))
        pack = Pack(
            championship_id=championship.id,
            name="Base",
            image_path="x.webp",
            currency="gold",
            cost=10,
            modifiche_count=3,
            sponsor_count=0,
            filter_enabled=False,
        )
        db.add(pack)
        db.commit()
        return {
            "championship": championship.id,
            "anna": anna.id,
            "bruno": bruno.id,
            "pack": pack.id,
        }


def login(make_client, username):
    client = make_client()
    response = client.post("/api/auth/login", json={"username": username, "password": PASSWORD})
    assert response.status_code == 200
    return client


def test_shop_requires_login(client, session_factory):
    ids = seed(session_factory)
    assert client.get(f"/api/championships/{ids['championship']}/shop").status_code == 401


def test_player_opens_the_shop_with_own_pilot(make_client, session_factory):
    ids = seed(session_factory)
    client = login(make_client, "giocatore")
    response = client.get(
        f"/api/championships/{ids['championship']}/shop", params={"pilot_id": ids["anna"]}
    )
    assert response.status_code == 200
    body = response.json()
    assert body["pilot"]["name"] == "Anna"
    assert body["pilot"]["gold"] == 15
    assert body["read_only"] is False
    assert body["locked"] is False
    assert [(p["name"], p["sold_out"]) for p in body["packs"]] == [("Base", False)]


def test_player_access_rules(make_client, session_factory):
    ids = seed(session_factory)
    client = login(make_client, "giocatore")
    url = f"/api/championships/{ids['championship']}/shop"
    assert client.get(url).status_code == 403
    assert client.get(url, params={"pilot_id": ids["bruno"]}).status_code == 404
    assert client.get("/api/championships/9999/shop").status_code == 404


def test_admin_without_pilot_is_read_only(make_client, session_factory):
    ids = seed(session_factory)
    client = login(make_client, "capo")
    response = client.get(f"/api/championships/{ids['championship']}/shop")
    assert response.status_code == 200
    assert response.json()["pilot"] is None
    assert response.json()["read_only"] is True


def test_purchase_returns_cards_and_balance_then_runs_out_of_gold(make_client, session_factory):
    ids = seed(session_factory)
    client = login(make_client, "giocatore")
    url = f"/api/championships/{ids['championship']}/shop/purchases"
    body = {"pilot_id": ids["anna"], "pack_id": ids["pack"]}
    response = client.post(url, json=body)
    assert response.status_code == 201
    data = response.json()
    assert data["gold"] == 5
    assert [(c["name"], c["copies"]) for c in data["cards_modifiche"]] == [("Freni", 3)]
    assert data["cards_sponsor"] == []
    again = client.post(url, json=body)
    assert again.status_code == 409
    assert again.json()["detail"] == "Saldo insufficiente"


def test_purchase_is_blocked_while_a_race_is_in_progress(make_client, session_factory):
    ids = seed(session_factory)
    with session_factory() as db:
        db.add(Race(championship_id=ids["championship"], number=1, date=datetime.now()))
        db.commit()
    client = login(make_client, "giocatore")
    url = f"/api/championships/{ids['championship']}/shop"
    assert client.get(url, params={"pilot_id": ids["anna"]}).json()["locked"] is True
    response = client.post(
        f"{url}/purchases", json={"pilot_id": ids["anna"], "pack_id": ids["pack"]}
    )
    assert response.status_code == 409
    assert response.json()["detail"] == "Negozio bloccato: gara in corso"


def test_other_players_pilot_cannot_buy(make_client, session_factory):
    ids = seed(session_factory)
    client = login(make_client, "giocatore")
    response = client.post(
        f"/api/championships/{ids['championship']}/shop/purchases",
        json={"pilot_id": ids["bruno"], "pack_id": ids["pack"]},
    )
    assert response.status_code == 404


def test_inventory_route_hides_starter_cards(make_client, session_factory):
    ids = seed(session_factory)
    client = login(make_client, "giocatore")
    response = client.get(
        f"/api/championships/{ids['championship']}/shop/inventory",
        params={"pilot_id": ids["anna"]},
    )
    assert response.status_code == 200
    assert [(c["name"], c["copies"]) for c in response.json()["modifiche"]] == [("Turbo", 2)]
    assert response.json()["sponsor"] == []


def test_history_route_lists_own_purchases_by_pilot(make_client, session_factory):
    ids = seed(session_factory)
    client = login(make_client, "giocatore")
    base = f"/api/championships/{ids['championship']}/shop"
    client.post(f"{base}/purchases", json={"pilot_id": ids["anna"], "pack_id": ids["pack"]})
    response = client.get(f"{base}/history")
    assert response.status_code == 200
    pilots = response.json()["pilots"]
    assert [p["pilot_name"] for p in pilots] == ["Anna"]
    assert pilots[0]["purchases"][0]["pack_name"] == "Base"
    assert pilots[0]["purchases"][0]["cards_modifiche"][0]["copies"] == 3


def test_full_history_is_for_the_admin_only(make_client, session_factory):
    ids = seed(session_factory)
    player = login(make_client, "giocatore")
    url = f"/api/championships/{ids['championship']}/shop/history/all"
    player.post(
        f"/api/championships/{ids['championship']}/shop/purchases",
        json={"pilot_id": ids["anna"], "pack_id": ids["pack"]},
    )
    assert player.get(url).status_code == 403
    admin = login(make_client, "capo")
    response = admin.get(url)
    assert response.status_code == 200
    assert [p["pilot_name"] for p in response.json()["pilots"]] == ["Anna"]
