import pytest
from sqlalchemy.orm.exc import StaleDataError

from app.db.models.deck import Deck
from app.db.models.pilot import Pilot
from app.services import pilot_deck
from app.services.cards import CardEntry, dump_cards

from .test_pilots_api import create_pilot, register


def test_concurrent_deck_edit_is_detected(session_factory):
    with session_factory() as first, session_factory() as second:
        deck = Deck(cards="[]")
        first.add(deck)
        first.commit()
        deck_id = deck.id

        seen_by_first = first.get(Deck, deck_id)
        seen_by_second = second.get(Deck, deck_id)
        seen_by_first.cards = "a"
        first.commit()

        seen_by_second.cards = "b"
        with pytest.raises(StaleDataError):
            second.commit()


def test_deck_version_increases_on_each_change(session_factory):
    with session_factory() as db:
        deck = Deck(cards="[]")
        db.add(deck)
        db.commit()
        before = deck.version
        deck.cards = "x"
        db.commit()
        assert deck.version == before + 1


def test_move_retries_after_a_conflict(client, session_factory, monkeypatch):
    register(client)
    pilot_id = create_pilot(client).json()["id"]
    path = "cards/starter/velocita-1.webp"
    real_commit = pilot_deck.Session.commit
    state = {"conflicts": 1}

    def flaky_commit(self):
        if state["conflicts"] > 0:
            state["conflicts"] -= 1
            raise StaleDataError
        return real_commit(self)

    monkeypatch.setattr(pilot_deck.Session, "commit", flaky_commit)
    r = client.post(f"/api/pilots/{pilot_id}/deck/add", json={"path": path})
    assert r.status_code == 200
    monkeypatch.undo()
    saved = client.get(f"/api/pilots/{pilot_id}").json()
    assert [c["copies"] for c in saved["game_deck"]] == [1]
    assert saved["inventory"][0]["copies"] == 2


def test_move_gives_409_when_conflicts_never_stop(client, monkeypatch):
    register(client)
    pilot_id = create_pilot(client).json()["id"]
    path = "cards/starter/velocita-1.webp"
    real_commit = pilot_deck.Session.commit

    def always_stale(self):
        raise StaleDataError

    monkeypatch.setattr(pilot_deck.Session, "commit", always_stale)
    r = client.post(f"/api/pilots/{pilot_id}/deck/add", json={"path": path})
    monkeypatch.setattr(pilot_deck.Session, "commit", real_commit)
    assert r.status_code == 409
    saved = client.get(f"/api/pilots/{pilot_id}").json()
    assert saved["game_deck"] == []
    assert saved["inventory"][0]["copies"] == 3
