from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.schemas.card import CardRead
from app.services.names import clean_name


class PoolChoice(BaseModel):
    # Una carta scelta dalla pool di base, con il numero di copie da tenere.
    name: str = Field(min_length=1, max_length=64)
    copies: int = Field(ge=1, le=999)


class PoolCreate(BaseModel):
    # Dati per creare una pool derivata dalla pool di base.
    name: str = Field(min_length=2, max_length=40)
    cards: list[PoolChoice] = Field(min_length=1)

    @field_validator("name", mode="before")
    @classmethod
    def _clean(cls, value):
        return clean_name(value) if isinstance(value, str) else value


class PoolRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str


class PoolDetail(PoolRead):
    cards: list[CardRead]