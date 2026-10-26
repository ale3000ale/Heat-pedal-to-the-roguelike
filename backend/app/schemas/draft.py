"""Contratti pubblici draft: mai includere snapshot di ripristino."""
from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.draft_state import DraftCardSlot
from app.services.cards import CardEntry

Id = Annotated[int, Field(gt=0)]


class DraftPilotRead(BaseModel):
    """Pilota visibile senza identificativi del proprietario."""
    pilot_id: int
    name: str
    present: bool


class DraftRead(BaseModel):
    """Dati autorizzati per ricostruire modal, turno e comandi disponibili."""
    id: int
    championship_id: int
    version: int
    phase: Literal["attendance", "order", "picking", "decks"]
    first_race: bool
    can_manage: bool
    my_pilot_ids: list[int]
    participants: list[DraftPilotRead]
    order: list[int]
    cards: list[DraftCardSlot]
    picks: list[int]
    preview_slot_id: int | None
    ready: list[int]
    current_pilot_id: int | None


class DraftPilotDeckRead(BaseModel):
    """Solo inventario modifiche e mazzo del proprietario; sponsor esclusi."""
    pilot_id: int
    preparation_version: int
    ready: bool
    inventory_version: int
    game_version: int
    inventory: list[CardEntry]
    game_deck: list[CardEntry]


class DraftVersionCommand(BaseModel):
    """Versione ottimistica obbligatoria, senza coercizioni o campi extra."""
    model_config = ConfigDict(extra="forbid", strict=True)
    version: Id


class DraftAttendanceCommand(DraftVersionCommand):
    pilot_id: Id
    present: bool


class DraftOrderCommand(DraftVersionCommand):
    pilot_ids: list[Id]


class DraftPreviewCommand(DraftVersionCommand):
    slot_id: Id | None


class DraftChoiceCommand(DraftVersionCommand):
    slot_id: Id


class DraftMoveCommand(DraftVersionCommand):
    pilot_id: Id
    path: str = Field(min_length=1, max_length=255)
    to_game: bool


class DraftReadyCommand(DraftVersionCommand):
    pilot_id: Id
    ready: bool


class DraftActionRead(BaseModel):
    """Conclusione: race_id; altrimenti preparazione aggiornata."""
    preparation: DraftRead | None
    race_id: int | None
