from sqlalchemy import select
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import Session
from sqlalchemy.orm.exc import StaleDataError

from app.db.models import User
from app.db.models.championship import Championship, ChampionshipPilot
from app.db.models.deck import Deck
from app.db.models.pilot import Pilot
from app.db.models.race import Race
from app.services.cards import (
    MAX_GAME_DECK_CARDS,
    CardEntry,
    card_key,
    dump_cards,
    parse_cards,
)
from app.services.pilots import get_own_pilot
from app.services.sqlite_write_lock import SQLiteWriteLockError, acquire_sqlite_write_lock

# Tentativi di spostamento se un'altra richiesta modifica gli stessi mazzi nel frattempo.
MAX_MOVE_ATTEMPTS = 3


class PilotCardNotFoundError(Exception):
    """La carta non è nel mazzo da cui si vuole spostarla."""


class GameDeckFullError(Exception):
    """Il mazzo da gioco ha già il massimo di carte."""


class ConcurrentUpdateError(Exception):
    """Conflitto di versioni o lock: lo spostamento non e' stato completato."""


class RaceInProgressError(Exception):
    """Una gara del campionato del pilota non è ancora confermata: il mazzo è in sola lettura."""


def active_championships(db: Session, pilot_ids: list[int]) -> dict[int, tuple[int, str]]:
    # Per ogni pilota iscritto a un campionato non chiuso: {pilot_id: (id, nome)}.
    # Una sola query per tutti i piloti, qualunque sia il loro numero.
    if not pilot_ids:
        return {}
    stmt = (
        select(ChampionshipPilot.pilot_id, Championship.id, Championship.name)
        .join(Championship, Championship.id == ChampionshipPilot.championship_id)
        .where(ChampionshipPilot.pilot_id.in_(pilot_ids), Championship.is_closed.is_(False))
        .order_by(Championship.id)
    )
    result: dict[int, tuple[int, str]] = {}
    for pilot_id, championship_id, name in db.execute(stmt):
        result.setdefault(pilot_id, (championship_id, name))
    return result


def active_championship(db: Session, pilot: Pilot) -> tuple[int, str] | None:
    # Il campionato attivo di un solo pilota, come (id, nome), se c'è (solo informativo).
    return active_championships(db, [pilot.id]).get(pilot.id)


def has_race_in_progress(db: Session, pilot: Pilot) -> bool:
    # Vero se il pilota è iscritto a un campionato non chiuso che ha una gara con la
    # revisione non ancora confermata (review_closed_at vuota). Comprende la gara in
    # corso, quella da rivedere e quella in revisione; tra la conferma di una gara e la
    # creazione della successiva il mazzo si può modificare. Una sola query.
    stmt = (
        select(Race.id)
        .join(Championship, Championship.id == Race.championship_id)
        .join(ChampionshipPilot, ChampionshipPilot.championship_id == Race.championship_id)
        .where(
            ChampionshipPilot.pilot_id == pilot.id,
            Championship.is_closed.is_(False),
            Race.review_closed_at.is_(None),
        )
        .limit(1)
    )
    return db.scalar(stmt) is not None


def _take_one(cards: list[CardEntry], path: str) -> CardEntry:
    # Toglie una copia della carta indicata dal percorso e restituisce la carta spostata.
    for index, card in enumerate(cards):
        if card.path == path:
            moved = CardEntry(name=card.name, path=card.path, copies=1)
            if card.copies > 1:
                cards[index] = CardEntry(name=card.name, path=card.path, copies=card.copies - 1)
            else:
                del cards[index]
            return moved
    raise PilotCardNotFoundError


def _put_one(cards: list[CardEntry], moved: CardEntry) -> None:
    # Aggiunge una copia: si somma alla carta con lo stesso nome, altrimenti si accoda.
    key = card_key(moved.name)
    for index, card in enumerate(cards):
        if card_key(card.name) == key:
            cards[index] = CardEntry(name=card.name, path=card.path, copies=card.copies + 1)
            return
    cards.append(moved)


def move_card(db: Session, user: User, pilot_id: int, path: str, to_game: bool) -> Pilot:
    """Sposta una copia con lock precedente alle letture di stato e mazzi.

    Parametri: sessione, proprietario, pilota, percorso e direzione verso il mazzo.
    Ritorno: pilota dopo commit. Errori di dominio e SQL causano rollback completo.
    Mantiene massimo 15 e blocco gara/revisione. Conserva i tentativi preesistenti
    solo per StaleDataError; lock occupato restituisce conflitto senza retry.
    Errori: PilotNotFoundError, RaceInProgressError, PilotCardNotFoundError,
    GameDeckFullError, ConcurrentUpdateError; altri errori SQL propagano.
    """
    for _ in range(MAX_MOVE_ATTEMPTS):
        try:
            acquire_sqlite_write_lock(db)
            pilot = get_own_pilot(db, user, pilot_id)
            if has_race_in_progress(db, pilot):
                raise RaceInProgressError
            inventory_deck = db.get(Deck, pilot.inventory_deck_id)
            game_deck = db.get(Deck, pilot.game_deck_id)
            inventory = parse_cards(inventory_deck.cards)
            game = parse_cards(game_deck.cards)
            source, target = (inventory, game) if to_game else (game, inventory)
            if to_game and sum(card.copies for card in game) >= MAX_GAME_DECK_CARDS:
                raise GameDeckFullError
            _put_one(target, _take_one(source, path))
            inventory_deck.cards = dump_cards(inventory)
            game_deck.cards = dump_cards(game)
            db.commit()
            db.refresh(pilot)
            return pilot
        except StaleDataError:
            db.rollback()
            continue
        except SQLiteWriteLockError as exc:
            db.rollback()
            raise ConcurrentUpdateError from exc
        except OperationalError as exc:
            db.rollback()
            code = getattr(exc.orig, "sqlite_errorcode", 0) or 0
            if code & 255 in (5, 6):
                raise ConcurrentUpdateError from exc
            raise
        except Exception:
            db.rollback()
            raise
    raise ConcurrentUpdateError
