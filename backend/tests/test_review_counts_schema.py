import pytest
from pydantic import ValidationError

from app.schemas.review_counts import ReviewCountsRequest


def payload(remaining=1, name="Alettone", pilot_id=1):
    return {"pilots": [{"pilot_id": pilot_id, "cards": [
        {"card_name": name, "remaining": remaining}
    ]}]}


def test_normalized_counts_preserve_zero_and_trim_names():
    request = ReviewCountsRequest.model_validate(payload(0, "  Alettone  "))
    assert request.pilots[0].cards[0].card_name == "Alettone"
    assert request.to_counts() == {(1, "alettone"): 0}


@pytest.mark.parametrize("value", [-1, 1.5, "2", True])
def test_invalid_quantities_are_rejected(value):
    with pytest.raises(ValidationError):
        ReviewCountsRequest.model_validate(payload(value))


@pytest.mark.parametrize("value", [0, -1, "1", True])
def test_invalid_pilot_ids_are_rejected(value):
    with pytest.raises(ValidationError):
        ReviewCountsRequest.model_validate(payload(pilot_id=value))


def test_blank_card_names_are_rejected():
    with pytest.raises(ValidationError):
        ReviewCountsRequest.model_validate(payload(name="   "))


def test_duplicate_cards_are_rejected_after_normalization():
    data = payload()
    data["pilots"][0]["cards"].append({"card_name": " ALETTONE ", "remaining": 0})
    with pytest.raises(ValidationError, match="Carta ripetuta"):
        ReviewCountsRequest.model_validate(data)


def test_duplicate_pilots_are_rejected():
    data = payload()
    data["pilots"].append({"pilot_id": 1, "cards": []})
    with pytest.raises(ValidationError, match="Pilota ripetuto"):
        ReviewCountsRequest.model_validate(data)


def test_same_card_is_allowed_for_different_pilots():
    data = payload()
    data["pilots"].extend(payload(pilot_id=2)["pilots"])
    assert ReviewCountsRequest.model_validate(data).to_counts() == {
        (1, "alettone"): 1, (2, "alettone"): 1
    }


def test_unknown_fields_are_rejected():
    data = payload()
    data["pilots"][0]["cards"][0]["total"] = 99
    with pytest.raises(ValidationError):
        ReviewCountsRequest.model_validate(data)


def test_empty_request_does_not_invent_counts():
    assert ReviewCountsRequest.model_validate({"pilots": []}).to_counts() == {}
