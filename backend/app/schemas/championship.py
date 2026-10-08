from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.services.names import clean_name


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
