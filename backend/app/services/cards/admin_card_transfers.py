"""Trasferimenti admin puri: nessuna lettura, scrittura o autorizzazione DB."""
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import Literal

from pydantic import ValidationError

from app.services.cards.cards import CardEntry, CardError, card_key, dump_cards, parse_cards

Container = Literal[
    "game_deck", "modification_inventory", "sponsor_inventory",
    "modification_pool", "sponsor_pool",
]
_DESTINATIONS: dict[Container, Container] = {
    "game_deck": "modification_pool",
    "modification_inventory": "modification_pool",
    "sponsor_inventory": "sponsor_pool",
    "modification_pool": "modification_inventory",
    "sponsor_pool": "sponsor_inventory",
}


class CardTransferError(ValueError):
    """Bozza non applicabile: contenitore, carta o quantita' incompatibile."""


@dataclass(frozen=True, slots=True)
class CardTransfer:
    """Un clic: sorgente e percorso esistente; destinazione imposta dal dominio."""

    source: Container
    path: str


def plan_transfers(
    containers: Mapping[Container, list[CardEntry]],
    transfers: Sequence[CardTransfer],
) -> dict[Container, list[CardEntry]]:
    """Prepara una bozza indipendente applicando una copia per operazione.

    Parametri: cinque contenitori fisici e operazioni nell'ordine dei clic.
    Ritorno: nuove liste e nuove CardEntry, anche per i contenitori invariati.
    Errori: CardTransferError su input, sorgenti o destinazioni incompatibili.
    Non muta mai gli input, neppure se una successiva operazione fallisce.
    Non verifica ruoli, versioni, esistenza delle pool o stato gara: questi
    controlli spettano al servizio transazionale prima di persistere il piano.
    """
    if set(containers) != set(_DESTINATIONS):
        raise CardTransferError("Servono esattamente i cinque contenitori")
    try:
        planned = {
            name: parse_cards(dump_cards(cards)) for name, cards in containers.items()
        }
        for transfer in transfers:
            if transfer.source not in _DESTINATIONS:
                raise CardTransferError("Contenitore sorgente non valido")
            if not isinstance(transfer.path, str) or not transfer.path:
                raise CardTransferError("Percorso della carta non valido")
            source = planned[transfer.source]
            destination = planned[_DESTINATIONS[transfer.source]]
            _move_one(source, destination, transfer.path)
        return planned
    except (CardError, ValidationError) as exc:
        raise CardTransferError("Carte non valide o limite di copie superato") from exc


def _move_one(source: list[CardEntry], destination: list[CardEntry], path: str) -> None:
    """Muove una copia nelle sole liste di lavoro; rifiuta percorsi ambigui.

    Parametri: liste gia' clonate e percorso della carta sorgente.
    Ritorno: None. Errori: CardTransferError se assente/ambigua o incompatibile;
    ValidationError se la nuova quantita' supera i limiti di CardEntry.
    """
    matches = [(i, card) for i, card in enumerate(source) if card.path == path]
    if len(matches) != 1:
        raise CardTransferError("Carta sorgente assente o percorso ambiguo")
    index, card = matches[0]
    target = next(
        (i for i, item in enumerate(destination) if card_key(item.name) == card_key(card.name)),
        None,
    )
    if target is not None:
        existing = destination[target]
        if existing.path != card.path:
            raise CardTransferError("Nome carta associato a immagini diverse")
        destination[target] = CardEntry(
            name=existing.name, path=existing.path, copies=existing.copies + 1,
        )
    else:
        destination.append(CardEntry(name=card.name, path=card.path, copies=1))
    if card.copies == 1:
        del source[index]
    else:
        source[index] = CardEntry(name=card.name, path=card.path, copies=card.copies - 1)
