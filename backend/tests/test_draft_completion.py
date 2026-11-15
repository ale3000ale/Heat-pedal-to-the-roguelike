"""Test predisposti della conclusione; esecuzione affidata alla CI."""
import pytest
from sqlalchemy import func, select

from app.db.models import ChampionshipPilot, Deck, DraftPreparation, EventLog, Pilot, Race
from app.schemas.draft_state import DraftState
from app.services.draft_commands import confirm_attendance, move_draft_card
from app.services.draft_completion import already_disputed, ready_pilot
from app.services.draft_preparation import DraftPreparationError, open_preparation
from tests.test_draft_preparation import seed


def add_second_pilot(factory, championship_id, owner_id):
    """Aggiunge un secondo presente esplicito ai soli dati SQLite di prova."""
    with factory() as db:
        decks = [Deck(cards="[]") for _ in range(3)]
        db.add_all(decks)
        db.flush()
        pilot = Pilot(name="Secondo", name_key="secondo", user_id=owner_id,
            inventory_deck_id=decks[0].id, game_deck_id=decks[1].id,
            sponsor_inventory_deck_id=decks[2].id)
        db.add(pilot)
        db.flush()
        db.add(ChampionshipPilot(championship_id=championship_id, pilot_id=pilot.id))
        db.commit()
        return pilot.id


def test_two_present_pilots_revoke_and_create_only_at_last_ready(session_factory):
    cid, judge, other, player, pid = seed(session_factory)
    second = add_second_pilot(session_factory, cid, other)
    with session_factory() as db:
        row = open_preparation(db, cid, judge)
        key = row.id
        row = confirm_attendance(db, key, judge, row.version)
        assert ready_pilot(db, key, player, row.version, pid, True).race_id is None
        row = db.get(DraftPreparation, key)
        with pytest.raises(DraftPreparationError):
            move_draft_card(db, key, player, row.version, pid, "cards/t.webp", True)
        row = db.get(DraftPreparation, key)
        assert ready_pilot(db, key, player, row.version, pid, False).race_id is None
        row = db.get(DraftPreparation, key)
        assert ready_pilot(db, key, other, row.version, second, True).race_id is None
        assert db.scalar(select(func.count()).select_from(Race)) == 0
        row = db.get(DraftPreparation, key)
        result = ready_pilot(db, key, player, row.version, pid, True)
        assert result.preparation_id is None and result.race_id is not None
        assert db.get(DraftPreparation, key) is None
        assert db.scalar(select(func.count()).select_from(Race)) == 1
        assert db.get(Race, result.race_id).number == 1
        assert db.scalar(select(func.count()).select_from(EventLog).where(EventLog.type == "race.started")) == 1


def test_same_owner_must_confirm_each_pilot(session_factory):
    cid, judge, _, player, pid = seed(session_factory)
    second = add_second_pilot(session_factory, cid, player)
    with session_factory() as db:
        row = open_preparation(db, cid, judge)
        key = row.id
        row = confirm_attendance(db, key, judge, row.version)
        assert ready_pilot(db, key, player, row.version, pid, True).race_id is None
        row = db.get(DraftPreparation, key)
        assert ready_pilot(db, key, player, row.version, second, True).race_id is not None


def test_terminal_signal_failure_rolls_back_race_and_last_ready(session_factory, monkeypatch):
    from app.services import draft_transaction as transaction
    cid, judge, _, player, pid = seed(session_factory)
    with session_factory() as db:
        row = open_preparation(db, cid, judge)
        row = confirm_attendance(db, row.id, judge, row.version)
        key, version = row.id, row.version
        def fail(*args):
            raise RuntimeError("Errore segnale terminale")
        monkeypatch.setattr(transaction, "signal_draft_changed", fail)
        with pytest.raises(RuntimeError, match="Errore segnale terminale"):
            ready_pilot(db, key, player, version, pid, True)
        saved = db.get(DraftPreparation, key)
        assert saved is not None and saved.version == version
        assert DraftState.model_validate_json(saved.state_json).ready == []
        assert db.scalar(select(func.count()).select_from(Race)) == 0
        assert db.scalar(select(func.count()).select_from(EventLog).where(EventLog.type == "race.started")) == 0


def test_already_disputed_skips_exact_fifteen_and_keeps_results_empty(session_factory):
    cid, judge, _, _, _ = seed(session_factory)
    with session_factory() as db:
        row = open_preparation(db, cid, judge)
        key = row.id
        result = already_disputed(db, key, judge, row.version)
        assert result.race_id is not None
        assert db.get(DraftPreparation, key) is None
        assert db.get(Race, result.race_id).review_closed_at is None
