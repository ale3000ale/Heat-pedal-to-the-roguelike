"""Regressioni: l'idoneita del mazzo si verifica dopo la modifica, non alle presenze."""
import random
from datetime import datetime, timezone

import pytest
from sqlalchemy import func, select

from app.db.models import Championship, Deck, DraftPreparation, Pilot, Race, RaceResult
from app.schemas.draft.draft_state import DraftState
from app.services.cards.cards import CardEntry, dump_cards, parse_cards
from app.services.draft.draft_commands import begin_picking, choose_card, confirm_attendance, move_draft_card
from app.services.draft.draft_completion import ready_pilot
from app.services.draft.draft_preparation import DraftPreparationError, open_preparation, set_attendance
from app.services.draft.draft_transitions import DraftTransitionError
from tests.test_draft_api import api_client
from tests.test_draft_preparation import seed


def following_race(factory, game_count, pool_count):
    """Prepara solo SQLite di prova: gara con risultati e revisione chiusa, mazzo incompleto.

    Parametri: factory temporanea e conteggi di copie. Ritorna gli ID della fixture
    esistente; nessun servizio di creazione gara o database reale viene usato.
    """
    ids = seed(factory)
    cid, _, _, _, pid = ids
    with factory() as db:
        pilot = db.get(Pilot, pid)
        game = [] if game_count == 0 else [CardEntry(name="Turbo", path="cards/t.webp", copies=game_count)]
        pool = [] if pool_count == 0 else [CardEntry(name="Turbo", path="cards/t.webp", copies=pool_count)]
        db.get(Deck, pilot.game_deck_id).cards = dump_cards(game)
        db.get(Deck, pilot.inventory_deck_id).cards = dump_cards([
            CardEntry(name="Turbo", path="cards/t.webp", copies=15 - game_count)
        ])
        db.get(Deck, db.get(Championship, cid).pool_deck_id).cards = dump_cards(pool)
        now = datetime.now(timezone.utc)
        previous = Race(championship_id=cid, number=1, date=now, review_closed_at=now)
        db.add(previous)
        db.flush()
        db.add(RaceResult(race_id=previous.id, pilot_id=pid, position=1, points=9, sponsor_points=0))
        db.commit()
    return ids


def race_count(db, championship_id):
    """Conta le gare del solo campionato della fixture, senza modificarle."""
    return db.scalar(select(func.count()).select_from(Race).where(Race.championship_id == championship_id))


@pytest.mark.parametrize("game_count", [0, 14])
@pytest.mark.parametrize("pool_count, expected_phase", [(0, "decks"), (4, "order")])
def test_following_race_attendance_allows_incomplete_game_deck(
    session_factory, game_count, pool_count, expected_phase
):
    cid, judge, _, _, pid = following_race(session_factory, game_count, pool_count)
    with session_factory() as db:
        row = open_preparation(db, cid, judge)
        assert not DraftState.model_validate_json(row.state_json).first_race
        pilot = db.get(Pilot, pid)
        game_id, inventory_id = pilot.game_deck_id, pilot.inventory_deck_id
        pool_id = db.get(Championship, cid).pool_deck_id
        originals = {key: db.get(Deck, key).cards for key in (game_id, inventory_id, pool_id)}
        row = confirm_attendance(db, row.id, judge, row.version)
        state = DraftState.model_validate_json(row.state_json)
        assert row.phase == state.phase == expected_phase
        assert state.ready == []
        assert {key: db.get(Deck, key).cards for key in originals} == originals
        assert race_count(db, cid) == 1


@pytest.mark.parametrize("pool_count", [0, 4])
def test_following_race_validates_after_edit_and_creates_only_after_ready(session_factory, pool_count):
    cid, judge, _, player, pid = following_race(session_factory, 14, pool_count)
    with session_factory() as db:
        row = open_preparation(db, cid, judge)
        key = row.id
        row = confirm_attendance(db, key, judge, row.version)
        if pool_count:
            row = begin_picking(db, key, judge, row.version, rng=random.Random(3))
            row = choose_card(db, key, player, row.version, 1)
        assert row.phase == "decks"
        assert race_count(db, cid) == 1
        version = row.version
        with pytest.raises(DraftTransitionError, match="Mazzo non pronto"):
            ready_pilot(db, key, player, version, pid, True)
        saved = db.get(DraftPreparation, key)
        assert saved.version == version
        assert DraftState.model_validate_json(saved.state_json).ready == []
        assert race_count(db, cid) == 1
        row = move_draft_card(db, key, player, saved.version, pid, "cards/t.webp", True)
        pilot = db.get(Pilot, pid)
        assert sum(card.copies for card in parse_cards(db.get(Deck, pilot.game_deck_id).cards)) == 15
        assert race_count(db, cid) == 1
        result = ready_pilot(db, key, player, row.version, pid, True)
        assert result.preparation_id is None and result.race_id is not None
        assert db.get(DraftPreparation, key) is None
        assert db.get(Race, result.race_id).number == 2
        assert race_count(db, cid) == 2


@pytest.mark.parametrize("pool_count, expected_phase", [(0, "decks"), (4, "order")])
def test_http_attendance_does_not_reject_fourteen_cards(session_factory, pool_count, expected_phase):
    cid, judge, _, _, _ = following_race(session_factory, 14, pool_count)
    with api_client(session_factory, judge) as client:
        response = client.post(f"/api/championships/{cid}/draft")
        assert response.status_code == 201
        initial = response.json()
        response = client.post(f"/api/drafts/{initial['id']}/attendance/confirm", json={
            "version": initial["version"]
        })
        assert response.status_code == 200
        assert response.json()["phase"] == expected_phase
        assert response.json()["first_race"] is False
    with session_factory() as db:
        assert race_count(db, cid) == 1


def test_attendance_still_requires_a_present_pilot(session_factory):
    cid, judge, _, _, pid = following_race(session_factory, 14, 4)
    with session_factory() as db:
        row = open_preparation(db, cid, judge)
        row = set_attendance(db, row.id, judge, row.version, pid, False)
        key, version = row.id, row.version
        with pytest.raises(DraftPreparationError, match="piloti presenti"):
            confirm_attendance(db, key, judge, version)
        saved = db.get(DraftPreparation, key)
        assert saved.phase == "attendance" and saved.version == version
        assert race_count(db, cid) == 1
