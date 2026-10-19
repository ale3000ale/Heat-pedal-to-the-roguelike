from datetime import datetime, timedelta, timezone

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.db.models import User
from app.db.models.race import Race
from app.services.card_play_close import consume_plays
from app.services.cards import CardError
from app.services.championships import ChampionshipClosedError, get_championship
from app.services.races import RaceNotFoundError, count_participants, get_race
from app.services.shop_purchase import _lock_database

REVIEW_MINUTES = 15


class RaceNotInProgressError(Exception):
    """La gara ha già i risultati."""


class RaceNotClosedError(Exception):
    """La gara non ha ancora i risultati."""


class ReviewAlreadyConfirmedError(Exception):
    """La revisione è già confermata."""


class ReviewHeldByOtherError(Exception):
    """Un altro utente detiene la revisione."""


class ReviewNotActiveError(Exception):
    """Revisione non aperta o scaduta."""


class RaceNotLastError(Exception):
    """Solo l'ultima gara può essere riaperta."""


class ReviewNotConfirmedError(Exception):
    """La revisione non è ancora confermata."""


class ReviewReopenForbiddenError(Exception):
    """Solo l'admin può riaprire una revisione confermata."""


def _utc(value: datetime) -> datetime:
    return value if value.tzinfo is not None else value.replace(tzinfo=timezone.utc)


def is_review_active(race: Race, now: datetime | None = None) -> bool:
    if race.review_started_at is None or race.review_closed_at is not None:
        return False
    return (now or datetime.now(timezone.utc)) - _utc(race.review_started_at) < timedelta(minutes=REVIEW_MINUTES)


def is_last_race(db: Session, race: Race) -> bool:
    last = db.scalar(select(func.max(Race.number)).where(Race.championship_id == race.championship_id))
    return last == race.number


def _open_race(db: Session, championship_id: int, race_id: int) -> Race:
    championship = get_championship(db, championship_id)
    race = get_race(db, championship_id, race_id)
    if championship.is_closed:
        raise ChampionshipClosedError
    if count_participants(db, race.id) > 0:
        raise RaceNotInProgressError
    return race


def _closed_race(db: Session, championship_id: int, race_id: int) -> Race:
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
    """Apre o riprende la revisione dell'utente; rollback in caso di conflitto."""
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
    """Rinuncia senza cambiare le carte; restituisce la gara o un errore di stato/titolare."""
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


def confirm_review(db: Session, championship_id: int, race_id: int, user: User, is_admin: bool) -> Race:
    """Conferma legacy senza conteggi; consuma le giocate con un unico commit."""
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


def settle_expired_reviews(db: Session, championship_id: int, now: datetime | None = None) -> int:
    """Chiude le revisioni scadute e restituisce quante sono state chiuse.

    Con bozza applica solo le carte coerenti; senza bozza usa la chiusura
    legacy. Ogni gara ha una transazione distinta. CardError lascia la gara
    intatta e aperta; gli altri errori fanno rollback e vengono propagati.
    La scadenza è elaborata quando il servizio viene chiamato, non da un job.
    """
    get_championship(db, championship_id)
    stmt = select(Race).where(
        Race.championship_id == championship_id,
        Race.review_closed_at.is_(None),
        Race.review_started_at.is_not(None),
    )
    candidates = [race.id for race in db.scalars(stmt)
                  if count_participants(db, race.id) > 0 and not is_review_active(race, now)]
    db.rollback()
    settled = 0
    for race_id in candidates:
        try:
            _lock_database(db)
            championship = get_championship(db, championship_id)
            race = db.get(Race, race_id)
            if race.review_closed_at is not None or is_review_active(race, now):
                db.rollback()
                continue
            if race.review_draft:
                # Import locale: evita il ciclo con i servizi dei conteggi.
                from app.services.review_expiry import apply_expired_draft
                apply_expired_draft(db, race)
            else:
                consume_plays(db, race.id, championship.sponsor_pool_deck_id)
            race.review_closed_at = now or datetime.now(timezone.utc)
            db.commit()
            settled += 1
        except CardError:
            db.rollback()
        except Exception:
            db.rollback()
            raise
    return settled


def reopen_review(db: Session, championship_id: int, race_id: int, user: User, is_admin: bool) -> Race:
    """Riapre l'ultima gara confermata per l'admin; restituisce la gara o errore di stato."""
    try:
        _lock_database(db)
        if not is_admin:
            raise ReviewReopenForbiddenError
        championship = get_championship(db, championship_id)
        race = get_race(db, championship_id, race_id)
        if championship.is_closed:
            raise ChampionshipClosedError
        if count_participants(db, race.id) == 0:
            raise RaceNotClosedError
        if race.review_closed_at is None:
            raise ReviewNotConfirmedError
        if not is_last_race(db, race):
            raise RaceNotLastError
        race.review_closed_at = None
        race.review_started_at = datetime.now(timezone.utc)
        race.review_started_by_user_id = user.id
        db.commit()
        db.refresh(race)
    except Exception:
        db.rollback()
        raise
    return race


def start_review(db: Session, championship_id: int, race_id: int) -> Race:
    """Blocca le giocate nella gara senza risultati; restituisce la gara senza riavviare il timer."""
    try:
        _lock_database(db)
        race = _open_race(db, championship_id, race_id)
        if race.review_started_at is None:
            race.review_started_at = datetime.now(timezone.utc)
        db.commit()
        db.refresh(race)
    except Exception:
        db.rollback()
        raise
    return race


def cancel_review(db: Session, championship_id: int, race_id: int) -> Race:
    """Riporta in corso la gara senza risultati; giocate invariate, rollback su errore."""
    try:
        _lock_database(db)
        race = _open_race(db, championship_id, race_id)
        race.review_started_at = None
        db.commit()
        db.refresh(race)
    except Exception:
        db.rollback()
        raise
    return race
