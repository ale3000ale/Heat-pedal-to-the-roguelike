from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.services.pilots.names import clean_name


class ChampionshipCreate(BaseModel):
    # Dati per creare un campionato; senza pool_id e sponsor_pool_id usa le pool di base.
    # Con shop_template_id il negozio parte con i pacchetti di quel template di negozio;
    # senza, il negozio è vuoto.
    name: str = Field(min_length=2, max_length=40)
    pool_id: int | None = None
    sponsor_pool_id: int | None = None
    shop_template_id: int | None = None

    @field_validator("name", mode="before")
    @classmethod
    def _clean(cls, value):
        return clean_name(value) if isinstance(value, str) else value


class EnrollRequest(BaseModel):
    pilot_id: int


class EntrantRead(BaseModel):
    # Pilota iscritto, come lo vedono tutti.
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    team_id: int | None
    point: int


class ChampionshipRead(BaseModel):
    id: int
    name: str
    date: datetime
    is_closed: bool
    pilots_count: int


class ChampionshipDetail(ChampionshipRead):
    pilots: list[EntrantRead]
    # Percorsi relativi a media delle carte estratte per la prossima gara.
    next_map_path: str | None
    next_event_path: str | None
    # Conteggi derivati da maps.json per la mappa estratta.
    next_map_stress: int | None
    next_map_heat: int | None
    next_map_curve: int | None
    next_map_caselle: int | None
