"""Contratto carte admin: lettura, versioni attese e trasferimenti."""
from pydantic import BaseModel, ConfigDict, Field
from app.services.cards.admin_card_transfers import Container
from app.services.cards.cards import CardEntry


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


class CardAdminRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")


class ExpectedDeckVersion(CardAdminRequest):
    id: int = Field(gt=0, strict=True)
    version: int = Field(gt=0, strict=True)


class ExpectedCardVersions(CardAdminRequest):
    game_deck: ExpectedDeckVersion
    modification_inventory: ExpectedDeckVersion
    sponsor_inventory: ExpectedDeckVersion
    modification_pool: ExpectedDeckVersion | None
    sponsor_pool: ExpectedDeckVersion | None


class AdminCardTransferRequest(CardAdminRequest):
    source: Container
    path: str = Field(min_length=1, max_length=255, strict=True)


class AdminPilotCardsSave(CardAdminRequest):
    versions: ExpectedCardVersions
    transfers: list[AdminCardTransferRequest]
