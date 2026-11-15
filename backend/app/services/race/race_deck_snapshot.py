"""Lettura DB dei mazzi iscritti; il chiamante possiede la transazione protetta."""
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models.championship import ChampionshipPilot
from app.db.models.deck import Deck
from app.db.models.pilot import Pilot
from app.services.race.race_deck_readiness import (
    GameDecksNotReadyError,
    PilotGameDeck,
    UnreadyGameDeck,
    unready_game_decks,
)


def require_ready_championship_decks(db: Session, championship_id: int) -> None:
    """Verifica tutti gli iscritti leggendo colonne DB, non identita' ORM in cache.

    Parametri: sessione e identificativo del campionato gia' verificato dal chiamante.
    Ritorno: None se tutti i mazzi hanno 15 copie, anche senza iscritti.
    Errori: GameDecksNotReadyError con tutti i piloti non pronti, senza carte;
    gli errori SQL propagano. Un Deck mancante e' invalido, non un mazzo vuoto.
    Include gli iscritti nascosti e ignora inventari e pool. Nessun autoflush,
    lock, commit, rollback o evento: il chiamante deve acquisire il lock condiviso
    prima della lettura e mantenerlo fino al commit dell'avvio. Questa funzione
    da sola non impedisce una modifica concorrente e non verifica l'esistenza
    o lo stato del campionato.
    """
    statement = (
        select(Pilot.id, Pilot.name, Deck.id, Deck.cards)
        .select_from(Pilot)
        .join(ChampionshipPilot, ChampionshipPilot.pilot_id == Pilot.id)
        .outerjoin(Deck, Deck.id == Pilot.game_deck_id)
        .where(ChampionshipPilot.championship_id == championship_id)
        .order_by(Pilot.name_key, Pilot.id)
    )
    with db.no_autoflush:
        rows = db.execute(statement).all()
    unready = []
    for pilot_id, pilot_name, deck_id, cards in rows:
        if deck_id is None:
            unready.append(UnreadyGameDeck(pilot_id, pilot_name, None, "invalid_cards"))
        else:
            unready.extend(unready_game_decks((PilotGameDeck(pilot_id, pilot_name, cards),)))
    if unready:
        raise GameDecksNotReadyError(tuple(unready))
