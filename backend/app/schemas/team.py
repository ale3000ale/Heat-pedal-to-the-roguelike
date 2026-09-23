# backend/app/schemas/team.py
# Schemi Pydantic per Team, incluso il dettaglio con piloti annidati.

from typing import Optional, List
from pydantic import BaseModel


class TeamCreate(BaseModel):
    name: str
    pilot_id: int  # almeno un pilota dell'utente da associare alla creazione


class TeamPilotOut(BaseModel):
    id: int
    name: str
    point: int
    user_id: int
    is_current_user_pilot: bool = False

    class Config:
        from_attributes = True


class TeamOut(BaseModel):
    id: int
    name: str
    total_points: int
    pilots: List[TeamPilotOut] = []

    class Config:
        from_attributes = True
