from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.db.models.deck import DeckPrototype
from app.services.cards import CardEntry, card_key, dump_cards, parse_cards
from app.services.names import clean_name

# Nome della pool di base: il catalogo completo da cui nascono tutte le altre.
BASE_POOL_NAME = "default"


class PoolNotFoundError(Exception):
    """La pool non esiste."""


class PoolNameTakenError(Exception):
    """Esiste già una pool con questo nome (senza distinguere le maiuscole)."""


class PoolProtectedError(Exception):
    """La pool di base non si può eliminare."""


class PoolRuleError(ValueError):
    """La scelta delle carte non rispetta la pool di base (messaggio leggibile)."""


def list_pools(db: Session) -> list[DeckPrototype]:
    # Tutte le pool, dalla più vecchia alla più recente.
    return list(db.scalars(select(DeckPrototype).order_by(DeckPrototype.id)))


def get_pool(db: Session, pool_id: int) -> DeckPrototype:
    pool = db.get(DeckPrototype, pool_id)
    if pool is None:
        raise PoolNotFoundError
    return pool


def get_base_pool(db: Session) -> DeckPrototype:
    pool = db.scalar(select(DeckPrototype).where(DeckPrototype.name == BASE_POOL_NAME))
    if pool is None:
        raise PoolNotFoundError
    return pool


def pool_cards(pool: DeckPrototype) -> list[CardEntry]:
    return parse_cards(pool.base_cards)


def create_pool(db: Session, name: str, choices: list[tuple[str, int]]) -> DeckPrototype:
    # Crea una pool scegliendo carte e copie dalla pool di base. Nome, percorso e
    # grafia delle carte sono quelli della base; le copie non possono superarla.
    name = clean_name(name)
    if any(pool.name.casefold() == name.casefold() for pool in list_pools(db)):
        raise PoolNameTakenError
    base = {card_key(card.name): card for card in pool_cards(get_base_pool(db))}
    chosen: list[CardEntry] = []
    seen: set[str] = set()
    for card_name, copies in choices:
        key = card_key(card_name)
        if key not in base:
            raise PoolRuleError(f"Carta non presente nella pool di base: {card_name}")
        if key in seen:
            raise PoolRuleError(f"Carta ripetuta: {card_name}")
        if copies > base[key].copies:
            raise PoolRuleError(
                f"Troppe copie di {base[key].name}: la pool di base ne ha {base[key].copies}"
            )
        seen.add(key)
        chosen.append(CardEntry(name=base[key].name, path=base[key].path, copies=copies))
    if not chosen:
        raise PoolRuleError("La pool deve contenere almeno una carta")
    pool = DeckPrototype(name=name, base_cards=dump_cards(chosen))
    db.add(pool)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise PoolNameTakenError
    db.refresh(pool)
    return pool


def delete_pool(db: Session, pool_id: int) -> None:
    # Elimina una pool. I campionati già creati non cambiano: hanno la loro copia.
    pool = get_pool(db, pool_id)
    if pool.name == BASE_POOL_NAME:
        raise PoolProtectedError
    db.delete(pool)
    db.commit()