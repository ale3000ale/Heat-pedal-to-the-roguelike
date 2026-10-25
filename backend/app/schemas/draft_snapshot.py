"""Contratto interno del ripristino draft; non e una risposta pubblica API."""
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from app.services.cards import parse_cards


class DraftDeckSnapshot(BaseModel):
    """Testo originale e versione di un Deck prima della preparazione.

    Conserva anche None o stringa vuota, ammessi dal lettore corrente delle carte.
    Non normalizza il testo: il ripristino deve poter recuperare l'originale.
    La versione iniziale non autorizza sovrascritture di versioni successive.
    """

    model_config = ConfigDict(extra="forbid", strict=True)

    deck_id: int = Field(gt=0)
    version: int = Field(gt=0)
    cards: str | None

    @field_validator("cards")
    @classmethod
    def validate_cards(cls, value: str | None) -> str | None:
        """Valida con parse_cards senza riscrivere il testo; errore se corrotto."""
        parse_cards(value)
        return value


class DraftSnapshot(BaseModel):
    """Snapshot interno versionato di contenitori distinti.

    Parametri: formato e lista di mazzi. Rifiuta campi extra, tipi coercibili,
    formato sconosciuto e ID duplicati. Non acquisisce lock, non legge Deck e
    non implementa ripristino o protezione da scritture concorrenti.
    """

    model_config = ConfigDict(extra="forbid", strict=True)

    format_version: int = Field(ge=1, le=1)
    decks: list[DraftDeckSnapshot]

    @model_validator(mode="after")
    def unique_decks(self) -> "DraftSnapshot":
        """Impedisce due originali diversi per lo stesso contenitore."""
        ids = [deck.deck_id for deck in self.decks]
        if len(set(ids)) != len(ids):
            raise ValueError("Mazzo ripetuto nello snapshot draft")
        return self
