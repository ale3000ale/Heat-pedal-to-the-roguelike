"""Test HTTP predisposti su app isolata; esecuzione affidata alla CI."""
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import func, select

from app.api.deps import get_current_user
from app.api.draft.draft import router
from app.db.models import Championship, Deck, Race, User
from app.db.session import get_db
from app.services.cards.cards import CardEntry, dump_cards, parse_cards
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


def test_first_race_four_picks_and_ready_creates_race(session_factory):
    cid, judge, _, player, pid = seed(session_factory)
    with session_factory() as db:
        pool_id = db.get(Championship, cid).pool_deck_id
        db.get(Deck, pool_id).cards = dump_cards([
            CardEntry(name="Turbo", path="cards/turbo.webp", copies=9)])
        db.commit()
    with api_client(session_factory, judge) as creator:
        opened = creator.post(f"/api/championships/{cid}/draft").json()
        key = opened["id"]
        assert opened["first_race"] is True
        confirmed = creator.post(f"/api/drafts/{key}/attendance/confirm",
                                 json={"version": opened["version"]})
        assert confirmed.status_code == 200 and confirmed.json()["phase"] == "order"
        started = creator.post(f"/api/drafts/{key}/start",
                               json={"version": confirmed.json()["version"]})
        state = started.json()
        assert started.status_code == 200 and state["phase"] == "picking"
        assert state["current_pilot_id"] == pid
        assert len([card for card in state["cards"] if card["chosen_by"] is None]) == 5
    with api_client(session_factory, player) as owner:
        state = owner.get(f"/api/drafts/{key}").json()
        for index in range(4):
            slot = next(card for card in state["cards"] if card["chosen_by"] is None)
            response = owner.post(f"/api/drafts/{key}/choice",
                                  json={"version": state["version"], "slot_id": slot["slot_id"]})
            assert response.status_code == 200
            state = response.json()
            expected_row = 5 if index < 3 else 0
            assert len([card for card in state["cards"] if card["chosen_by"] is None]) == expected_row
        assert state["phase"] == "decks" and len(state["picks"]) == 4
        assert len(state["cards"]) == 4
        assert all(card["chosen_by"] is not None for card in state["cards"])
        deck_state = owner.get(f"/api/drafts/{key}/pilots/{pid}/deck").json()
        assert sum(card["copies"] for card in deck_state["inventory"]) == 4
        ready = owner.post(f"/api/drafts/{key}/ready",
                           json={"version": state["version"], "pilot_id": pid, "ready": True})
        assert ready.status_code == 200 and ready.json()["race_id"] is not None
    with session_factory() as db:
        pool_id = db.get(Championship, cid).pool_deck_id
        assert sum(card.copies for card in parse_cards(db.get(Deck, pool_id).cards)) == 5
        assert db.scalar(select(func.count()).select_from(Race)) == 1
