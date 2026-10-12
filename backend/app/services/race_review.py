from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.db.models.race import Race
from app.services.championships import ChampionshipClosedError, get_championship
from app.services.races import RaceNotFoundError, count_participants, get_race
from app.services.shop_purchase import _lock_database


class RaceNotInProgressError(Exception):
    """La gara ha già i risultati: non si può più aprire o chiudere la revisione."""


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


def start_review(db: Session, championship_id: int, race_id: int) -> Race:
    # Porta la gara in revisione. Se è già in revisione non cambia nulla (resta la data
    # originale). Un solo commit; in caso di errore non cambia nulla.
    # Errori: quelli di _open_race.
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
    # Riporta la gara allo stato "in corso", com'era prima della revisione: le giocate
    # non cambiano. Se non è in revisione non cambia nulla.
    # Errori: quelli di _open_race.
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
