from dataclasses import dataclass, field

from pydantic import ValidationError
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.config import MEDIA_DIR
from app.db.models import Championship
from app.db.models.deck import Deck, DeckPrototype
from app.services.cards import (
    CardEntry,
    CardError,
    card_key,
    dump_cards,
    parse_card_filename,
    parse_cards,
)
from app.services.names import clean_name

# Tipi di pool e nome della rispettiva pool di base: il catalogo completo da cui
# nascono tutte le altre pool dello stesso tipo.
POOL_KINDS = ("modifiche", "sponsor")
BASE_POOL_NAMES = {"modifiche": "default", "sponsor": "sponsor"}
BASE_POOL_NAME = BASE_POOL_NAMES["modifiche"]

IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp"}


class PoolNotFoundError(Exception):
    """La pool non esiste."""


class PoolNameTakenError(Exception):
    """Esiste già una pool con questo nome (senza distinguere le maiuscole)."""


class PoolProtectedError(Exception):
    """Le pool di base non si possono eliminare."""


class PoolRuleError(ValueError):
    """La scelta delle carte non rispetta la pool di base (messaggio leggibile)."""


@dataclass
class ReloadResult:
    # Esito della ricarica: carte aggiunte, carte rimosse perché il file non esiste più
    # (nomi e, in parallelo, percorsi), carte già presenti e file scartati.
    added: list[str] = field(default_factory=list)
    removed: list[str] = field(default_factory=list)
    removed_paths: list[str] = field(default_factory=list)
    already_present: int = 0
    warnings: list[str] = field(default_factory=list)


@dataclass
class RemovedCard:
    # Carta che la ricarica toglierebbe; `in_use` è vero se è nella copia di pool di un
    # campionato attivo.
    name: str
    in_use: bool


@dataclass
class ReloadPreview:
    # Anteprima della ricarica: nulla è stato scritto nel database.
    added: list[str]
    removed: list[RemovedCard]
    warnings: list[str]


def list_pools(db: Session) -> list[DeckPrototype]:
    # Tutte le pool, dalla più vecchia alla più recente.
    return list(db.scalars(select(DeckPrototype).order_by(DeckPrototype.id)))


def get_pool(db: Session, pool_id: int) -> DeckPrototype:
    pool = db.get(DeckPrototype, pool_id)
    if pool is None:
        raise PoolNotFoundError
    return pool


def get_base_pool(db: Session, kind: str = "modifiche") -> DeckPrototype:
    # Pool di base del tipo richiesto (le modifiche se il tipo è omesso).
    name = BASE_POOL_NAMES.get(kind)
    if name is None:
        raise PoolNotFoundError
    pool = db.scalar(select(DeckPrototype).where(DeckPrototype.name == name))
    if pool is None:
        raise PoolNotFoundError
    return pool


def pool_for_kind(db: Session, pool_id: int | None, kind: str) -> DeckPrototype:
    # La pool scelta (o quella di base se omessa), che deve essere del tipo richiesto.
    if pool_id is None:
        return get_base_pool(db, kind)
    pool = get_pool(db, pool_id)
    if pool.kind != kind:
        raise PoolRuleError(f"La pool scelta non è di tipo {kind}")
    return pool


def pool_cards(pool: DeckPrototype) -> list[CardEntry]:
    return parse_cards(pool.base_cards)


def create_pool(
    db: Session, name: str, choices: list[tuple[str, int]], kind: str = "modifiche"
) -> DeckPrototype:
    # Crea una pool scegliendo carte e copie dalla pool di base dello stesso tipo. Nome,
    # percorso e grafia delle carte sono quelli della base; le copie non possono superarla.
    name = clean_name(name)
    if any(pool.name.casefold() == name.casefold() for pool in list_pools(db)):
        raise PoolNameTakenError
    base = {card_key(card.name): card for card in pool_cards(get_base_pool(db, kind))}
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
    pool = DeckPrototype(name=name, base_cards=dump_cards(chosen), kind=kind)
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
    if pool.name in BASE_POOL_NAMES.values():
        raise PoolProtectedError
    db.delete(pool)
    db.commit()


def _drop_missing(
    cards: list[CardEntry], existing_paths: set[str], kind: str, result: ReloadResult
) -> list[CardEntry]:
    # Toglie le carte della cartella <tipo> il cui file non esiste più e ne annota nome e
    # percorso in result.removed e result.removed_paths. Le carte con un percorso fuori da
    # quella cartella non si toccano.
    prefix = f"cards/base/{kind}/"
    kept: list[CardEntry] = []
    for card in cards:
        if card.path.startswith(prefix) and card.path not in existing_paths:
            result.removed.append(card.name)
            result.removed_paths.append(card.path)
        else:
            kept.append(card)
    return kept


def reload_base_pool(db: Session, kind: str, apply: bool = True) -> ReloadResult:
    # Sincronizza una pool di base con la sua cartella (backend/media/cards/base/<tipo>).
    # Le carte già presenti (stesso nome, senza distinguere le maiuscole, oppure stesso
    # percorso) non si toccano, così nomi e copie corretti a mano si conservano. Le carte
    # nuove vanno in fondo. Le carte il cui file non esiste più vengono tolte dal database.
    # Se la cartella manca o non contiene immagini non si toglie nulla.
    # Con apply=False calcola l'esito senza scrivere nel database (anteprima).
    pool = get_base_pool(db, kind)
    result = ReloadResult()
    folder = MEDIA_DIR / "cards" / "base" / kind
    if not folder.is_dir():
        result.warnings.append(f"Cartella non trovata: cards/base/{kind}")
        return result

    cards = pool_cards(pool)
    files = sorted(
        path
        for path in folder.iterdir()
        if path.is_file() and path.suffix.lower() in IMAGE_EXTENSIONS
    )
    if files:
        existing_paths = {f"cards/base/{kind}/{path.name}" for path in files}
        cards = _drop_missing(cards, existing_paths, kind, result)
    elif cards:
        result.warnings.append(
            f"Nessuna immagine in cards/base/{kind}: nessuna carta è stata rimossa"
        )

    names = {card_key(card.name) for card in cards}
    paths = {card.path for card in cards}
    webp_stems = {path.stem.casefold() for path in files if path.suffix.lower() == ".webp"}

    for path in files:
        if path.suffix.lower() != ".webp":
            # Si usano solo i WebP: un altro formato senza il suo WebP va ridimensionato.
            if path.stem.casefold() not in webp_stems:
                result.warnings.append(
                    f"{path.name}: non è WebP, esegui resize_cards e ricarica"
                )
            continue
        try:
            name, copies = parse_card_filename(path.name)
            entry = CardEntry(
                name=name, path=f"cards/base/{kind}/{path.name}", copies=copies
            )
        except CardError as exc:
            result.warnings.append(f"{path.name}: scartato ({exc})")
            continue
        except ValidationError:
            result.warnings.append(f"{path.name}: scartato (nome o copie fuori dai limiti)")
            continue
        if card_key(entry.name) in names or entry.path in paths:
            result.already_present += 1
            continue
        cards.append(entry)
        names.add(card_key(entry.name))
        paths.add(entry.path)
        result.added.append(entry.name)

    if apply and (result.added or result.removed):
        pool.base_cards = dump_cards(cards)
        db.commit()
    return result


def _active_championship_paths(db: Session, kind: str) -> set[str]:
    # Percorsi delle carte presenti nella copia di pool (del tipo richiesto) di ogni
    # campionato attivo.
    column = Championship.pool_deck_id if kind == "modifiche" else Championship.sponsor_pool_deck_id
    deck_ids = list(
        db.scalars(select(column).where(Championship.is_closed.is_(False), column.is_not(None)))
    )
    paths: set[str] = set()
    for deck_id in deck_ids:
        deck = db.get(Deck, deck_id)
        if deck is not None:
            paths.update(card.path for card in parse_cards(deck.cards))
    return paths


def preview_reload(db: Session, kind: str) -> ReloadPreview:
    # Anteprima della ricarica: cosa verrebbe aggiunto e quali carte verrebbero tolte,
    # con l'indicazione di quelle presenti nella copia di pool di un campionato attivo.
    # Non scrive nel database. Errori: PoolNotFoundError.
    result = reload_base_pool(db, kind, apply=False)
    in_use_paths = _active_championship_paths(db, kind) if result.removed_paths else set()
    removed = [
        RemovedCard(name=name, in_use=path in in_use_paths)
        for name, path in zip(result.removed, result.removed_paths)
    ]
    return ReloadPreview(added=result.added, removed=removed, warnings=result.warnings)
