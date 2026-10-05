from pydantic import ValidationError
from sqlalchemy.orm import Session

from app.db.models.deck import DeckPrototype
from app.services.cards import CardEntry, card_key, dump_cards
from app.services.pools import PoolRuleError, get_pool, pool_cards


class PoolCardNotFoundError(Exception):
    """La carta non è nella pool."""


class PoolCardNameTakenError(Exception):
    """Un'altra carta della pool ha già questo nome (senza distinguere le maiuscole)."""


def rename_pool_card(db: Session, pool_id: int, path: str, new_name: str) -> DeckPrototype:
    # Cambia il nome di una carta della pool. La carta si riconosce dal percorso, che non
    # cambia mai. Le altre pool e i campionati hanno una loro copia e non vengono toccati.
    pool = get_pool(db, pool_id)
    cards = pool_cards(pool)
    index = next((i for i, card in enumerate(cards) if card.path == path), None)
    if index is None:
        raise PoolCardNotFoundError
    name = new_name.strip()
    if not name:
        raise PoolRuleError("Il nome della carta non può essere vuoto")
    key = card_key(name)
    if any(i != index and card_key(card.name) == key for i, card in enumerate(cards)):
        raise PoolCardNameTakenError
    try:
        cards[index] = CardEntry(name=name, path=cards[index].path, copies=cards[index].copies)
    except ValidationError:
        raise PoolRuleError("Nome della carta non valido")
    pool.base_cards = dump_cards(cards)
    db.commit()
    db.refresh(pool)
    return pool
