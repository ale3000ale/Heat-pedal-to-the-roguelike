"""Test predisposti dei comandi DB; esecuzione affidata alla CI."""
import random
from datetime import datetime, timezone

import pytest
from sqlalchemy import select

from app.db.models import Championship, Deck, DraftPreparation, Pilot, Race, RaceResult
from app.schemas.draft.draft_state import DraftState
from app.services.cards.cards import CardEntry, dump_cards, parse_cards
from app.services.draft.draft_commands import begin_picking, choose_card, confirm_attendance, move_draft_card
from app.services.draft.draft_preparation import open_preparation
from app.services.draft.draft_transaction import cancel_preparation
from app.services.draft.draft_transitions import DraftTurnPermissionError
from tests.test_draft_preparation import seed


def concluded_race(db, cid, pid):
    """Gara chiusa con risultato: rende la draft successiva non di prima gara."""
    race = Race(championship_id=cid, number=1, date=datetime.now(timezone.utc),
                review_closed_at=datetime.now(timezone.utc))
    db.add(race)
    db.flush()
    db.add(RaceResult(race_id=race.id, pilot_id=pid, position=1))
    db.commit()


def test_reserve_choose_return_move_and_cancel(session_factory):
    cid, judge, _, player, pid = seed(session_factory)
    with session_factory() as db:
        concluded_race(db, cid, pid)
        pool_id = db.get(Championship, cid).pool_deck_id
        db.get(Deck, pool_id).cards = dump_cards([CardEntry(name="Turbo", path="cards/t.webp", copies=5)])
        db.commit()
        row = open_preparation(db, cid, judge)
        key = row.id
        row = confirm_attendance(db, key, judge, row.version)
        assert row.phase == "order"
        row = begin_picking(db, key, judge, row.version, rng=random.Random(3))
        assert sum(c.copies for c in parse_cards(db.get(Deck, pool_id).cards)) == 1
        version = row.version
        with pytest.raises(DraftTurnPermissionError):
            choose_card(db, key, judge, version, 1)
        row = choose_card(db, key, player, version, 1)
        assert row.phase == "decks"
        assert sum(c.copies for c in parse_cards(db.get(Deck, pool_id).cards)) == 4
        pilot = db.get(Pilot, pid)
        inventory_id, game_id = pilot.inventory_deck_id, pilot.game_deck_id
        assert sum(c.copies for c in parse_cards(db.get(Deck, inventory_id).cards)) == 1
        row = move_draft_card(db, key, player, row.version, pid, "cards/t.webp", True)
        assert parse_cards(db.get(Deck, inventory_id).cards) == []
        assert sum(c.copies for c in parse_cards(db.get(Deck, game_id).cards)) == 1
        assert len(db.scalars(select(Race)).all()) == 1
        cancel_preparation(db, key, judge, row.version)
        assert db.get(DraftPreparation, key) is None
        assert sum(c.copies for c in parse_cards(db.get(Deck, pool_id).cards)) == 5
        assert parse_cards(db.get(Deck, inventory_id).cards) == []
        assert parse_cards(db.get(Deck, game_id).cards) == []


def test_first_race_reserves_table_and_returns_leftovers(session_factory):
    cid, judge, _, player, pid = seed(session_factory)
    with session_factory() as db:
        pool_id = db.get(Championship, cid).pool_deck_id
        db.get(Deck, pool_id).cards = dump_cards([CardEntry(name="Turbo", path="cards/t.webp", copies=9)])
        db.commit()
        row = open_preparation(db, cid, judge)
        key = row.id
        row = confirm_attendance(db, key, judge, row.version)
        assert row.phase == "order"
        row = begin_picking(db, key, judge, row.version, rng=random.Random(3))
        state = DraftState.model_validate_json(row.state_json)
        assert state.phase == "picking" and len(state.row) == 5
        assert sum(c.copies for c in parse_cards(db.get(Deck, pool_id).cards)) == 4
        for _ in range(4):
            state = DraftState.model_validate_json(row.state_json)
            row = choose_card(db, key, player, row.version, state.row[0], rng=random.Random(5))
        state = DraftState.model_validate_json(row.state_json)
        assert state.phase == "decks" and state.row == [] and len(state.picks) == 4
        assert sum(c.copies for c in parse_cards(db.get(Deck, pool_id).cards)) == 5
        pilot = db.get(Pilot, pid)
        assert sum(c.copies for c in parse_cards(db.get(Deck, pilot.inventory_deck_id).cards)) == 4
        assert db.scalar(select(Race)) is None


def test_insufficient_pool_goes_to_decks_without_reservation(session_factory):
    cid, judge, _, _, _ = seed(session_factory)
    with session_factory() as db:
        row = open_preparation(db, cid, judge)
        row = confirm_attendance(db, row.id, judge, row.version)
        state = DraftState.model_validate_json(row.state_json)
        assert state.phase == "decks"
        assert state.order == [] and state.cards == []
        assert db.scalar(select(Race)) is None
