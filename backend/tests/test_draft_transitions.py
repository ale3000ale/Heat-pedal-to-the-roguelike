"""Test predisposti delle transizioni; nessuna esecuzione locale attestata."""
import random

import pytest
from pydantic import ValidationError

from app.schemas.draft.draft_state import DraftParticipant, DraftState
from app.services.cards.cards import CardEntry
from app.services.draft.draft_transitions import (
    DraftTransitionError, DraftTurnPermissionError, advance_attendance, all_ready,
    choose, preview, reorder, set_ready, start_picking,
)


def attendance(first=True):
    """Nuovo stato indipendente con due presenti e un assente."""
    return DraftState(format_version=1, phase="attendance", first_race=first,
        participants=[DraftParticipant(pilot_id=1, user_id=10, name="Uno", present=True),
                      DraftParticipant(pilot_id=2, user_id=20, name="Due", present=True),
                      DraftParticipant(pilot_id=3, user_id=30, name="Assente", present=False)],
        order=[], cards=[], picks=[], preview_slot_id=None, ready=[])


def pool(copies=8):
    return [CardEntry(name="Turbo", path="cards/t.webp", copies=copies)]


def picking():
    ordered = advance_attendance(attendance(), pool(), None, shuffle=lambda values: None)
    return start_picking(ordered, pool(), rng=random.Random(7))[0]


def test_first_race_and_insufficient_pool_paths():
    original = attendance()
    ordered = advance_attendance(original, pool(), None, shuffle=list.reverse)
    assert ordered.order == [2, 1]
    assert original.phase == "attendance"
    decks = advance_attendance(original, pool(4), None)
    assert decks.phase == "decks" and decks.order == []


def test_reverse_previous_result_and_reorder():
    ordered = advance_attendance(attendance(False), pool(), [1, 2])
    assert ordered.order == [2, 1]
    assert reorder(ordered, [1, 2]).order == [1, 2]
    with pytest.raises(ValidationError):
        reorder(ordered, [1, 3])


def test_duplicate_copies_and_input_preservation():
    original = pool()
    ordered = advance_attendance(attendance(), original, None)
    state, remaining = start_picking(ordered, original, rng=random.Random(2))
    assert len(state.cards) == 5
    assert len({slot.slot_id for slot in state.cards}) == 5
    assert sum(card.copies for card in remaining) == 3
    assert original[0].copies == 8 and ordered.phase == "order"


def test_turn_preview_choices_and_final_phase():
    original = picking()
    with pytest.raises(DraftTurnPermissionError):
        preview(original, 20, 1)
    enlarged = preview(original, 10, 1)
    assert enlarged.preview_slot_id == 1 and original.preview_slot_id is None
    assert preview(enlarged, 10, None).preview_slot_id is None
    first, pilot, card = choose(enlarged, 10, 1)
    assert pilot == 1 and card.copies == 1 and first.preview_slot_id is None
    with pytest.raises(DraftTransitionError):
        choose(first, 20, 1)
    done, pilot, _ = choose(first, 20, 2)
    assert pilot == 2 and done.phase == "decks"
    assert len([slot for slot in done.cards if slot.chosen_by is None]) == 3


def test_two_pilots_ready_and_revocation_at_first_race():
    state = advance_attendance(attendance(), pool(4), None)
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


def test_same_owner_chooses_and_confirms_each_pilot():
    source = attendance()
    source.participants[1].user_id = 10
    ordered = advance_attendance(source, pool(), None, shuffle=lambda values: None)
    state, _ = start_picking(ordered, pool(), rng=random.Random(1))
    state, pilot, _ = choose(state, 10, 1)
    assert pilot == 1
    state, pilot, _ = choose(state, 10, 2)
    assert pilot == 2
    state = set_ready(state, 10, 1, True, [])
    assert not all_ready(state)
    assert all_ready(set_ready(state, 10, 2, True, []))
