import pytest

from app.db.models import User
from app.db.models.championship import Championship
from app.db.models.deck import Deck, DeckPrototype
from app.security import hash_password
from app.services.cards import CardEntry, dump_cards, parse_cards

PASSWORD = "password123"
MODIFICHE = [
    CardEntry(name="Turbo", path="cards/base/modifiche/turbo_2.webp", copies=2),
    CardEntry(name="Ruota da bagnato", path="cards/base/modifiche/ruota_3.webp", copies=3),
]
SPONSOR = [CardEntry(name="Premio", path="cards/base/sponsor/premio_1.webp", copies=1)]


@pytest.fixture()
def media(tmp_path, monkeypatch):
    # Cartella multimediale di prova: la ricarica legge da qui e non da backend/media.
    monkeypatch.setattr("app.services.pools.MEDIA_DIR", tmp_path)
    return tmp_path


def touch(media, kind, *names):
    folder = media / "cards" / "base" / kind
    folder.mkdir(parents=True, exist_ok=True)
    for name in names:
        (folder / name).write_bytes(b"x")


def seed(session_factory, modifiche=None, sponsor=None, with_sponsor=True):
    # Pool di base di prova: modifiche ("default") e, se richiesto, sponsor.
    with session_factory() as db:
        db.add(
            DeckPrototype(
                name="default", base_cards=dump_cards(modifiche or []), kind="modifiche"
            )
        )
        if with_sponsor:
            db.add(
                DeckPrototype(
                    name="sponsor", base_cards=dump_cards(sponsor or []), kind="sponsor"
                )
            )
        db.commit()


def make_admin(make_client, session_factory):
    client = make_client()
    with session_factory() as db:
        db.add(User(username="capo", password=hash_password(PASSWORD), role="admin"))
        db.commit()
    r = client.post("/api/auth/login", json={"username": "capo", "password": PASSWORD})
    assert r.status_code == 200
    return client


def make_player(make_client):
    client = make_client()
    r = client.post("/api/auth/register", json={"username": "mario", "password": PASSWORD})
    assert r.status_code == 201
    return client


def base_id(admin, name):
    return next(p["id"] for p in admin.get("/api/pools").json() if p["name"] == name)


def reload_pool(admin, kind):
    return admin.post(f"/api/pools/base/{kind}/reload")


def cards_of(admin, pool_id):
    return admin.get(f"/api/pools/{pool_id}").json()["cards"]


def test_reload_adds_cards_found_in_folder(make_client, session_factory, media):
    seed(session_factory)
    admin = make_admin(make_client, session_factory)
    touch(media, "modifiche", "turbo_2.webp", "ruota da bagnato_3.webp")
    r = reload_pool(admin, "modifiche")
    assert r.status_code == 200
    assert r.json() == {
        "added": ["ruota da bagnato", "turbo"],
        "removed": [],
        "already_present": 0,
        "warnings": [],
    }
    assert cards_of(admin, base_id(admin, "default")) == [
        {
            "name": "ruota da bagnato",
            "path": "cards/base/modifiche/ruota da bagnato_3.webp",
            "copies": 3,
        },
        {"name": "turbo", "path": "cards/base/modifiche/turbo_2.webp", "copies": 2},
    ]


def test_reload_never_changes_cards_already_in_the_pool(make_client, session_factory, media):
    seed(
        session_factory,
        modifiche=[CardEntry(name="Turbo", path="cards/base/turbo.webp", copies=5)],
    )
    admin = make_admin(make_client, session_factory)
    touch(media, "modifiche", "turbo_2.webp", "nuova_1.webp")
    r = reload_pool(admin, "modifiche")
    assert r.json()["added"] == ["nuova"]
    assert r.json()["already_present"] == 1
    assert cards_of(admin, base_id(admin, "default")) == [
        {"name": "Turbo", "path": "cards/base/turbo.webp", "copies": 5},
        {"name": "nuova", "path": "cards/base/modifiche/nuova_1.webp", "copies": 1},
    ]


def test_reload_recognizes_a_renamed_card_by_path(make_client, session_factory, media):
    seed(
        session_factory,
        modifiche=[
            CardEntry(name="Rinominata", path="cards/base/modifiche/turbo_2.webp", copies=4)
        ],
    )
    admin = make_admin(make_client, session_factory)
    touch(media, "modifiche", "turbo_2.webp")
    r = reload_pool(admin, "modifiche")
    assert r.json() == {"added": [], "removed": [], "already_present": 1, "warnings": []}
    assert [c["name"] for c in cards_of(admin, base_id(admin, "default"))] == ["Rinominata"]


def test_reload_removes_cards_whose_file_is_gone(make_client, session_factory, media):
    seed(session_factory, modifiche=MODIFICHE)
    admin = make_admin(make_client, session_factory)
    touch(media, "modifiche", "turbo_2.webp")
    r = reload_pool(admin, "modifiche")
    assert r.json() == {
        "added": [],
        "removed": ["Ruota da bagnato"],
        "already_present": 1,
        "warnings": [],
    }
    assert cards_of(admin, base_id(admin, "default")) == [
        {"name": "Turbo", "path": "cards/base/modifiche/turbo_2.webp", "copies": 2}
    ]


def test_reload_adds_and_removes_in_the_same_run(make_client, session_factory, media):
    seed(session_factory, modifiche=MODIFICHE)
    admin = make_admin(make_client, session_factory)
    touch(media, "modifiche", "turbo_2.webp", "nuova_1.webp")
    r = reload_pool(admin, "modifiche").json()
    assert r["added"] == ["nuova"]
    assert r["removed"] == ["Ruota da bagnato"]
    assert r["already_present"] == 1
    names = [c["name"] for c in cards_of(admin, base_id(admin, "default"))]
    assert names == ["Turbo", "nuova"]


def test_reload_removes_nothing_when_the_folder_has_no_images(
    make_client, session_factory, media
):
    seed(session_factory, modifiche=MODIFICHE)
    admin = make_admin(make_client, session_factory)
    touch(media, "modifiche", "nota.txt")
    r = reload_pool(admin, "modifiche").json()
    assert r["removed"] == []
    assert len(r["warnings"]) == 1
    assert len(cards_of(admin, base_id(admin, "default"))) == 2


def test_reload_removes_nothing_when_the_folder_is_missing(make_client, session_factory, media):
    seed(session_factory, modifiche=MODIFICHE)
    admin = make_admin(make_client, session_factory)
    r = reload_pool(admin, "modifiche").json()
    assert r["removed"] == []
    assert len(cards_of(admin, base_id(admin, "default"))) == 2


def test_reload_twice_adds_nothing_the_second_time(make_client, session_factory, media):
    seed(session_factory)
    admin = make_admin(make_client, session_factory)
    touch(media, "modifiche", "turbo_2.webp")
    assert reload_pool(admin, "modifiche").json()["added"] == ["turbo"]
    second = reload_pool(admin, "modifiche").json()
    assert second["added"] == []
    assert second["removed"] == []
    assert second["already_present"] == 1


def test_reload_discards_bad_files_with_a_warning(make_client, session_factory, media):
    seed(session_factory)
    admin = make_admin(make_client, session_factory)
    touch(
        media,
        "modifiche",
        "senza.webp",
        "zero_0.webp",
        "foto_2.png",
        "ok_1.png",
        "ok_1.webp",
        "nota.txt",
    )
    r = reload_pool(admin, "modifiche").json()
    assert r["added"] == ["ok"]
    assert len(r["warnings"]) == 3
    text = " ".join(r["warnings"])
    assert "senza.webp" in text
    assert "zero_0.webp" in text
    assert "foto_2.png" in text


def test_reload_works_per_kind(make_client, session_factory, media):
    seed(session_factory)
    admin = make_admin(make_client, session_factory)
    touch(media, "sponsor", "premio_1.webp")
    assert reload_pool(admin, "sponsor").json()["added"] == ["premio"]
    assert cards_of(admin, base_id(admin, "sponsor"))[0]["path"] == (
        "cards/base/sponsor/premio_1.webp"
    )
    assert cards_of(admin, base_id(admin, "default")) == []


def test_reload_with_missing_folder_only_warns(make_client, session_factory, media):
    seed(session_factory)
    admin = make_admin(make_client, session_factory)
    r = reload_pool(admin, "modifiche")
    assert r.status_code == 200
    assert r.json()["added"] == []
    assert len(r.json()["warnings"]) == 1


def test_reload_is_admin_only_and_needs_the_base_pool(make_client, session_factory, media):
    anonymous = make_client()
    assert reload_pool(anonymous, "modifiche").status_code == 401
    player = make_player(make_client)
    assert reload_pool(player, "modifiche").status_code == 403
    admin = make_admin(make_client, session_factory)
    assert reload_pool(admin, "modifiche").status_code == 404
    seed(session_factory)
    assert reload_pool(admin, "altro").status_code == 422


def test_derived_pool_takes_cards_from_the_base_of_its_own_kind(make_client, session_factory):
    seed(session_factory, modifiche=MODIFICHE, sponsor=SPONSOR)
    admin = make_admin(make_client, session_factory)
    ok = admin.post(
        "/api/pools",
        json={"name": "Premi", "kind": "sponsor", "cards": [{"name": "premio", "copies": 1}]},
    )
    assert ok.status_code == 201
    assert ok.json()["kind"] == "sponsor"
    assert ok.json()["cards"][0]["name"] == "Premio"
    wrong = admin.post(
        "/api/pools",
        json={"name": "Sbagliata", "cards": [{"name": "Premio", "copies": 1}]},
    )
    assert wrong.status_code == 422
    assert [p["kind"] for p in admin.get("/api/pools").json()] == [
        "modifiche",
        "sponsor",
        "sponsor",
    ]


def test_base_pools_cannot_be_deleted(make_client, session_factory):
    seed(session_factory)
    admin = make_admin(make_client, session_factory)
    assert admin.delete(f"/api/pools/{base_id(admin, 'default')}").status_code == 409
    assert admin.delete(f"/api/pools/{base_id(admin, 'sponsor')}").status_code == 409


def test_championship_gets_independent_copies_of_both_pools(make_client, session_factory):
    seed(session_factory, modifiche=MODIFICHE, sponsor=SPONSOR)
    admin = make_admin(make_client, session_factory)
    r = admin.post("/api/championships", json={"name": "Estate"})
    assert r.status_code == 201
    with session_factory() as db:
        championship = db.get(Championship, r.json()["id"])
        modifiche_deck = db.get(Deck, championship.pool_deck_id)
        sponsor_deck = db.get(Deck, championship.sponsor_pool_deck_id)
        assert parse_cards(modifiche_deck.cards) == MODIFICHE
        assert parse_cards(sponsor_deck.cards) == SPONSOR
        sponsor_base = db.query(DeckPrototype).filter_by(name="sponsor").one()
        assert sponsor_deck.id_prototype == sponsor_base.id
        sponsor_base.base_cards = dump_cards([])
        db.commit()
        assert parse_cards(db.get(Deck, championship.sponsor_pool_deck_id).cards) == SPONSOR


def test_championship_with_chosen_pools_of_both_kinds(make_client, session_factory):
    seed(session_factory, modifiche=MODIFICHE, sponsor=SPONSOR)
    admin = make_admin(make_client, session_factory)
    mod = admin.post(
        "/api/pools", json={"name": "Corta", "cards": [{"name": "Turbo", "copies": 1}]}
    ).json()
    spo = admin.post(
        "/api/pools",
        json={"name": "Premi", "kind": "sponsor", "cards": [{"name": "Premio", "copies": 1}]},
    ).json()
    r = admin.post(
        "/api/championships",
        json={"name": "Inverno", "pool_id": mod["id"], "sponsor_pool_id": spo["id"]},
    )
    assert r.status_code == 201
    with session_factory() as db:
        championship = db.get(Championship, r.json()["id"])
        modifiche_deck = db.get(Deck, championship.pool_deck_id)
        sponsor_deck = db.get(Deck, championship.sponsor_pool_deck_id)
        assert [c.name for c in parse_cards(modifiche_deck.cards)] == ["Turbo"]
        assert modifiche_deck.id_prototype == mod["id"]
        assert [c.name for c in parse_cards(sponsor_deck.cards)] == ["Premio"]
        assert sponsor_deck.id_prototype == spo["id"]


def test_championship_rejects_a_pool_of_the_wrong_kind(make_client, session_factory):
    seed(session_factory, modifiche=MODIFICHE, sponsor=SPONSOR)
    admin = make_admin(make_client, session_factory)
    mod = admin.post(
        "/api/pools", json={"name": "Corta", "cards": [{"name": "Turbo", "copies": 1}]}
    ).json()
    spo = admin.post(
        "/api/pools",
        json={"name": "Premi", "kind": "sponsor", "cards": [{"name": "Premio", "copies": 1}]},
    ).json()
    wrong_modifiche = admin.post(
        "/api/championships", json={"name": "Uno", "pool_id": spo["id"]}
    )
    wrong_sponsor = admin.post(
        "/api/championships", json={"name": "Due", "sponsor_pool_id": mod["id"]}
    )
    assert wrong_modifiche.status_code == 422
    assert wrong_sponsor.status_code == 422
    with session_factory() as db:
        assert db.query(Championship).count() == 0
        assert db.query(Deck).count() == 0


def test_championship_without_sponsor_base_pool_has_no_sponsor_copy(make_client, session_factory):
    seed(session_factory, modifiche=MODIFICHE, with_sponsor=False)
    admin = make_admin(make_client, session_factory)
    r = admin.post("/api/championships", json={"name": "Estate"})
    assert r.status_code == 201
    with session_factory() as db:
        championship = db.get(Championship, r.json()["id"])
        assert championship.pool_deck_id is not None
        assert championship.sponsor_pool_deck_id is None


def test_deleting_a_championship_removes_both_pool_copies(make_client, session_factory):
    seed(session_factory, modifiche=MODIFICHE, sponsor=SPONSOR)
    admin = make_admin(make_client, session_factory)
    championship_id = admin.post("/api/championships", json={"name": "Estate"}).json()["id"]
    with session_factory() as db:
        assert db.query(Deck).count() == 2
    admin.post(f"/api/championships/{championship_id}/close")
    assert admin.delete(f"/api/championships/{championship_id}").status_code == 204
    with session_factory() as db:
        assert db.query(Deck).count() == 0
