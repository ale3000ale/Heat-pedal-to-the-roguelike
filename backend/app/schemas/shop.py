from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field, field_validator, model_validator

from app.services.names import clean_name


class PackData(BaseModel):
    # Caratteristiche di un template di pacchetto o di un pacchetto (dati in ingresso).
    name: str = Field(min_length=1, max_length=40)
    image_path: str | None = None
    currency: Literal["gold", "sponsor"]
    cost: int = Field(gt=0)
    modifiche_count: int = Field(default=3, ge=0)
    sponsor_count: int = Field(default=0, ge=0)
    filter_enabled: bool = False
    filter_text: str | None = None

    @field_validator("name", mode="before")
    @classmethod
    def _clean_name(cls, value):
        return clean_name(value) if isinstance(value, str) else value

    @field_validator("filter_text", mode="before")
    @classmethod
    def _normalize_filter(cls, value):
        # Nomi separati da virgola, senza spazi in più e senza voci vuote.
        if not isinstance(value, str):
            return value
        terms = [term.strip() for term in value.split(",") if term.strip()]
        return ", ".join(terms) or None

    @model_validator(mode="after")
    def _check_rules(self):
        if self.modifiche_count + self.sponsor_count < 1:
            raise ValueError("Il pacchetto deve contenere almeno una carta")
        if self.filter_enabled and not self.filter_text:
            raise ValueError("Il filtro attivo richiede almeno un nome")
        return self


class PackTemplateRead(BaseModel):
    model_config = {"from_attributes": True}

    id: int
    name: str
    image_path: str
    currency: str
    cost: int
    modifiche_count: int
    sponsor_count: int
    filter_enabled: bool
    filter_text: str | None
    created_at: datetime
    updated_at: datetime


class PackImageRead(BaseModel):
    # Percorso relativo dentro media/pack, es. "illustration/turbo.webp".
    path: str


class ShopTemplateData(BaseModel):
    # Dati per creare o modificare un template di negozio.
    name: str = Field(min_length=2, max_length=40)
    pack_template_ids: list[int] = Field(default_factory=list)

    @field_validator("name", mode="before")
    @classmethod
    def _clean_name(cls, value):
        return clean_name(value) if isinstance(value, str) else value


class ShopTemplateRead(BaseModel):
    model_config = {"from_attributes": True}

    id: int
    name: str
    created_at: datetime
    pack_template_ids: list[int]
    # Vero se non ha template di pacchetto (triangolo giallo, non utilizzabile).
    is_empty: bool
