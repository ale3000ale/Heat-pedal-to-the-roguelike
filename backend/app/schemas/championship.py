# backend/app/schemas/championship.py
# Schemi Pydantic per Championship e ChampionshipParticipant.

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel


class ParticipantOut(BaseModel):
    pilot_id: int
    pilot_name: str
    points: int
    ranking: Optional[int] = None

    class Config:
        from_attributes = True


class ChampionshipOut(BaseModel):
    id: int
    name: str
    date: datetime
    deck: Optional[int] = None
    participants: List[ParticipantOut] = []

    class Config:
        from_attributes = True


class ChampionshipCreate(BaseModel):
    name: str
    date: datetime
    deck: Optional[int] = None
