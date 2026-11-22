"""Test delle transizioni draft: percorso classico e prima gara a serpentina."""
import random

import pytest
from pydantic import ValidationError

from app.schemas.draft.draft_state import DraftParticipant, DraftState
from app.services.cards.cards import CardEntry
from app.services.draft.draft_order import required_draft_copies, turn_pilot
from app.services.draft.draft_transitions import (
    DraftTransitionError, DraftTurnPermissionError, advance_attendance, all_ready,
    choose, choose_first_race, preview, reorder, set_ready, start_picking,
)


def attendance(first=True):
    """Nuovo stato indipendente con due presenti e un assente."""
    return DraftState(format_version=2, phase="attendance", first_race=first,
        participants=[DraftParticipant(pilot_id=1, user_id=10, name="Uno", present=True),
                      DraftParticipant(pilot_id=2, user_id=20, name="Due", present=True),
                      DraftParticipant(pilot_id=3, user_id=30, name="Assente", present=False)],
        order=[], cards=[], row=[], picks=[], preview_slot_id=None, ready=[])


def pool(copies=8):
    return [CardEntry(name="Turbo", path="cards/t.webp", copies=copies)]


def ordered(first=True):
    """Ordine confermato con la pool minima esatta per il percorso scelto."""
    return advance_attendance(attendance(first), pool(required_draft_copies(2, first)),
                              None if first else [1, 2], shuffle=lambda values: None)


def picking():
    """Scelta classica avviata: cinque copie, nessun tavolo."""
    return start_picking(ordered(False), pool(5), rng=random.Random(7))[0]


def first_race():
    """Prima gara avviata: tavolo da cinque copie e pool da tredici."""
    return start_picking(ordered(True), pool(13), rng=random.Random(7))


def test_state_format_two_only():
    payload = attendance().model_dump()
    payload["format_version"] = 1
    with pytest.raises(ValidationError):
        DraftState.model_validate(payload)


def test_first_race_and_classic_pool_thresholds():
    assert required_draft_copies(2, True) == 13
    assert required_draft_copies(2, False) == 5
    first = ordered(True)
    assert first.phase == "order" and first.order == [1, 2]
    assert advance_attendance(attendance(True), pool(12), None).phase == "decks"
    classic = ordered(False)
    assert classic.phase == "order" and classic.order == [2, 1]
    assert advance_attendance(attendance(False), pool(4), [1, 2]).phase == "decks"


def test_reverse_previous_result_and_reorder():
    ordered_state = advance_attendance(attendance(False), pool(8), [1, 2])
    assert ordered_state.order == [2, 1]
    assert reorder(ordered_state, [1, 2]).order == [1, 2]
    with pytest.raises(ValidationError):
        reorder(ordered_state, [1, 3])


def test_first_race_table_turns_and_pool_reservation():
    state, remaining = first_race()
    assert len(state.row) == 5 and len(state.cards) == 5
    assert sum(card.copies for card in remaining) == 8
    assert [turn_pilot(state.order, made, True) for made in range(8)] == [1, 2, 2, 1, 1, 2, 2, 1]
    with pytest.raises(DraftTurnPermissionError):
        choose_first_race(state, 20, state.row[0], remaining)
    with pytest.raises(DraftTransitionError):
        choose(state, 10, state.row[0])


def test_first_race_four_picks_each_and_pool_return():
    state, remaining = first_race()
    owners = [10, 20, 20, 10, 10, 20, 20, 10]
    pilots = [1, 2, 2, 1, 1, 2, 2, 1]
    for index, (owner, expected) in enumerate(zip(owners, pilots, strict=True)):
        state, pilot, card, remaining = choose_first_race(
            state, owner, state.row[0], remaining, rng=random.Random(index))
        assert pilot == expected and card.copies == 1
        if index < 7:
            assert state.phase == "picking" and len(state.row) == 5
    assert state.phase == "decks" and state.row == [] and len(state.picks) == 8
    assert sum(card.copies for card in remaining) == 5
    assert len([card for card in state.cards if card.chosen_by is None]) == 0


def test_first_race_refill_keeps_table_full_between_rounds():
    state, remaining = first_race()
    state, _, _, remaining = choose_first_race(state, 10, state.row[0], remaining,
                                               rng=random.Random(1))
    assert len(state.row) == 5 and sum(card.copies for card in remaining) == 7
    state, _, _, remaining = choose_first_race(state, 20, state.row[0], remaining,
                                               rng=random.Random(2))
    assert len(state.row) == 5 and sum(card.copies for card in remaining) == 6


def test_classic_single_pick_and_leftovers():
    state, remaining = start_picking(ordered(False), pool(5), rng=random.Random(2))
    assert len(state.cards) == 5 and state.row == []
    assert sum(card.copies for card in remaining) == 0
    state, pilot, card = choose(state, 20, 1)
    assert pilot == 2 and card.copies == 1
    with pytest.raises(DraftTransitionError):
        choose(state, 10, 1)
    done, pilot, _ = choose(state, 10, 2)
    assert pilot == 1 and done.phase == "decks" and len(done.picks) == 2


def test_turn_preview_choices_and_final_phase():
    original = picking()
    with pytest.raises(DraftTurnPermissionError):
        preview(original, 10, 1)
    enlarged = preview(original, 20, 1)
    assert enlarged.preview_slot_id == 1 and original.preview_slot_id is None
    assert preview(enlarged, 20, None).preview_slot_id is None
    first, pilot, card = choose(enlarged, 20, 1)
    assert pilot == 2 and card.copies == 1 and first.preview_slot_id is None
    done, pilot, _ = choose(first, 10, 2)
    assert pilot == 1 and done.phase == "decks"
    assert len([slot for slot in done.cards if slot.chosen_by is None]) == 3


def test_two_pilots_ready_and_revocation_at_first_race():
    state = advance_attendance(attendance(True), pool(4), None)
    assert state.phase == "decks"
    first = set_ready(state, 10, 1, True, [])
    assert not all_ready(first)
    done = set_ready(first, 20, 2, True, [])
    assert all_ready(done)
    assert not all_ready(set_ready(done, 10, 1, False, []))
    assert state.ready == []


def test_later_race_requires_fifteen_only_for_ready():
    state = advance_attendance(attendance(False), pool(4), [1, 2])
    with pytest.raises(DraftTransitionError):
        set_ready(state, 10, 1, True, pool(14))
    ready = set_ready(state, 10, 1, True, pool(15))
    assert set_ready(ready, 10, 1, False, []).ready == []
    with pytest.raises(DraftTurnPermissionError):
        set_ready(state, 20, 1, True, pool(15))
    with pytest.raises(DraftTransitionError):
        set_ready(state, 30, 3, True, pool(15))


def test_same_owner_chooses_each_pilot_until_ready():
    source = attendance(True)
    source.participants[1].user_id = 10
    state, remaining = start_picking(
        advance_attendance(source, pool(13), None, shuffle=lambda values: None),
        pool(13), rng=random.Random(1))
    for index in range(8):
        state, _, _, remaining = choose_first_race(
            state, 10, state.row[0], remaining, rng=random.Random(index))
    assert state.phase == "decks" and len(state.picks) == 8
    state = set_ready(state, 10, 1, True, [])
    assert not all_ready(state)
    assert all_ready(set_ready(state, 10, 2, True, []))
