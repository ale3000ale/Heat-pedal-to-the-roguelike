"""Test HTTP predisposti su app isolata; esecuzione affidata alla CI."""
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.deps import get_current_user
from app.api.draft.draft import router
from app.db.models import User
from app.db.session import get_db
from tests.test_draft_preparation import seed


def api_client(factory, actor_id=None):
    """Client con SQLite temporaneo e identita esplicita opzionale."""
    app = FastAPI()
    app.include_router(router, prefix="/api")
    def database():
        with factory() as db:
            yield db
    app.dependency_overrides[get_db] = database
    if actor_id is not None:
        def actor():
            with factory() as db:
                return db.get(User, actor_id)
        app.dependency_overrides[get_current_user] = actor
    return TestClient(app)


def test_authentication_and_role(session_factory):
    cid, _, _, player, _ = seed(session_factory)
    with api_client(session_factory) as client:
        assert client.get("/api/drafts").status_code == 401
    with api_client(session_factory, player) as client:
        assert client.post(f"/api/championships/{cid}/draft").status_code == 403


def test_open_validate_cancel_and_recover(session_factory):
    cid, judge, _, _, pid = seed(session_factory)
    with api_client(session_factory, judge) as client:
        response = client.post(f"/api/championships/{cid}/draft")
        assert response.status_code == 201
        state = response.json()
        key = state["id"]
        assert "snapshot_json" not in state
        assert client.get("/api/drafts").json()[0]["id"] == key
        invalid = client.post(f"/api/drafts/{key}/attendance", json={
            "version": True, "pilot_id": pid, "present": False})
        assert invalid.status_code == 422
        assert client.post(f"/api/drafts/{key}/cancel", json={"version": state["version"]}).status_code == 204
        assert client.get("/api/drafts").json() == []
        assert client.get(f"/api/drafts/{key}").status_code == 404


def test_owner_recovers_and_ready_creates_first_race(session_factory):
    cid, judge, _, player, pid = seed(session_factory)
    with api_client(session_factory, judge) as creator:
        initial = creator.post(f"/api/championships/{cid}/draft").json()
        key = initial["id"]
        response = creator.post(f"/api/drafts/{key}/attendance/confirm", json={"version": initial["version"]})
        assert response.status_code == 200 and response.json()["phase"] == "decks"
    with api_client(session_factory, player) as owner:
        current = owner.get("/api/drafts").json()[0]
        response = owner.post(f"/api/drafts/{key}/ready", json={
            "version": current["version"], "pilot_id": pid, "ready": True})
        assert response.status_code == 200
        assert response.json()["preparation"] is None
        assert response.json()["race_id"] is not None
        assert owner.get("/api/drafts").json() == []
