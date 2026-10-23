"""Letture admin: permessi, contenitori separati e assenza di scritture."""
from datetime import datetime, timezone
import pytest
from sqlalchemy import func, select

from app.db.models import EventLog, User
from app.db.models.championship import Championship, ChampionshipPilot
from app.db.models.deck import Deck
from app.db.models.pilot import Pilot
from app.db.models.race import Race
from .test_pilots_api import register, create_pilot, enroll


@pytest.fixture()
def admin_cards(client, session_factory):
    user_id = register(client)
    pilot_id = create_pilot(client).json()["id"]
    enroll(session_factory, pilot_id)
    with session_factory() as db:
        db.get(User, user_id).role = "admin"
        championship_id = db.scalar(select(ChampionshipPilot.championship_id).where(
            ChampionshipPilot.pilot_id == pilot_id
        ))
        db.commit()
    return user_id, pilot_id, championship_id


def url(data):
    _, pilot_id, championship_id = data
    return f"/api/admin/championships/{championship_id}/pilots/{pilot_id}/cards"


def test_anonymous_is_denied(client):
    assert client.get("/api/admin/championships/1/pilots").status_code == 401
    assert client.get("/api/admin/championships/1/pilots/1/cards").status_code == 401


@pytest.mark.parametrize("role", ["player", "judge"])
def test_only_admin_can_read(client, session_factory, admin_cards, role):
    user_id, _, championship_id = admin_cards
    with session_factory() as db:
        db.get(User, user_id).role = role
        db.commit()
    assert client.get(f"/api/admin/championships/{championship_id}/pilots").status_code == 403
    assert client.get(url(admin_cards)).status_code == 403


def test_list_includes_username(client, admin_cards):
    user_id, pilot_id, championship_id = admin_cards
    response = client.get(f"/api/admin/championships/{championship_id}/pilots")
    assert response.status_code == 200
    assert response.json() == [{
        "pilot_id": pilot_id, "name": "Ayrton", "user_id": user_id, "username": "mario",
    }]


def test_five_containers_and_missing_pools(client, admin_cards):
    response = client.get(url(admin_cards))
    assert response.status_code == 200
    body = response.json()
    assert body["read_only"] is False
    assert body["blocked_reason"] is None
    containers = body["containers"]
    assert set(containers) == {
        "game_deck", "modification_inventory", "sponsor_inventory",
        "modification_pool", "sponsor_pool",
    }
    assert containers["game_deck"]["cards"] == []
    assert containers["sponsor_inventory"]["cards"] == []
    inventory = containers["modification_inventory"]
    assert inventory["available"] is True and inventory["version"] >= 1
    assert sum(card["copies"] for card in inventory["cards"]) == 12
    assert all(card["path"].startswith("cards/starter/") for card in inventory["cards"])
    for name in ("modification_pool", "sponsor_pool"):
        assert containers[name] == {"available": False, "id": None, "version": None, "cards": []}
    assert "password" not in response.text


def test_existing_empty_pools_are_not_absent(client, session_factory, admin_cards):
    with session_factory() as db:
        pools = [Deck(cards="[]"), Deck(cards="[]")]
        db.add_all(pools)
        db.flush()
        championship = db.get(Championship, admin_cards[2])
        championship.pool_deck_id, championship.sponsor_pool_deck_id = [pool.id for pool in pools]
        db.commit()
    body = client.get(url(admin_cards)).json()
    for name in ("modification_pool", "sponsor_pool"):
        assert body["containers"][name]["available"] is True
        assert body["containers"][name]["version"] >= 1


def test_wrong_championship_or_pilot_is_not_found(client, admin_cards):
    assert client.get("/api/admin/championships/999/pilots").status_code == 404
    assert client.get(f"/api/admin/championships/{admin_cards[2]}/pilots/999/cards").status_code == 404


def test_hidden_pilot_not_exposed(client, session_factory, admin_cards):
    with session_factory() as db:
        db.get(Pilot, admin_cards[1]).deleted_at = datetime.now(timezone.utc)
        db.commit()
    assert client.get(url(admin_cards)).status_code == 404
    assert client.get(f"/api/admin/championships/{admin_cards[2]}/pilots").json() == []


def test_closed_championship_is_read_only(client, session_factory, admin_cards):
    with session_factory() as db:
        db.get(Championship, admin_cards[2]).is_closed = True
        db.commit()
    body = client.get(url(admin_cards)).json()
    assert body["read_only"] is True
    assert body["blocked_reason"] == "Campionato chiuso"


@pytest.mark.parametrize("review", [False, True])
def test_race_or_review_blocks_future_changes(client, session_factory, admin_cards, review):
    with session_factory() as db:
        db.add(Race(
            championship_id=admin_cards[2], number=1,
            review_started_at=datetime.now(timezone.utc) if review else None,
        ))
        db.commit()
    body = client.get(url(admin_cards)).json()
    assert body["read_only"] is True
    assert body["blocked_reason"] == "Gara o revisione non ancora confermata"


def test_corrupt_cards_are_not_silently_emptied(client, session_factory, admin_cards):
    with session_factory() as db:
        pilot = db.get(Pilot, admin_cards[1])
        db.get(Deck, pilot.inventory_deck_id).cards = "not-json"
        db.commit()
    assert client.get(url(admin_cards)).status_code == 409


def test_reads_do_not_change_decks_or_events(client, session_factory, admin_cards):
    def state():
        with session_factory() as db:
            decks = list(db.execute(select(Deck.id, Deck.cards, Deck.version).order_by(Deck.id)))
            events = db.scalar(select(func.count()).select_from(EventLog))
            return decks, events
    before = state()
    assert client.get(url(admin_cards)).status_code == 200
    assert client.get(f"/api/admin/championships/{admin_cards[2]}/pilots").status_code == 200
    assert state() == before
