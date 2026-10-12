from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models.card_play import STATUS_PLAYED, STATUS_UNDONE, CardPlay
from app.db.models.deck import Deck
from app.db.models.pilot import Pilot
from app.services.card_gift import _with_one_more_copy, _without_one_copy
from app.services.card_play import CardNotAvailableError
from app.services.cards import CardEntry, card_key, dump_cards, parse_cards
from app.services.championships import ChampionshipClosedError, get_championship
from app.services.pilots import PilotNotFoundError
from app.services.race_review import _open_race
from app.services.races import get_race
from app.services.shop_purchase import _lock_database
from app.services.shop_view import PilotNotEnrolledError, is_enrolled


class CardPlayNotFoundError(Exception):
    """La giocata non esiste o appartiene a un'altra gara."""


class CardPlayNotActiveError(Exception):
    """La giocata non è attiva: è già annullata o consumata."""


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


def cancel_play(db: Session, championship_id: int, race_id: int, play_id: int) -> CardPlay:
    # Il giudice annulla una giocata attiva: resta nello storico con stato "annullata".
    # Possibile solo finché la gara non ha risultati. Un solo commit.
    # Errori: quelli di _open_race, CardPlayNotFoundError, CardPlayNotActiveError.
    try:
        _lock_database(db)
        race = _open_race(db, championship_id, race_id)
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
    db: Session, championship_id: int, race_id: int, pilot_id: int, card_name: str
) -> tuple[Pilot, CardEntry]:
    # Bonus del giudice per correggere errori: una copia dalla pool all'inventario del
    # pilota, senza notifica. Un solo commit.
    # Errori: ChampionshipNotFoundError, RaceNotFoundError, ChampionshipClosedError,
    # PilotNotFoundError, PilotNotEnrolledError, CardNotAvailableError.
    try:
        _lock_database(db)
        championship = get_championship(db, championship_id)
        get_race(db, championship_id, race_id)
        if championship.is_closed:
            raise ChampionshipClosedError
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
