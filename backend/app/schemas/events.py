"""Contratto degli eventi persistenti; non espone un endpoint HTTP."""
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, JsonValue

EventType = Literal[
    "card.gifted", "card.gift_undone", "card.played", "card.play_undone",
    "cards.changed", "race.started", "race.review_changed",
    "race.results_changed", "standings.changed",
]


class EventCreate(BaseModel):
    """Valida tipo, riferimenti positivi e payload JSON prima della persistenza.

    recipient_user_id limita un evento privato al proprietario; None indica un
    evento di campionato. Il servizio di lettura deve verificare gli accessi:
    questo schema non autorizza l'utente e non pubblica alcun dato.
    Campi sconosciuti, identificativi non interi e payload non JSON generano
    ValidationError. I riferimenti devono essere verificati dal servizio.
    """

    model_config = ConfigDict(extra="forbid", strict=True)

    type: EventType
    championship_id: int = Field(gt=0)
    pilot_id: int | None = Field(default=None, gt=0)
    recipient_user_id: int | None = Field(default=None, gt=0)
    payload: dict[str, JsonValue] = Field(default_factory=dict)
