# backend/app/schemas/pilot.py
# Schemi Pydantic per Pilot (request/response API).

from typing import Optional
from pydantic import BaseModel


class PilotBase(BaseModel):
    name: str
    gold: int = 0
    sponsor: int = 0
    point: int = 0
    championship_id: Optional[int] = None
    team: Optional[int] = None


class PilotCreate(PilotBase):
    pass


class PilotUpdate(BaseModel):
    name: Optional[str] = None
    gold: Optional[int] = None
    sponsor: Optional[int] = None
    point: Optional[int] = None
    championship_id: Optional[int] = None
    team: Optional[int] = None


class PilotOut(PilotBase):
    id: int
    user_id: int
    team_name: Optional[str] = None
    championship_name: Optional[str] = None

    class Config:
        from_attributes = True
