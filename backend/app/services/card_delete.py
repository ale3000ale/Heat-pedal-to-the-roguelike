from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import MEDIA_DIR
from app.db.models.card_gift import CardGift
from app.db.models.card_play import CardPlay
from app.db.models.deck import Deck, DeckPrototype
from app.services.cards import CardError, card_key, dump_cards, parse_cards
from app.services.pools import POOL_KINDS, get_base_pool, pool_cards


class CardNotFoundError(Exception):
    """La carta non esiste nella pool di base del tipo indicato (risposta 404)."""


class CardNotDeletableError(Exception):
    """Solo le carte caricate si eliminano: quelle di base e di partenza no (409)."""


def uploads_prefix(kind: str) -> str:
    # Prefisso del percorso relativo delle carte caricate di un tipo.
    return f"cards/uploads/{kind}/"


def _paths_in_use(db: Session) -> set[str] | None:
    # Percorsi di tutte le carte che compaiono ancora da qualche parte: pool di base e
    # personalizzate, ogni mazzo (copie di pool dei campionati, inventari, mazzi da gioco)
    # e registri di giocate e regali. Più prudente della specifica, che parla delle sole
    # pool dei campionati: un file in un inventario non deve perdere l'immagine.
    # Ritorna None se un mazzo ha un formato illeggibile: nel dubbio non si cancella nulla.
    paths: set[str] = set()
    raw_values = list(db.scalars(select(DeckPrototype.base_cards)))
    raw_values += list(db.scalars(select(Deck.cards)))
    try:
        for raw in raw_values:
            paths.update(card.path for card in parse_cards(raw))
    except CardError:
        return None
    paths.update(db.scalars(select(CardPlay.card_path)))
    paths.update(db.scalars(select(CardGift.card_path)))
    return paths


def remove_orphan_uploads(db: Session) -> list[str]:
    # Cancella i file di backend/media/cards/uploads che nessuna carta usa più e ritorna i
    # loro percorsi relativi. Un file che non si riesce a cancellare resta dov'è.
    folder = MEDIA_DIR / "cards" / "uploads"
    if not folder.is_dir():
        return []
    in_use = _paths_in_use(db)
    if in_use is None:
        return []
    removed: list[str] = []
    for file in sorted(folder.rglob("*")):
        if not file.is_file():
            continue
        relative = file.relative_to(MEDIA_DIR).as_posix()
        if relative in in_use:
            continue
        try:
            file.unlink()
        except OSError:
            continue
        removed.append(relative)
    return removed


def delete_uploaded_card(db: Session, kind: str, name: str) -> list[str]:
    # Toglie una carta caricata dalla pool di base del tipo e poi cancella i file rimasti
    # senza uso (di norma quello della carta, se nessun campionato la possiede ancora).
    # Le copie nelle pool dei campionati e negli inventari non cambiano.
    # Ritorna i percorsi dei file cancellati.
    # Errori: CardNotFoundError, CardNotDeletableError, PoolNotFoundError.
    if kind not in POOL_KINDS:
        raise CardNotFoundError
    pool = get_base_pool(db, kind)
    cards = pool_cards(pool)
    target = next((card for card in cards if card_key(card.name) == card_key(name)), None)
    if target is None:
        raise CardNotFoundError
    if not target.path.startswith(uploads_prefix(kind)):
        raise CardNotDeletableError
    pool.base_cards = dump_cards([card for card in cards if card is not target])
    db.commit()
    return remove_orphan_uploads(db)
