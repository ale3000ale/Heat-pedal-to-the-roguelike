# backend/app/schemas/deck.py
# Schemi Pydantic per Deck e Deck_prototype, inclusa la struttura delle singole carte.

from typing import Optional, List
from pydantic import BaseModel, field_validator


class CardItem(BaseModel):
    """Rappresenta una singola carta dentro il JSON di Deck.cards / Deck_prototype.base_cards."""
    path: str
    value: int

    # validate_path(v)
    # v: path relativo dell'immagine della carta (es. "src/images/cards/3_SpeedBoost.png").
    # Verifica che il file segua la convenzione di naming N_nome.ext richiesta dal progetto.
    @field_validator("path")
    @classmethod
    def validate_path(cls, v: str) -> str:
        filename = v.split("/")[-1]
        prefix = filename.split("_", 1)[0]
        if not prefix.isdigit():
            raise ValueError(
                f"Path carta non valido: '{v}'. Formato atteso N_nome.ext (N intero 1-10)"
            )
        n = int(prefix)
        if not (1 <= n <= 10):
            raise ValueError(f"L'indice N della carta '{v}' deve essere tra 1 e 10")
        return v

    # validate_value(v)
    # v: valore numerico associato alla carta (punteggio/effetto in gioco).
    # Garantisce che il valore sia un intero non negativo, coerente con le regole di gioco.
    @field_validator("value")
    @classmethod
    def validate_value(cls, v: int) -> int:
        if not isinstance(v, int) or v < 0:
            raise ValueError("Il campo 'value' della carta deve essere un intero >= 0")
        return v


class DeckPrototypeOut(BaseModel):
    id: int
    name: str
    base_cards: List[CardItem] = []

    class Config:
        from_attributes = True


class DeckOut(BaseModel):
    id: int
    id_prototype: int
    pilot_id: Optional[int] = None
    pilot_name: Optional[str] = None
    championship_name: Optional[str] = None
    cards: List[CardItem] = []

    class Config:
        from_attributes = True


class DeckCreate(BaseModel):
    id_prototype: int
    pilot_id: Optional[int] = None
    cards: List[CardItem]
