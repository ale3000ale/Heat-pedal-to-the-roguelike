from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.services.names import clean_name


class TeamWrite(BaseModel):
    # Dati per creare o rinominare un team. Il nome viene ripulito prima dei controlli
    # di lunghezza, quindi "  a  " non supera il minimo di 2 caratteri.
    name: str = Field(min_length=2, max_length=40)

    @field_validator("name", mode="before")
    @classmethod
    def _clean(cls, value):
        return clean_name(value) if isinstance(value, str) else value


class TeamRead(BaseModel):
    # Team come lo vede il client.
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str