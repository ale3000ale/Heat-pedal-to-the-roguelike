"""Valutazione pura dei mazzi prima dell'avvio: nessun accesso DB o HTTP."""
from collections.abc import Iterable
from dataclasses import dataclass
from typing import Literal

from app.services.cards import CardError, MAX_GAME_DECK_CARDS, parse_cards


@dataclass(frozen=True, slots=True)
class PilotGameDeck:
    """Riga interna letta dal mazzo da gioco, non dall'inventario totale."""
    pilot_id: int
    pilot_name: str
    cards: str | None


@dataclass(frozen=True, slots=True)
class UnreadyGameDeck:
    """Riepilogo senza carte; count=None indica JSON non valido, non zero copie."""
    pilot_id: int
    pilot_name: str
    count: int | None
    reason: Literal["wrong_count", "invalid_cards"]


class GameDecksNotReadyError(ValueError):
    """Conserva tutti i piloti non pronti; il chiamante deve impedire gara ed evento."""
    def __init__(self, unready: tuple[UnreadyGameDeck, ...]):
        self.unready = unready
        details = "; ".join(
            f"{row.pilot_name}: {row.count}/{MAX_GAME_DECK_CARDS}" if row.count is not None
            else f"{row.pilot_name}: mazzo non valido"
            for row in unready
        )
        super().__init__("Mazzi non pronti: " + details)


def unready_game_decks(decks: Iterable[PilotGameDeck]) -> tuple[UnreadyGameDeck, ...]:
    """Raccoglie tutti i mazzi con conteggio diverso da 15 o JSON non valido.

    Parametro: righe dei soli mazzi da gioco di tutti gli iscritti. Il chiamante
    deve leggerle nella transazione protetta di avvio e verificare i riferimenti.
    Ritorno: riepiloghi immutabili nell'ordine di ingresso; nessuna carta esposta.
    CardError viene convertito in invalid_cards con count=None, mai in mazzo vuoto.
    Altri errori propagano. Non modifica dati, non completa mazzi e non impone un
    nuovo minimo di iscritti. La funzione da sola non protegge da concorrenza e
    non e' ancora collegata a create_race in questo incremento.
    """
    unready = []
    for deck in decks:
        try:
            count = sum(card.copies for card in parse_cards(deck.cards))
        except CardError:
            unready.append(UnreadyGameDeck(deck.pilot_id, deck.pilot_name, None, "invalid_cards"))
            continue
        if count != MAX_GAME_DECK_CARDS:
            unready.append(UnreadyGameDeck(deck.pilot_id, deck.pilot_name, count, "wrong_count"))
    return tuple(unready)


def require_ready_game_decks(decks: Iterable[PilotGameDeck]) -> None:
    """Valida tutte le righe; solleva GameDecksNotReadyError con l'intero riepilogo.

    Parametro: righe dei mazzi da gioco; ritorno None se tutti pronti.
    Non acquisisce lock, non esegue commit/rollback e non genera race.started.
    La gestione della transazione e la traduzione HTTP spettano all'integrazione.
    """
    unready = unready_game_decks(decks)
    if unready:
        raise GameDecksNotReadyError(unready)
