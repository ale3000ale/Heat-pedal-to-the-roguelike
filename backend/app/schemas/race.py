from datetime import datetime

from pydantic import BaseModel, Field


class RaceCreate(BaseModel):
    # Dati facoltativi della nuova gara.
    date: datetime | None = None


class ResultEntry(BaseModel):
    # Un pilota all'arrivo, con i punti sponsor scelti a mano (mai negativi).
    pilot_id: int
    sponsor_points: int = Field(default=0, ge=0)


class ResultsSet(BaseModel):
    # Risultati nell'ordine di arrivo: la posizione è la posizione nell'elenco.
    results: list[ResultEntry] = Field(min_length=1, max_length=12)


class RaceRead(BaseModel):
    id: int
    number: int
    date: datetime | None
    participants: int


class RaceResultRead(BaseModel):
    pilot_id: int
    pilot_name: str
    position: int | None
    points: int
    sponsor_points: int


class RaceDetail(RaceRead):
    results: list[RaceResultRead]


class StandingRead(BaseModel):
    rank: int
    pilot_id: int | None
    pilot_name: str
    points: int
    races_played: int
