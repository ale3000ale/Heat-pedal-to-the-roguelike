from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import User
from app.db.models.card_play import STATUS_PLAYED, STATUS_UNDONE, CardPlay
from app.db.models.deck import Deck
from app.db.models.pilot import Pilot
from app.db.models.race import Race
from app.services.card_gift import _with_one_more_copy, _without_one_copy
from app.services.card_play import CardNotAvailableError
from app.services.cards import CardEntry, card_key, dump_cards, parse_cards
from app.services.championships import get_championship
from app.services.pilots import PilotNotFoundError
from app.services.race_review import (
    ReviewHeldByOtherError,
    ReviewNotActiveError,
    _closed_race,
    is_review_active,
)
from app.services.races import get_race
from app.services.shop_purchase import _lock_database
from app.services.shop_view import PilotNotEnrolledError, is_enrolled


class CardPlayNotFoundError(Exception):
    """La giocata non esiste o appartiene a un'altra gara."""


class CardPlayNotActiveError(Exception):
    """La giocata non è attiva: è già annullata o consumata."""


class CardNotRemovableError(Exception):
    """La carta non si può togliere dall'inventario del pilota (il messaggio dice perché)."""


def _reviewed_race(db: Session, championship_id: int, race_id: int, user: User) -> Race:
    # Gara con i risultati e revisione delle carte attiva, aperta da questo utente.
    # Errori: ChampionshipNotFoundError, RaceNotFoundError, ChampionshipClosedError,
    # RaceNotClosedError, ReviewAlreadyConfirmedError, ReviewNotActiveError,
    # ReviewHeldByOtherError.
    race = _closed_race(db, championship_id, race_id)
    if not is_review_active(race):
        raise ReviewNotActiveError
    if race.review_started_by_user_id != user.id:
        raise ReviewHeldByOtherError
    return race


def get_card_summary(
    db: Session, championship_id: int, race_id: int
) -> list[tuple[Pilot, list[CardPlay]]]:
    # Giocate di tutti i piloti nella gara, raggruppate per pilota e in ordine cronologico.
    # Errori: ChampionshipNotFoundError, RaceNotFoundError.
    get_championship(db, championship_id)
    race = get_race(db, championship_id, race_id)
    plays = db.scalars(select(CardPlay).where(CardPlay.race_id == race.id).order_by(CardPlay.id))
    grouped: dict[int, list[CardPlay]] = {}
    for play in plays:
        grouped.setdefault(play.pilot_id, []).append(play)
    return [(db.get(Pilot, pilot_id), items) for pilot_id, items in grouped.items()]


def cancel_play(
    db: Session, championship_id: int, race_id: int, play_id: int, user: User
) -> CardPlay:
    # Il revisore annulla una giocata attiva: resta nello storico con stato "annullata" e
    # la carta resta al pilota. Possibile solo con la revisione attiva. Un solo commit.
    # Errori: quelli di _reviewed_race, CardPlayNotFoundError, CardPlayNotActiveError.
    try:
        _lock_database(db)
        race = _reviewed_race(db, championship_id, race_id, user)
        play = db.get(CardPlay, play_id)
        if play is None or play.race_id != race.id:
            raise CardPlayNotFoundError
        if play.status != STATUS_PLAYED:
            raise CardPlayNotActiveError
        play.status = STATUS_UNDONE
        db.commit()
        db.refresh(play)
    except Exception:
        db.rollback()
        raise
    return play


def grant_bonus(
    db: Session, championship_id: int, race_id: int, pilot_id: int, card_name: str, user: User
) -> tuple[Pilot, CardEntry]:
    # Bonus del revisore per correggere errori: una copia dalla pool all'inventario del
    # pilota, senza notifica. Possibile solo con la revisione attiva. Un solo commit.
    # Errori: quelli di _reviewed_race, PilotNotFoundError, PilotNotEnrolledError,
    # CardNotAvailableError.
    try:
        _lock_database(db)
        _reviewed_race(db, championship_id, race_id, user)
        championship = get_championship(db, championship_id)
        pilot = db.get(Pilot, pilot_id)
        if pilot is None or pilot.deleted_at is not None:
            raise PilotNotFoundError
        if not is_enrolled(db, championship_id, pilot.id):
            raise PilotNotEnrolledError
        pool_deck = db.get(Deck, championship.sponsor_pool_deck_id) if championship.sponsor_pool_deck_id else None
        pool = parse_cards(pool_deck.cards) if pool_deck else []
        key = card_key(card_name)
        picked = next((card for card in pool if card_key(card.name) == key), None)
        if picked is None:
            raise CardNotAvailableError
        inventory_deck = db.get(Deck, pilot.sponsor_inventory_deck_id)
        inventory_deck.cards = dump_cards(_with_one_more_copy(parse_cards(inventory_deck.cards), picked))
        pool_deck.cards = dump_cards(_without_one_copy(pool, picked))
        db.commit()
    except Exception:
        db.rollback()
        raise
    return pilot, picked


def _active_copies(db: Session, race_id: int, pilot_id: int, card_name: str) -> int:
    # Copie della carta impegnate in giocate attive del pilota nella gara.
    key = card_key(card_name)
    plays = db.scalars(
        select(CardPlay).where(
            CardPlay.race_id == race_id,
            CardPlay.pilot_id == pilot_id,
            CardPlay.status == STATUS_PLAYED,
        )
    )
    return sum(1 for play in plays if card_key(play.card_name) == key)


def remove_card(
    db: Session, championship_id: int, race_id: int, pilot_id: int, card_name: str, user: User
) -> tuple[Pilot, CardEntry]:
    # Il revisore toglie una copia dall'inventario sponsor del pilota e la rimette nella
    # pool sponsor del campionato (inverso del bonus). Possibile solo con la revisione
    # attiva e se almeno una copia non è impegnata in una giocata attiva. Un solo commit.
    # Errori: quelli di _reviewed_race, PilotNotFoundError, PilotNotEnrolledError,
    # CardNotRemovableError (pool assente, carta non in inventario, copie tutte in gioco).
    try:
        _lock_database(db)
        race = _reviewed_race(db, championship_id, race_id, user)
        championship = get_championship(db, championship_id)
        pilot = db.get(Pilot, pilot_id)
        if pilot is None or pilot.deleted_at is not None:
            raise PilotNotFoundError
        if not is_enrolled(db, championship_id, pilot.id):
            raise PilotNotEnrolledError
        pool_deck = db.get(Deck, championship.sponsor_pool_deck_id) if championship.sponsor_pool_deck_id else None
        if pool_deck is None:
            raise CardNotRemovableError("Il campionato non ha una pool sponsor")
        inventory_deck = db.get(Deck, pilot.sponsor_inventory_deck_id)
        inventory = parse_cards(inventory_deck.cards)
        key = card_key(card_name)
        held = next((card for card in inventory if card_key(card.name) == key), None)
        if held is None:
            raise CardNotRemovableError("La carta non è nell'inventario sponsor del pilota")
        if held.copies <= _active_copies(db, race.id, pilot.id, held.name):
            raise CardNotRemovableError("Tutte le copie della carta sono in gioco")
        one = CardEntry(name=held.name, path=held.path, copies=1)
        inventory_deck.cards = dump_cards(_without_one_copy(inventory, one))
        pool_deck.cards = dump_cards(_with_one_more_copy(parse_cards(pool_deck.cards), one))
        db.commit()
    except Exception:
        db.rollback()
        raise
    return pilot, one
