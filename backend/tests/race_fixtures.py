"""Dati di prova espliciti per i mazzi prima dell'avvio; mai importati dall'app."""
from app.db.models.deck import Deck
from app.db.models.pilot import Pilot
from app.services.cards.cards import CardEntry, dump_cards, parse_cards


def seed_game_deck_from_inventory_card(factory, pilot_id: int, *, path: str, copies: int) -> None:
    """Imposta un mazzo di prova con la carta scelta e il numero esplicito di copie.

    Parametri: factory SQLite dei test, pilota, percorso della carta nell'inventario
    e copie richieste dal singolo test. Ritorno: None dopo il commit dei dati di prova.
    Errori: ValueError per pilota, mazzi o carta mancanti; errori di validazione
    delle carte e SQL propagano. L'inventario non viene modificato: questa e' una
    preparazione di fixture, non un trasferimento di gioco ne' un completamento
    automatico. Nessun valore predefinito di 15, hook, patch o chiamata all'avvio.
    """
    with factory() as db:
        pilot = db.get(Pilot, pilot_id)
        if pilot is None:
            raise ValueError("Pilota di prova mancante")
        inventory = db.get(Deck, pilot.inventory_deck_id)
        game = db.get(Deck, pilot.game_deck_id)
        if inventory is None or game is None or inventory.id == game.id:
            raise ValueError("Mazzi di prova mancanti o coincidenti")
        source = next((card for card in parse_cards(inventory.cards) if card.path == path), None)
        if source is None:
            raise ValueError("Carta di prova assente dall'inventario")
        card = CardEntry(name=source.name, path=source.path, copies=copies)
        game.cards = dump_cards([card])
        db.commit()
