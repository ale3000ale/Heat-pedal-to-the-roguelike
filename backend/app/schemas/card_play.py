from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class CardPlayRequest(BaseModel):
    # Giocata di una carta sponsor: pilota e nome della carta nell'inventario.
    pilot_id: int
    card_name: str = Field(min_length=1, max_length=64)


class CardUndoRequest(BaseModel):
    pilot_id: int


class CardPlayRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    card_name: str
    card_path: str
    status: str
    played_at: datetime


class AvailableCardRead(BaseModel):
    name: str
    path: str
    copies_total: int
    copies_available: int


class CardPlayStateRead(BaseModel):
    # Stato delle giocate di un pilota nella gara in corso; in_review indica che la gara
    # è in revisione e non si può più giocare né annullare.
    race_id: int
    pilot_id: int
    plays: list[CardPlayRead]
    available: list[AvailableCardRead]
    undo_remaining: int
    in_review: bool
