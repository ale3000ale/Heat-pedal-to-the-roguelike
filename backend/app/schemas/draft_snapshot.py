"""Snapshot interno di ripristino; non serializzare nelle risposte pubbliche."""
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from app.services.cards import parse_cards


class DraftDeckSnapshot(BaseModel):
    """Originale del Deck e ultima versione prodotta dalla preparazione.

    cards e version conservano l'originale; current_version segue soltanto le
    scritture autorizzate della procedura. None usa version per gli snapshot
    iniziali. Non usare la versione corrente del DB per assorbire conflitti.
    """
    model_config = ConfigDict(extra="forbid", strict=True)
    deck_id: int = Field(gt=0)
    version: int = Field(gt=0)
    cards: str | None
    current_version: int | None = Field(default=None, gt=0)

    @field_validator("cards")
    @classmethod
    def validate_cards(cls, value: str | None) -> str | None:
        """Valida le carte mantenendo il testo originale, inclusi None e stringa vuota."""
        parse_cards(value)
        return value

    @model_validator(mode="after")
    def monotonic_version(self) -> "DraftDeckSnapshot":
        """Rifiuta una versione corrente inferiore a quella iniziale."""
        if self.current_version is not None and self.current_version < self.version:
            raise ValueError("Versione corrente precedente allo snapshot")
        return self


class DraftSnapshot(BaseModel):
    """Snapshot versionato di contenitori distinti; nessun accesso DB o ripristino."""
    model_config = ConfigDict(extra="forbid", strict=True)
    format_version: int = Field(ge=1, le=1)
    decks: list[DraftDeckSnapshot]

    @model_validator(mode="after")
    def unique_decks(self) -> "DraftSnapshot":
        """Impedisce due originali differenti per lo stesso contenitore."""
        ids = [deck.deck_id for deck in self.decks]
        if len(set(ids)) != len(ids):
            raise ValueError("Mazzo ripetuto nello snapshot draft")
        return self
