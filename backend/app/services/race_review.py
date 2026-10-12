from datetime import datetime, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import User
from app.db.models.race import Race, RaceResult
from app.services.championships import ChampionshipClosedError, get_championship
from app.services.races import get_race

# Un blocco non rinnovato per questo tempo scade da solo: un giudice che chiude il
# browser non lascia la gara bloccata per sempre.
REVIEW_TIMEOUT = timedelta(minutes=30)


class RaceLockedError(Exception):
    """Un altro giudice sta già chiudendo la gara (judge_name è il suo nome)."""

    def __init__(self, judge_name: str):
        super().__init__(judge_name)
        self.judge_name = judge_name


class RaceNotInProgressError(Exception):
    """La gara ha già i risultati: non c'è più nulla da revisionare."""


class NotReviewerError(Exception):
    """Solo il giudice che ha il blocco, o l'admin, può liberarlo."""


def _now() -> datetime:
    # Il database salva gli orari UTC senza fuso.
    return datetime.now(timezone.utc).replace(tzinfo=None)


def active_reviewer(db: Session, race: Race) -> User | None:
    # Il giudice con un blocco valido, oppure None se non c'è o è scaduto.
    if race.reviewer_id is None or race.review_started_at is None:
        return None
    if _now() - race.review_started_at >= REVIEW_TIMEOUT:
        return None
    return db.get(User, race.reviewer_id)


def _has_results(db: Session, race: Race) -> bool:
    stmt = select(RaceResult.id).where(RaceResult.race_id == race.id).limit(1)
    return db.scalar(stmt) is not None


def open_review(db: Session, championship_id: int, race_id: int, user: User) -> Race:
    # Apre la revisione o, se il blocco è già di chi chiama, lo rinnova.
    # Errori: ChampionshipNotFoundError, RaceNotFoundError, ChampionshipClosedError,
    # RaceNotInProgressError, RaceLockedError.
    championship = get_championship(db, championship_id)
    race = get_race(db, championship_id, race_id)
    if championship.is_closed:
        raise ChampionshipClosedError
    if _has_results(db, race):
        raise RaceNotInProgressError
    holder = active_reviewer(db, race)
    if holder is not None and holder.id != user.id:
        raise RaceLockedError(holder.username)
    race.reviewer_id = user.id
    race.review_started_at = _now()
    db.commit()
    db.refresh(race)
    return race


def release_review(db: Session, championship_id: int, race_id: int, user: User) -> Race:
    # Libera il blocco: lo può fare chi lo possiede o l'admin. Se nessuno lo ha, non fa nulla.
    # Errori: ChampionshipNotFoundError, RaceNotFoundError, NotReviewerError.
    race = get_race(db, championship_id, race_id)
    holder = active_reviewer(db, race)
    if holder is not None and holder.id != user.id and user.role != "admin":
        raise NotReviewerError
    race.reviewer_id = None
    race.review_started_at = None
    db.commit()
    db.refresh(race)
    return race


def ensure_not_locked(db: Session, championship_id: int, race_id: int, user: User) -> None:
    # Impedisce di registrare i risultati se un altro giudice ha il blocco.
    # Errori: ChampionshipNotFoundError, RaceNotFoundError, RaceLockedError.
    race = get_race(db, championship_id, race_id)
    holder = active_reviewer(db, race)
    if holder is not None and holder.id != user.id:
        raise RaceLockedError(holder.username)


def clear_review(db: Session, championship_id: int, race_id: int) -> None:
    # Toglie il blocco dopo che i risultati sono stati salvati.
    race = get_race(db, championship_id, race_id)
    race.reviewer_id = None
    race.review_started_at = None
    db.commit()
