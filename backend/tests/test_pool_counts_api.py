from app.db.models import User
from app.db.models.deck import DeckPrototype
from app.security import hash_password
from app.services.cards import CardEntry, dump_cards

PASSWORD = "password123"
MODIFICHE = [
    CardEntry(name="Turbo", path="cards/base/modifiche/turbo_2.webp", copies=2),
    CardEntry(name="Ruota da bagnato", path="cards/base/modifiche/ruota_3.webp", copies=3),
]


def make_admin(make_client, session_factory):
    client = make_client()
    with session_factory() as db:
        db.add(User(username="capo", password=hash_password(PASSWORD), role="admin"))
        db.commit()
    r = client.post("/api/auth/login", json={"username": "capo", "password": PASSWORD})
    assert r.status_code == 200
    return client


def seed(session_factory):
    with session_factory() as db:
        db.add(DeckPrototype(name="default", base_cards=dump_cards(MODIFICHE), kind="modifiche"))
        db.add(DeckPrototype(name="sponsor", base_cards="[]", kind="sponsor"))
        db.commit()


def counts(pools):
    return {p["name"]: (p["cards_count"], p["copies_count"]) for p in pools}


def test_list_shows_cards_and_copies_count(make_client, session_factory):
    seed(session_factory)
    admin = make_admin(make_client, session_factory)
    assert counts(admin.get("/api/pools").json()) == {"default": (2, 5), "sponsor": (0, 0)}


def test_derived_pool_counts_its_own_copies(make_client, session_factory):
    seed(session_factory)
    admin = make_admin(make_client, session_factory)
    created = admin.post(
        "/api/pools", json={"name": "Corta", "cards": [{"name": "Turbo", "copies": 1}]}
    )
    assert created.status_code == 201
    assert (created.json()["cards_count"], created.json()["copies_count"]) == (1, 1)
    assert counts(admin.get("/api/pools").json())["Corta"] == (1, 1)


def test_detail_includes_the_counts(make_client, session_factory):
    seed(session_factory)
    admin = make_admin(make_client, session_factory)
    pool_id = next(p["id"] for p in admin.get("/api/pools").json() if p["name"] == "default")
    detail = admin.get(f"/api/pools/{pool_id}").json()
    assert (detail["cards_count"], detail["copies_count"]) == (2, 5)
    assert len(detail["cards"]) == 2
