"""Lettura dei mazzi iscritti su SQLite di test, senza attivare il blocco gara."""
import pytest
from sqlalchemy import select

from app.db.models.deck import Deck
from app.db.models.pilot import Pilot
from app.services.cards.cards import CardEntry, dump_cards
from app.services.race.race_deck_readiness import GameDecksNotReadyError
from app.services.race.race_deck_snapshot import require_ready_championship_decks
from tests.test_races_api import setup


def set_counts(factory, pilots, counts):
    """Prepara esplicitamente i soli mazzi da gioco dei piloti di questa prova."""
    with factory() as db:
        for name, count in counts.items():
            pilot = db.get(Pilot, pilots[name])
            cards = [CardEntry(name="Velocita test", path="cards/test.webp", copies=count)] if count else []
            db.get(Deck, pilot.game_deck_id).cards = dump_cards(cards)
        db.commit()


def deck_rows(db):
    return list(db.execute(select(Deck.id, Deck.cards, Deck.version).order_by(Deck.id)))


def test_ready_decks_are_not_modified(make_client, session_factory):
    _, _, cid, pilots = setup(make_client, session_factory, ["Anna", "Beppe"])
    set_counts(session_factory, pilots, {"Anna": 15, "Beppe": 15})
    with session_factory() as db:
        before = deck_rows(db)
        require_ready_championship_decks(db, cid)
        assert deck_rows(db) == before
        assert not db.new and not db.dirty and not db.deleted


@pytest.mark.parametrize("count", [0, 1, 14, 16])
def test_reports_all_unready_pilots(make_client, session_factory, count):
    _, _, cid, pilots = setup(make_client, session_factory, ["Beppe", "Anna", "Carlo"])
    set_counts(session_factory, pilots, {"Anna": count, "Beppe": 14, "Carlo": 15})
    with session_factory() as db:
        before = deck_rows(db)
        with pytest.raises(GameDecksNotReadyError) as error:
            require_ready_championship_decks(db, cid)
        assert [(row.pilot_id, row.count) for row in error.value.unready] == [
            (pilots["Anna"], count), (pilots["Beppe"], 14),
        ]
        assert deck_rows(db) == before


def test_corrupt_json_is_not_zero_and_other_championship_is_ignored(make_client, session_factory):
    admin, _, cid, pilots = setup(make_client, session_factory, ["Anna"])
    other = admin.post("/api/championships", json={"name": "Altro"}).json()["id"]
    with session_factory() as db:
        pilot = db.get(Pilot, pilots["Anna"])
        db.get(Deck, pilot.game_deck_id).cards = "not json"
        db.commit()
    with session_factory() as db:
        require_ready_championship_decks(db, other)
        with pytest.raises(GameDecksNotReadyError) as error:
            require_ready_championship_decks(db, cid)
        assert len(error.value.unready) == 1
        row = error.value.unready[0]
        assert row.count is None and row.reason == "invalid_cards"


def test_no_new_minimum_number_of_entrants(make_client, session_factory):
    _, _, cid, _ = setup(make_client, session_factory, [])
    with session_factory() as db:
        require_ready_championship_decks(db, cid)
