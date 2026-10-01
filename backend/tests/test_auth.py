from datetime import timedelta

from fastapi import FastAPI
from sqlalchemy import func, select, update

from app.api.auth import router as auth_router
from app.api.deps import AdminUser
from app.config import SESSION_COOKIE_NAME
from app.db.models import Session, User
from app.security import hash_password
from app.services.sessions import _now, purge_expired

PASSWORD = "password123"


def register(client, username="mario", password=PASSWORD):
    return client.post(
        "/api/auth/register", json={"username": username, "password": password}
    )


def login(client, username="mario", password=PASSWORD):
    return client.post(
        "/api/auth/login", json={"username": username, "password": password}
    )


def count_sessions(session_factory):
    with session_factory() as db:
        return db.scalar(select(func.count()).select_from(Session))


def test_register_creates_player_and_logs_in(client):
    r = register(client)
    assert r.status_code == 201
    assert r.json()["username"] == "mario"
    assert r.json()["role"] == "player"
    assert "password" not in r.json()
    assert SESSION_COOKIE_NAME in client.cookies
    me = client.get("/api/auth/me")
    assert me.status_code == 200
    assert me.json()["username"] == "mario"


def test_register_cannot_choose_role(client):
    r = client.post(
        "/api/auth/register",
        json={"username": "furbo", "password": PASSWORD, "role": "admin"},
    )
    assert r.status_code == 201
    assert r.json()["role"] == "player"


def test_register_duplicate_is_case_insensitive(client):
    assert register(client, "mario").status_code == 201
    assert register(client, "MARIO").status_code == 409
    assert register(client, "  Mario ").status_code == 409


def test_register_rejects_invalid_input(client):
    assert register(client, "ab").status_code == 422
    assert register(client, "mario rossi").status_code == 422
    assert register(client, "mario", "corta").status_code == 422


def test_password_is_stored_hashed(client, session_factory):
    register(client)
    with session_factory() as db:
        user = db.scalar(select(User).where(User.username == "mario"))
        assert user.password != PASSWORD
        assert user.password.startswith("$argon2")


def test_login_success_and_case_insensitive(client):
    register(client)
    client.cookies.clear()
    r = login(client, "MARIO")
    assert r.status_code == 200
    assert SESSION_COOKIE_NAME in client.cookies


def test_login_wrong_password_and_unknown_user_look_the_same(client):
    register(client)
    client.cookies.clear()
    wrong = login(client, "mario", "sbagliata1")
    unknown = login(client, "nessuno", PASSWORD)
    assert wrong.status_code == unknown.status_code == 401
    assert wrong.json() == unknown.json()
    assert SESSION_COOKIE_NAME not in client.cookies


def test_me_requires_session(client):
    assert client.get("/api/auth/me").status_code == 401


def test_cookie_is_httponly(client):
    r = register(client)
    header = r.headers["set-cookie"].lower()
    assert "httponly" in header
    assert "samesite=lax" in header


def test_session_token_is_not_stored_in_clear(client, session_factory):
    register(client)
    token = client.cookies.get(SESSION_COOKIE_NAME)
    with session_factory() as db:
        stored = db.scalar(select(Session.token_hash))
    assert stored != token
    assert len(stored) == 64


def test_logout_deletes_session_row(client, session_factory):
    register(client)
    assert count_sessions(session_factory) == 1
    assert client.post("/api/auth/logout").status_code == 204
    assert count_sessions(session_factory) == 0
    assert client.get("/api/auth/me").status_code == 401


def test_logout_without_session_is_ok(client):
    assert client.post("/api/auth/logout").status_code == 204


def test_old_token_stops_working_after_logout(client):
    register(client)
    token = client.cookies.get(SESSION_COOKIE_NAME)
    client.post("/api/auth/logout")
    client.cookies.set(SESSION_COOKIE_NAME, token)
    assert client.get("/api/auth/me").status_code == 401


def test_expired_session_is_rejected_and_purged(client, session_factory):
    register(client)
    with session_factory() as db:
        db.execute(update(Session).values(expires_at=_now() - timedelta(minutes=1)))
        db.commit()
    assert client.get("/api/auth/me").status_code == 401
    with session_factory() as db:
        assert purge_expired(db) == 1
    assert count_sessions(session_factory) == 0


def test_deleting_user_deletes_sessions(client, session_factory):
    register(client)
    with session_factory() as db:
        db.delete(db.scalar(select(User)))
        db.commit()
    assert count_sessions(session_factory) == 0


def test_admin_route_forbidden_for_player_allowed_for_admin(make_client, session_factory):
    admin_app = FastAPI()
    admin_app.include_router(auth_router, prefix="/api/auth")

    @admin_app.get("/admin-only")
    def admin_only(user: AdminUser):
        return {"ok": True}

    c = make_client(admin_app)
    assert c.get("/admin-only").status_code == 401

    register(c, "giocatore")
    assert c.get("/admin-only").status_code == 403
    c.post("/api/auth/logout")

    with session_factory() as db:
        db.add(User(username="capo", password=hash_password(PASSWORD), role="admin"))
        db.commit()
    login(c, "capo")
    assert c.get("/admin-only").status_code == 200