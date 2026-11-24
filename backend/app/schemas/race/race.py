from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

# Stato di una gara: in corso (senza risultati), in revisione (revisione carte attiva),
# da rivedere (risultati registrati ma revisione non attiva né confermata), chiusa.
RaceStatus = Literal["in_progress", "in_review", "to_review", "closed"]


class RaceCreate(BaseModel):
    # Dati facoltativi della nuova gara.
    date: datetime | None = None


class ResultEntry(BaseModel):
    # Un pilota all'arrivo, con i punti sponsor e i punti extra evento scelti a mano.
    pilot_id: int
    sponsor_points: int = Field(default=0, ge=0)
    bonus_points: int = Field(default=0, ge=0)


class ResultsSet(BaseModel):
    # Risultati nell'ordine di arrivo: la posizione è la posizione nell'elenco.
    # absent: piloti iscritti che non partecipano, dichiarati a mano. Se presente, ogni
    # iscritto deve stare o nei risultati o tra gli assenti.
    results: list[ResultEntry] = Field(min_length=1, max_length=12)
    absent: list[int] | None = None


class RaceRead(BaseModel):
    id: int
    number: int
    date: datetime | None
    participants: int
    status: RaceStatus
    is_last: bool


class RaceResultRead(BaseModel):
    pilot_id: int
    pilot_name: str
    position: int | None
    points: int
    sponsor_points: int
    # Punti proposti dai tasti S della gara. Servono a precompilare il modulo dei
    # risultati, che resta modificabile e salva solo i valori confermati.
    suggested_sponsor_points: int
    # Punti extra evento già inclusi in points, distinti dai punti di posizione.
    bonus_points: int


class RaceDetail(RaceRead):
    results: list[RaceResultRead]


class StandingRead(BaseModel):
    rank: int
    pilot_id: int | None
    pilot_name: str
    points: int
    races_played: int
