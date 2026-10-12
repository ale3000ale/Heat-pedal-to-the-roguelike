from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session

from app.db.models import User
from app.db.models.race import Race
from app.services.card_play_close import consume_plays
from app.services.championships import ChampionshipClosedError, get_championship
from app.services.races import RaceNotFoundError, count_participants, get_race
from app.services.shop_purchase import _lock_database

# Dopo questo tempo dall'apertura la revisione si libera e un altro giudice può prenderla.
REVIEW_MINUTES = 15


class RaceNotInProgressError(Exception):
    """La gara ha già i risultati: non si può più aprire o chiudere la revisione."""


class RaceNotClosedError(Exception):
    """La gara non ha ancora i risultati: la revisione delle carte non può iniziare."""


class ReviewAlreadyConfirmedError(Exception):
    """La revisione di questa gara è già stata confermata."""


class ReviewHeldByOtherError(Exception):
    """Un altro utente sta già facendo la revisione di questa gara."""


class ReviewNotActiveError(Exception):
    """La revisione non è aperta o è scaduta: va aperta di nuovo."""


def _utc(value: datetime) -> datetime:
    # SQLite restituisce date senza fuso: si considerano in UTC.
    return value if value.tzinfo is not None else value.replace(tzinfo=timezone.utc)


def is_review_active(race: Race, now: datetime | None = None) -> bool:
    # Vera se la revisione è stata aperta da meno di REVIEW_MINUTES e non è confermata.
    # Una revisione scaduta vale come non aperta, senza scrivere nulla nel database.
    if race.review_started_at is None or race.review_closed_at is not None:
        return False
    current = now or datetime.now(timezone.utc)
    return current - _utc(race.review_started_at) < timedelta(minutes=REVIEW_MINUTES)


def _open_race(db: Session, championship_id: int, race_id: int) -> Race:
    # Gara esistente, in un campionato attivo e ancora senza risultati.
    # Errori: ChampionshipNotFoundError, RaceNotFoundError, ChampionshipClosedError,
    # RaceNotInProgressError.
    championship = get_championship(db, championship_id)
    race = get_race(db, championship_id, race_id)
    if championship.is_closed:
        raise ChampionshipClosedError
    if count_participants(db, race.id) > 0:
        raise RaceNotInProgressError
    return race


def _closed_race(db: Session, championship_id: int, race_id: int) -> Race:
    # Gara con i risultati confermati e revisione delle carte ancora da concludere.
    # Errori: ChampionshipNotFoundError, RaceNotFoundError, ChampionshipClosedError,
    # RaceNotClosedError, ReviewAlreadyConfirmedError.
    championship = get_championship(db, championship_id)
    race = get_race(db, championship_id, race_id)
    if championship.is_closed:
        raise ChampionshipClosedError
    if count_participants(db, race.id) == 0:
        raise RaceNotClosedError
    if race.review_closed_at is not None:
        raise ReviewAlreadyConfirmedError
    return race


def _clear_review(race: Race) -> None:
    race.review_started_at = None
    race.review_started_by_user_id = None


def begin_review(db: Session, championship_id: int, race_id: int, user: User) -> Race:
    # Apre la revisione delle carte per l'utente (giudice o admin) o la riprende se è la
    # sua. Se è aperta da un altro e non è scaduta, nessuno può prenderla (nemmeno l'admin);
    # se è scaduta, riparte da zero con il nuovo revisore. Un solo commit.
    # Errori: quelli di _closed_race, ReviewHeldByOtherError.
    try:
        _lock_database(db)
        race = _closed_race(db, championship_id, race_id)
        if is_review_active(race):
            if race.review_started_by_user_id != user.id:
                raise ReviewHeldByOtherError
        else:
            race.review_started_at = datetime.now(timezone.utc)
            race.review_started_by_user_id = user.id
        db.commit()
        db.refresh(race)
    except Exception:
        db.rollback()
        raise
    return race


def abandon_review(db: Session, championship_id: int, race_id: int, user: User) -> Race:
    # Il revisore rinuncia alla revisione: le giocate non cambiano e la gara torna
    # "da rivedere". Un solo commit.
    # Errori: quelli di _closed_race, ReviewNotActiveError, ReviewHeldByOtherError.
    try:
        _lock_database(db)
        race = _closed_race(db, championship_id, race_id)
        if not is_review_active(race):
            raise ReviewNotActiveError
        if race.review_started_by_user_id != user.id:
            raise ReviewHeldByOtherError
        _clear_review(race)
        db.commit()
        db.refresh(race)
    except Exception:
        db.rollback()
        raise
    return race


def confirm_review(
    db: Session, championship_id: int, race_id: int, user: User, is_admin: bool
) -> Race:
    # Conferma la revisione: le carte giocate (non annullate) escono dall'inventario e
    # tornano nella pool, la gara si chiude del tutto. Con la revisione attiva conferma solo
    # il revisore; con la revisione scaduta o mai aperta confermano le giocate così come
    # sono, come se non servissero modifiche, solo l'admin. Un solo commit: in caso di
    # errore carte e gara non cambiano.
    # Errori: quelli di _closed_race, ReviewHeldByOtherError, ReviewNotActiveError,
    # CardError (carta giocata non più nell'inventario).
    try:
        _lock_database(db)
        championship = get_championship(db, championship_id)
        race = _closed_race(db, championship_id, race_id)
        if is_review_active(race):
            if race.review_started_by_user_id != user.id:
                raise ReviewHeldByOtherError
        elif not is_admin:
            raise ReviewNotActiveError
        consume_plays(db, race.id, championship.sponsor_pool_deck_id)
        race.review_closed_at = datetime.now(timezone.utc)
        db.commit()
        db.refresh(race)
    except Exception:
        db.rollback()
        raise
    return race
