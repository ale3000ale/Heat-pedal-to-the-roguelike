from typing import Self

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class ReviewInput(BaseModel):
    model_config = ConfigDict(extra="forbid")


class ReviewCountItem(ReviewInput):
    card_name: str = Field(min_length=1, max_length=64)
    remaining: int = Field(strict=True, ge=0)

    @field_validator("card_name")
    @classmethod
    def clean_card_name(cls, value: str) -> str:
        """Ripulisce il nome ricevuto; restituisce il nome o rifiuta un valore vuoto."""
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("Il nome della carta non può essere vuoto")
        return cleaned


class ReviewPilotCounts(ReviewInput):
    pilot_id: int = Field(strict=True, gt=0)
    cards: list[ReviewCountItem]

    @model_validator(mode="after")
    def unique_cards(self) -> Self:
        """Valida le carte del pilota; restituisce self o rifiuta nomi duplicati."""
        keys = [card.card_name.casefold() for card in self.cards]
        if len(keys) != len(set(keys)):
            raise ValueError("Carta ripetuta nei conteggi del pilota")
        return self


class ReviewCountsRequest(ReviewInput):
    pilots: list[ReviewPilotCounts]

    @model_validator(mode="after")
    def unique_pilots(self) -> Self:
        """Valida la richiesta; restituisce self o rifiuta piloti duplicati."""
        ids = [pilot.pilot_id for pilot in self.pilots]
        if len(ids) != len(set(ids)):
            raise ValueError("Pilota ripetuto nei conteggi della revisione")
        return self

    def to_counts(self) -> dict[tuple[int, str], int]:
        """Converte la richiesta validata in (pilota, nome normalizzato) -> quantità.

        Ritorna un dizionario nuovo senza modificare la richiesta. I validatori
        garantiscono l'assenza di chiavi duplicate e di quantità negative.
        """
        return {
            (pilot.pilot_id, card.card_name.casefold()): card.remaining
            for pilot in self.pilots
            for card in pilot.cards
        }
