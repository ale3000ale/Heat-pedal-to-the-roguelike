from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.schemas.card import CardRead
from app.services.names import clean_name


class PilotName(BaseModel):
    # Nome del pilota, ripulito prima dei controlli di lunghezza (come per i team).
    name: str = Field(min_length=2, max_length=40)

    @field_validator("name", mode="before")
    @classmethod
    def _clean(cls, value):
        return clean_name(value) if isinstance(value, str) else value


class PilotCreate(PilotName):
    # Dati per creare un pilota; il team è facoltativo.
    team_id: int | None = None


class PilotRename(PilotName):
    # Dati per rinominare un pilota.
    pass


class PilotTeamSet(BaseModel):
    # Dati per assegnare un team al pilota. Il campo è obbligatorio:
    # null toglie il pilota dal team, un numero lo assegna a quel team.
    team_id: int | None


class PilotRead(BaseModel):
    # Pilota come lo vede il client nell'elenco.
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    team_id: int | None
    gold: int
    sponsor: int
    point: int


class PilotDetail(PilotRead):
    # Dettaglio del pilota, con inventario e mazzo da gioco.
    inventory: list[CardRead]
    game_deck: list[CardRead]