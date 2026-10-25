"""Contratto degli eventi persistenti; non espone un endpoint HTTP."""
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, JsonValue, model_validator

EventType = Literal[
    "card.gifted", "card.gift_undone", "card.played", "card.play_undone",
    "cards.changed", "race.started", "race.review_changed",
    "race.results_changed", "standings.changed", "championship.pilots_changed",
    "draft.changed",
]


class EventCreate(BaseModel):
    """Valida evento e riferimenti; autorizzazioni e commit spettano ai servizi.

    recipient_user_id limita gli eventi privati al destinatario. Gli altri
    eventi conservano il contratto esistente. Rifiuta extra e tipi coercibili.
    """
    model_config = ConfigDict(extra="forbid", strict=True)
    type: EventType
    championship_id: int = Field(gt=0)
    pilot_id: int | None = Field(default=None, gt=0)
    recipient_user_id: int | None = Field(default=None, gt=0)
    payload: dict[str, JsonValue] = Field(default_factory=dict)

    @model_validator(mode="after")
    def enrollment_signal_only(self) -> "EventCreate":
        """Il segnale iscrizioni resta pubblico e privo di dati aggiuntivi."""
        if self.type == "championship.pilots_changed" and (
            self.pilot_id is not None or self.recipient_user_id is not None or self.payload
        ):
            raise ValueError("Il segnale iscrizioni deve avere riferimenti nulli e payload vuoto")
        return self

    @model_validator(mode="after")
    def draft_signal_only(self) -> "EventCreate":
        """La draft ammette solo un destinatario privato e l'ID della preparazione."""
        if self.type == "draft.changed":
            key = self.payload.get("preparation_id")
            if (self.recipient_user_id is None or self.pilot_id is not None
                or set(self.payload) != {"preparation_id"}
                or type(key) is not int or key < 1):
                raise ValueError("Segnale draft privato non valido")
        return self
