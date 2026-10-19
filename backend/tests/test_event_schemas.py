"""Test del contratto degli eventi, senza scritture sul database."""
import pytest
from pydantic import ValidationError

from app.schemas.events import EventCreate


def test_valid_private_event():
    event = EventCreate(
        type="card.gifted", championship_id=1, pilot_id=2,
        recipient_user_id=3, payload={"gift_id": 4},
    )
    assert event.recipient_user_id == 3
    assert event.model_dump()["payload"] == {"gift_id": 4}


def test_payload_defaults_are_independent():
    first = EventCreate(type="standings.changed", championship_id=1)
    second = EventCreate(type="standings.changed", championship_id=1)
    first.payload["changed"] = True
    assert second.payload == {}
    assert second.recipient_user_id is None


@pytest.mark.parametrize("changes", [
    {"type": "unknown"}, {"championship_id": 0},
    {"championship_id": "1"}, {"championship_id": True},
    {"pilot_id": -1}, {"recipient_user_id": 0},
    {"unexpected": "value"}, {"payload": {"invalid": object()}},
])
def test_invalid_event_is_rejected(changes):
    values = {"type": "race.started", "championship_id": 1}
    values.update(changes)
    with pytest.raises(ValidationError):
        EventCreate(**values)
