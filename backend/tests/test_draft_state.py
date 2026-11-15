"""Coerenza dello stato draft senza DB o operazioni di gioco."""
import pytest
from pydantic import ValidationError

from app.schemas.draft.draft_state import DraftState


def payload(phase="picking"):
    """Costruisce uno stato indipendente per ciascun caso."""
    data = dict(format_version=1, phase=phase, first_race=True,
                participants=[dict(pilot_id=1, user_id=7, name="Uno", present=True),
                              dict(pilot_id=2, user_id=7, name="Due", present=True),
                              dict(pilot_id=3, user_id=8, name="Assente", present=False)],
                order=[2, 1], cards=[], picks=[], preview_slot_id=None, ready=[])
    if phase == "attendance":
        data["order"] = []
    if phase == "picking":
        data["cards"] = [dict(slot_id=i, name="Turbo", path="cards/t.webp") for i in range(1, 6)]
    if phase == "decks":
        data["order"] = []
    return data


@pytest.mark.parametrize("phase", ["attendance", "order", "picking", "decks"])
def test_phase_round_trip_and_multiple_pilots_per_owner(phase):
    state = DraftState.model_validate(payload(phase))
    assert DraftState.model_validate_json(state.model_dump_json()) == state


def test_duplicate_card_names_have_distinct_slots():
    state = DraftState.model_validate(payload())
    assert len({card.slot_id for card in state.cards}) == 5
    assert len({card.name for card in state.cards}) == 1


def test_completed_choices_allow_deck_preparation():
    data = payload()
    data["phase"] = "decks"
    data["cards"][0]["chosen_by"] = 2
    data["cards"][1]["chosen_by"] = 1
    data["picks"] = [1, 2]
    data["ready"] = [1, 2]
    assert DraftState.model_validate(data).ready == [1, 2]


@pytest.mark.parametrize("mutation", [
    lambda d: d["participants"].append(dict(d["participants"][0])),
    lambda d: d.update(order=[1, 1]),
    lambda d: d.update(order=[1, 3]),
    lambda d: d["cards"].pop(),
    lambda d: d["cards"][0].update(slot_id=2),
    lambda d: d.update(preview_slot_id=999),
    lambda d: d.update(picks=[999]),
    lambda d: d.update(ready=[1]),
    lambda d: d["cards"][0].update(chosen_by=3),
    lambda d: d.update(phase="decks"),
    lambda d: d.update(format_version=True),
    lambda d: d.update(ignored=True),
])
def test_incoherent_states_are_rejected(mutation):
    data = payload()
    mutation(data)
    with pytest.raises(ValidationError):
        DraftState.model_validate(data)


def test_choice_must_belong_to_current_pilot():
    data = payload()
    data["picks"] = [1]
    data["cards"][0]["chosen_by"] = 1
    with pytest.raises(ValidationError):
        DraftState.model_validate(data)
    data["cards"][0]["chosen_by"] = 2
    assert DraftState.model_validate(data).picks == [1]


def test_absent_pilot_cannot_be_ready():
    data = payload("decks")
    data["ready"] = [3]
    with pytest.raises(ValidationError):
        DraftState.model_validate(data)
