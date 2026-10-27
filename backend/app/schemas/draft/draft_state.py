"""Stato interno persistente della draft; non include snapshot o dati di sessione."""
from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

PositiveId = Annotated[int, Field(gt=0)]


class DraftParticipant(BaseModel):
    """Pilota e proprietario fissati dalla preparazione, mai fidarsi del client."""

    model_config = ConfigDict(extra="forbid", strict=True)
    pilot_id: PositiveId
    user_id: PositiveId
    name: str = Field(min_length=1)
    present: bool


class DraftCardSlot(BaseModel):
    """Una singola copia estratta: slot_id distingue anche carte identiche."""

    model_config = ConfigDict(extra="forbid", strict=True)
    slot_id: PositiveId
    name: str = Field(min_length=1, max_length=64)
    path: str = Field(min_length=1, max_length=255)
    chosen_by: PositiveId | None = None


class DraftState(BaseModel):
    """Valida riferimenti e coerenza tra fase, ordine, scelte e disponibilita.

    Parametri: stato completo nel formato 1. Ritorna un modello validato;
    ValidationError per campi extra, tipi errati o relazioni incoerenti.
    Non verifica iscrizioni, proprieta, percorsi su disco o transizioni da uno
    stato precedente: tali controlli appartengono ai servizi transazionali.
    """

    model_config = ConfigDict(extra="forbid", strict=True)
    format_version: int = Field(ge=1, le=1)
    phase: Literal["attendance", "order", "picking", "decks"]
    first_race: bool
    participants: list[DraftParticipant]
    order: list[PositiveId]
    cards: list[DraftCardSlot]
    picks: list[PositiveId]
    preview_slot_id: PositiveId | None
    ready: list[PositiveId]

    @model_validator(mode="after")
    def coherent_state(self) -> "DraftState":
        """Rifiuta duplicati e riferimenti impossibili prima della persistenza."""
        pilots = [item.pilot_id for item in self.participants]
        slots = [item.slot_id for item in self.cards]
        for values in (pilots, slots, self.order, self.picks, self.ready):
            if len(values) != len(set(values)):
                raise ValueError("Riferimento ripetuto nello stato draft")
        present = {item.pilot_id for item in self.participants if item.present}
        if self.phase == "attendance":
            if self.order or self.cards or self.picks or self.ready or self.preview_slot_id is not None:
                raise ValueError("La selezione presenze non contiene scelte o disponibilita")
            return self
        if not present:
            raise ValueError("Serve almeno un pilota presente")
        if self.phase in ("order", "picking") and set(self.order) != present:
            raise ValueError("L'ordine deve contenere tutti e soli i presenti")
        if self.phase == "order":
            if self.cards or self.picks or self.ready or self.preview_slot_id is not None:
                raise ValueError("La fase ordine non contiene carte o disponibilita")
            return self
        if self.cards:
            if set(self.order) != present or len(self.cards) != len(present) + 3:
                raise ValueError("Estrazione o ordine non coerenti con i presenti")
            by_slot = {card.slot_id: card for card in self.cards}
            if not set(self.picks) <= set(by_slot):
                raise ValueError("Scelta riferita a una copia inesistente")
            chosen = {card.slot_id for card in self.cards if card.chosen_by is not None}
            if chosen != set(self.picks) or len(self.picks) > len(self.order):
                raise ValueError("Registro scelte incoerente")
            for index, slot_id in enumerate(self.picks):
                if by_slot[slot_id].chosen_by != self.order[index]:
                    raise ValueError("Scelta fuori ordine")
        elif self.order or self.picks or self.phase == "picking":
            raise ValueError("La draft richiede le copie estratte")
        if self.phase == "picking":
            if len(self.picks) >= len(self.order) or self.ready:
                raise ValueError("Turno esaurito o disponibilita prematura")
            available = {card.slot_id for card in self.cards if card.chosen_by is None}
            if self.preview_slot_id is not None and self.preview_slot_id not in available:
                raise ValueError("Anteprima riferita a una copia non disponibile")
        else:
            if self.cards and len(self.picks) != len(present):
                raise ValueError("Preparazione mazzi prima della fine delle scelte")
            if self.preview_slot_id is not None or not set(self.ready) <= present:
                raise ValueError("Anteprima o disponibilita non valida")
        return self
