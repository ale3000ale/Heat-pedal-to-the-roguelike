from datetime import datetime

from app.db.models.championship import Championship, ChampionshipPilot
from app.db.models.deck import Deck
from app.db.models.pilot import Pilot
from app.services.cards import dump_cards
from app.services.shop_list import list_my_shops
from app.services.users import register_user

PASSWORD = "password123"


def new_deck(db):
    deck = Deck(cards=dump_cards([]))
    db.add(deck)
    db.flush()
    return deck


def new_pilot(db, user, name, deleted=False):
    pilot = Pilot(
        name=name,
        name_key=name.casefold(),
        user_id=user.id,
        inventory_deck_id=new_deck(db).id,
        sponsor_inventory_deck_id=new_deck(db).id,
        game_deck_id=new_deck(db).id,
        deleted_at=datetime(2026, 10, 1) if deleted else None,
    )
    db.add(pilot)
    db.flush()
    return pilot


def new_championship(db, name, closed=False):
    championship = Championship(
        name=name,
        name_key=name.casefold(),
        pool_deck_id=new_deck(db).id,
        sponsor_pool_deck_id=new_deck(db).id,
        is_closed=closed,
    )
    db.add(championship)
    db.flush()
    return championship


def enroll(db, championship, *pilots):
    for pilot in pilots:
        db.add(ChampionshipPilot(championship_id=championship.id, pilot_id=pilot.id))


def seed(session_factory):
    with session_factory() as db:
        user = register_user(db, "giocatore", PASSWORD)
        other = register_user(db, "altro", PASSWORD)
        db.commit()
        zeno = new_pilot(db, user, "zeno")
        anna = new_pilot(db, user, "Anna")
        gone = new_pilot(db, user, "Eliminato", deleted=True)
        bruno = new_pilot(db, other, "Bruno")
        beta = new_championship(db, "Beta")
        alfa = new_championship(db, "alfa")
        closed = new_championship(db, "Chiuso", closed=True)
        empty = new_championship(db, "Senza di me")
        enroll(db, beta, zeno, anna, gone, bruno)
        enroll(db, alfa, zeno)
        enroll(db, closed, anna)
        enroll(db, empty, bruno)
        db.commit()
        return user.id


def test_lists_active_championships_with_own_enrolled_pilots(session_factory):
    user_id = seed(session_factory)
    with session_factory() as db:
        from app.db.models import User

        entries = list_my_shops(db, db.get(User, user_id))
        assert [(e.championship_name, [p.name for p in e.pilots]) for e in entries] == [
            ("alfa", ["zeno"]),
            ("Beta", ["Anna", "zeno"]),
        ]


def test_user_without_pilots_has_no_shops(session_factory):
    seed(session_factory)
    with session_factory() as db:
        nobody = register_user(db, "nessuno", PASSWORD)
        db.commit()
        assert list_my_shops(db, nobody) == []


def test_route_requires_login_and_returns_shops(make_client, session_factory):
    seed(session_factory)
    assert make_client().get("/api/me/shops").status_code == 401
    client = make_client()
    login = client.post("/api/auth/login", json={"username": "giocatore", "password": PASSWORD})
    assert login.status_code == 200
    response = client.get("/api/me/shops")
    assert response.status_code == 200
    shops = response.json()["shops"]
    assert [s["championship_name"] for s in shops] == ["alfa", "Beta"]
    assert [p["name"] for p in shops[1]["pilots"]] == ["Anna", "zeno"]
