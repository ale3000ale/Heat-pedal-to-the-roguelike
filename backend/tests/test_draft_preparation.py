"""Apertura e presenze sul solo database temporaneo dei test."""
import pytest
from sqlalchemy import select

from app.db.models import Championship, ChampionshipPilot, Deck, DraftPreparation, Pilot, Race, User
from app.schemas.draft.draft_snapshot import DraftSnapshot
from app.schemas.draft.draft_state import DraftState
from app.services.draft.draft_preparation import (
    DraftPermissionError, DraftPreparationError, open_preparation, set_attendance,
)


def seed(factory):
    """Prepara un campionato e un pilota senza usare il database reale."""
    with factory() as db:
        judge = User(username="judge", password="fixture", role="judge")
        other = User(username="other", password="fixture", role="judge")
        player = User(username="player", password="fixture", role="player")
        decks = [Deck(cards="[]") for _ in range(4)]
        db.add_all([judge, other, player, *decks])
        db.flush()
        championship = Championship(name="Draft", name_key="draft", pool_deck_id=decks[0].id)
        pilot = Pilot(name="Pilota", name_key="pilota", user_id=player.id,
            inventory_deck_id=decks[1].id, game_deck_id=decks[2].id, sponsor_inventory_deck_id=decks[3].id)
        db.add_all([championship, pilot])
        db.flush()
        db.add(ChampionshipPilot(championship_id=championship.id, pilot_id=pilot.id))
        db.commit()
        return championship.id, judge.id, other.id, player.id, pilot.id


def test_open_captures_originals_without_creating_race(session_factory):
    cid, judge, _, _, pid = seed(session_factory)
    with session_factory() as db:
        row = open_preparation(db, cid, judge)
        state = DraftState.model_validate_json(row.state_json)
        snapshot = DraftSnapshot.model_validate_json(row.snapshot_json)
        assert state.first_race
        assert state.participants[0].pilot_id == pid
        assert state.participants[0].present
        assert len(snapshot.decks) == 3
        assert db.scalar(select(Race)) is None


def test_exclude_include_and_stale_version(session_factory):
    cid, judge, _, _, pid = seed(session_factory)
    with session_factory() as db:
        row = open_preparation(db, cid, judge)
        key = row.id
        original_snapshot = row.snapshot_json
        row = set_attendance(db, key, judge, 1, pid, False)
        assert row.version == 2
        assert not DraftState.model_validate_json(row.state_json).participants[0].present
        with pytest.raises(DraftPreparationError):
            set_attendance(db, key, judge, 1, pid, True)
        row = set_attendance(db, key, judge, 2, pid, True)
        assert DraftState.model_validate_json(row.state_json).participants[0].present
        assert row.snapshot_json == original_snapshot


def test_player_cannot_open_and_other_judge_cannot_change(session_factory):
    cid, judge, other, player, pid = seed(session_factory)
    with session_factory() as db:
        with pytest.raises(DraftPermissionError):
            open_preparation(db, cid, player)
        assert db.scalar(select(DraftPreparation)) is None
        row = open_preparation(db, cid, judge)
        with pytest.raises(DraftPermissionError):
            set_attendance(db, row.id, other, 1, pid, False)


def test_duplicate_open_is_rejected(session_factory):
    cid, judge, _, _, _ = seed(session_factory)
    with session_factory() as db:
        first = open_preparation(db, cid, judge)
        key = first.id
        with pytest.raises(DraftPreparationError):
            open_preparation(db, cid, judge)
        assert db.scalar(select(DraftPreparation.id)) == key
