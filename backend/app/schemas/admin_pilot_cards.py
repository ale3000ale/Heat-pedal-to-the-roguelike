"""Contratto di lettura admin: contenitori fisici, immagini e versioni."""
from pydantic import BaseModel, Field
from app.services.cards import CardEntry


class AdminPilotRead(BaseModel):
    pilot_id: int
    name: str
    user_id: int
    username: str


class AdminDeckRead(BaseModel):
    available: bool
    id: int | None
    version: int | None
    cards: list[CardEntry] = Field(default_factory=list)


class AdminCardContainers(BaseModel):
    game_deck: AdminDeckRead
    modification_inventory: AdminDeckRead
    sponsor_inventory: AdminDeckRead
    modification_pool: AdminDeckRead
    sponsor_pool: AdminDeckRead


class AdminPilotCardsRead(BaseModel):
    championship_id: int
    pilot: AdminPilotRead
    read_only: bool
    blocked_reason: str | None
    containers: AdminCardContainers
