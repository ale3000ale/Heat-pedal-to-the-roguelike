"""Cambio password: DB in memoria dalle fixture, nessun DB reale."""
import hashlib
from datetime import timedelta

import pytest
from sqlalchemy import select, update

from app.config import SESSION_COOKIE_NAME
from app.db.models import Session, User
from app.schemas.accounts.password_change import ChangePasswordRequest
from app.security import verify_password
from app.services.core.event_stream import poll_events
from app.services.accounts.password_changes import PasswordSessionError, change_own_password
from app.services.accounts.sessions import _now

OLD = "old-password-123"
NEW = "new-password-456"
URL = "/api/auth/change-password"


def register(client, username="mario"):
    response = client.post("/api/auth/register", json={"username": username, "password": OLD})
    assert response.status_code == 201
    return response.json()["id"]


def payload(**changes):
    return {"current_password": OLD, "new_password": NEW, "confirm_password": NEW, **changes}


def snapshot(factory):
    with factory() as db:
        return (
            [(row.id, row.password) for row in db.scalars(select(User).order_by(User.id))],
            [(row.token_hash, row.user_id, row.expires_at)
             for row in db.scalars(select(Session).order_by(Session.id))],
        )


@pytest.mark.parametrize("role", ["player", "judge", "admin"])
def test_change_keeps_current_revokes_others_and_preserves_other_users(
    client, make_client, session_factory, role
):
    user_id = register(client)
    token = client.cookies.get(SESSION_COOKIE_NAME)
    other = make_client()
    assert other.post("/api/auth/login", json={"username": "mario", "password": OLD}).status_code == 200
    other_token = other.cookies.get(SESSION_COOKIE_NAME)
    stranger = make_client()
    register(stranger, "luigi")
    before = snapshot(session_factory)
    with session_factory() as db:
        db.execute(update(User).where(User.id == user_id).values(role=role))
        db.commit()
    response = client.post(URL, json=payload())
    assert response.status_code == 204
    assert response.content == b""
    assert "set-cookie" not in response.headers
    assert client.cookies.get(SESSION_COOKIE_NAME) == token
    assert client.get("/api/auth/me").json()["role"] == role
    assert other.get("/api/auth/me").status_code == 401
    assert stranger.get("/api/auth/me").status_code == 200
    assert poll_events(session_factory, other_token, None) is None
    after = snapshot(session_factory)
    current_hash = hashlib.sha256(token.encode()).hexdigest()
    assert [row for row in before[1] if row[0] == current_hash] == [row for row in after[1] if row[0] == current_hash]
    assert len(after[1]) == len(before[1]) - 1
    with session_factory() as db:
        stored = db.get(User, user_id).password
        assert stored not in (OLD, NEW)
        assert verify_password(NEW, stored)
        assert not verify_password(OLD, stored)
    fresh = make_client()
    assert fresh.post("/api/auth/login", json={"username": "mario", "password": OLD}).status_code == 401
    assert fresh.post("/api/auth/login", json={"username": "mario", "password": NEW}).status_code == 200


@pytest.mark.parametrize("changes,code", [
    ({"current_password": "incorrect-password"}, 403),
    ({"confirm_password": "different-password"}, 422),
    ({"new_password": "short", "confirm_password": "short"}, 422),
    ({"new_password": "x" * 129, "confirm_password": "x" * 129}, 422),
    ({"current_password": ""}, 422),
    ({"user_id": 999}, 422),
    ({"new_password": 12345678}, 422),
])
def test_rejections_do_not_change_hash_or_sessions(client, session_factory, changes, code):
    register(client)
    before = snapshot(session_factory)
    response = client.post(URL, json=payload(**changes))
    assert response.status_code == code
    assert snapshot(session_factory) == before
    assert OLD not in response.text
    assert NEW not in response.text
    assert "incorrect-password" not in response.text


def test_unauthenticated_and_expired_are_rejected(client, session_factory):
    assert client.post(URL, json=payload()).status_code == 401
    register(client)
    with session_factory() as db:
        db.execute(update(Session).values(expires_at=_now() - timedelta(seconds=1)))
        db.commit()
    before = snapshot(session_factory)
    assert client.post(URL, json=payload()).status_code == 401
    assert snapshot(session_factory) == before


def test_service_rechecks_revoked_session(client, session_factory):
    user_id = register(client)
    token = client.cookies.get(SESSION_COOKIE_NAME)
    assert client.post("/api/auth/logout").status_code == 204
    before = snapshot(session_factory)
    with session_factory() as db, pytest.raises(PasswordSessionError):
        change_own_password(db, user_id, token, ChangePasswordRequest.model_validate(payload()))
    assert snapshot(session_factory) == before


def test_commit_failure_rolls_back_hash_and_revocation(client, make_client, session_factory, monkeypatch):
    user_id = register(client)
    token = client.cookies.get(SESSION_COOKIE_NAME)
    other = make_client()
    assert other.post("/api/auth/login", json={"username": "mario", "password": OLD}).status_code == 200
    before = snapshot(session_factory)
    def fail_commit():
        raise RuntimeError("simulated commit failure")
    with session_factory() as db:
        monkeypatch.setattr(db, "commit", fail_commit)
        with pytest.raises(RuntimeError, match="simulated commit failure"):
            change_own_password(db, user_id, token, ChangePasswordRequest.model_validate(payload()))
    assert snapshot(session_factory) == before
