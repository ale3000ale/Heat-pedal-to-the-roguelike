from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models.card_play import STATUS_CONSUMED, STATUS_PLAYED, CardPlay
from app.db.models.deck import Deck
from app.db.models.pilot import Pilot
from app.services.cards import CardEntry, CardError, card_key, dump_cards, parse_cards


def _remove_from_inventory(inventory: dict[str, CardEntry], play: CardPlay) -> None:
    # Toglie una copia della carta giocata dall'inventario sponsor del pilota.
    # Errori: CardError se la carta non c'è più (l'inventario non cambia durante la gara).
    key = card_key(play.card_name)
    card = inventory.get(key)
    if card is None:
        raise CardError(f"Carta giocata non presente nell'inventario: {play.card_name}")
    card.copies -= 1
    if card.copies <= 0:
        del inventory[key]


def _add_to_pool(pool: dict[str, CardEntry], returned: dict[str, CardEntry]) -> None:
    # Somma le copie restituite alla pool, creando la riga se la carta non c'è.
    for key, card in returned.items():
        if key in pool:
            pool[key].copies += card.copies
        else:
            pool[key] = card


def consume_plays(db: Session, race_id: int, sponsor_pool_deck_id: int | None) -> None:
    # Alla prima chiusura della gara: le carte giocate (non annullate) escono per sempre
    # dall'inventario sponsor del pilota, tornano nella pool sponsor del campionato e le
    # righe del registro passano a 'consumata'. Non fa commit: lo fa chi chiude la gara,
    # così tutto avviene nella stessa transazione. Senza pool sponsor le carte escono
    # comunque dall'inventario.
    # Errori: CardError se una carta giocata non è più nell'inventario.
    stmt = select(CardPlay).where(CardPlay.race_id == race_id, CardPlay.status == STATUS_PLAYED)
    plays = list(db.scalars(stmt.order_by(CardPlay.id)))
    if not plays:
        return
    returned: dict[str, CardEntry] = {}
    by_pilot: dict[int, list[CardPlay]] = {}
    for play in plays:
        by_pilot.setdefault(play.pilot_id, []).append(play)
    for pilot_id, pilot_plays in by_pilot.items():
        pilot = db.get(Pilot, pilot_id)
        deck = db.get(Deck, pilot.sponsor_inventory_deck_id)
        inventory = {card_key(card.name): card for card in parse_cards(deck.cards)}
        for play in pilot_plays:
            _remove_from_inventory(inventory, play)
            key = card_key(play.card_name)
            if key in returned:
                returned[key].copies += 1
            else:
                returned[key] = CardEntry(name=play.card_name, path=play.card_path, copies=1)
            play.status = STATUS_CONSUMED
        deck.cards = dump_cards(list(inventory.values()))
    if sponsor_pool_deck_id is None:
        return
    pool_deck = db.get(Deck, sponsor_pool_deck_id)
    pool = {card_key(card.name): card for card in parse_cards(pool_deck.cards)}
    _add_to_pool(pool, returned)
    pool_deck.cards = dump_cards(list(pool.values()))
