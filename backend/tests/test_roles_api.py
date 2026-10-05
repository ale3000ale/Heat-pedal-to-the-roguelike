from app.db.models import User
from app.db.models.deck import DeckPrototype
from app.security import hash_password
from app.services.cards import CardEntry, dump_cards

PASSWORD = "password123"
BASE_CARDS = [CardEntry(name="Velocità 1", path="cards/starter/velocita-1.webp", copies=3)]


def make_admin(make_client, session_factory):
    client = make_client()
    with session_factory() as db:
        db.add(DeckPrototype(name="default", base_cards=dump_cards(BASE_CARDS)))
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


def ids_by_name(admin):
    return {u["username"]: u["id"] for u in admin.get("/api/admin/users").json()}


def test_user_roles_are_admin_only(make_client, session_factory):
    make_admin(make_client, session_factory)
    player = make_player(make_client)
    anonymous = make_client()
    for client, code in ((anonymous, 401), (player, 403)):
        assert client.get("/api/admin/users").status_code == code
        assert client.put("/api/admin/users/1/role", json={"role": "judge"}).status_code == code


def test_admin_lists_users_with_roles(make_client, session_factory):
    admin = make_admin(make_client, session_factory)
    make_player(make_client, "mario")
    make_player(make_client, "luigi")
    users = admin.get("/api/admin/users").json()
    assert [(u["username"], u["role"]) for u in users] == [
        ("capo", "admin"),
        ("luigi", "player"),
        ("mario", "player"),
    ]
    assert all("password" not in u for u in users)


def test_admin_assigns_and_removes_the_judge_role(make_client, session_factory):
    admin = make_admin(make_client, session_factory)
    player = make_player(make_client)
    mario = ids_by_name(admin)["mario"]
    r = admin.put(f"/api/admin/users/{mario}/role", json={"role": "judge"})
    assert r.status_code == 200
    assert (r.json()["username"], r.json()["role"]) == ("mario", "judge")
    assert player.get("/api/admin/users").status_code == 403
    r = admin.put(f"/api/admin/users/{mario}/role", json={"role": "player"})
    assert r.json()["role"] == "player"


def test_admin_role_cannot_be_changed(make_client, session_factory):
    admin = make_admin(make_client, session_factory)
    capo = ids_by_name(admin)["capo"]
    assert admin.put(f"/api/admin/users/{capo}/role", json={"role": "player"}).status_code == 409
    assert admin.get("/api/admin/users").json()[0]["role"] == "admin"


def test_invalid_roles_and_unknown_users(make_client, session_factory):
    admin = make_admin(make_client, session_factory)
    make_player(make_client)
    mario = ids_by_name(admin)["mario"]
    assert admin.put(f"/api/admin/users/{mario}/role", json={"role": "admin"}).status_code == 422
    assert admin.put(f"/api/admin/users/{mario}/role", json={"role": "boss"}).status_code == 422
    assert admin.put("/api/admin/users/999/role", json={"role": "judge"}).status_code == 404


def test_a_new_judge_can_create_races_right_away(make_client, session_factory):
    admin = make_admin(make_client, session_factory)
    judge = make_player(make_client)
    cid = admin.post("/api/championships", json={"name": "Estate"}).json()["id"]
    assert judge.post(f"/api/championships/{cid}/races").status_code == 403
    mario = ids_by_name(admin)["mario"]
    admin.put(f"/api/admin/users/{mario}/role", json={"role": "judge"})
    assert judge.post(f"/api/championships/{cid}/races").status_code == 201
