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

# Dopo questo tempo dall'apertura la revisione scade e viene confermata così com'è.
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
    """La revisione non è aperta o è scaduta."""


class RaceNotLastError(Exception):
    """Solo l'ultima gara del campionato si può rivedere di nuovo."""


class ReviewNotConfirmedError(Exception):
    """La revisione non è ancora stata confermata: non c'è nulla da riaprire."""


class ReviewReopenForbiddenError(Exception):
    """Solo l'admin può riaprire una revisione già confermata."""


def _utc(value: datetime) -> datetime:
    # SQLite restituisce date senza fuso: si considerano in UTC.
    return value if value.tzinfo is not None else value.replace(tzinfo=timezone.utc)


def is_review_active(race: Race, now: datetime | None = None) -> bool:
    # Vera se la revisione è stata aperta da meno di REVIEW_MINUTES e non è confermata.
    # Una revisione scaduta non è più attiva, senza scrivere nulla nel database.
    if race.review_started_at is None or race.review_closed_at is not None:
        return False
    current = now or datetime.now(timezone.utc)
    return current - _utc(race.review_started_at) < timedelta(minutes=REVIEW_MINUTES)


def is_last_race(db: Session, race: Race) -> bool:
    # Vera se la gara ha il numero più alto del suo campionato.
    last = db.scalar(select(func.max(Race.number)).where(Race.championship_id == race.championship_id))
    return last == race.number


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
    # sua. Se è aperta da un altro e non è scaduta, nessuno può prenderla (nemmeno l'admin).
    # Un solo commit.
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
    # il revisore; con la revisione scaduta o mai aperta solo l'admin. Un solo commit: in
    # caso di errore carte e gara non cambiano.
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


def settle_expired_reviews(
    db: Session, championship_id: int, now: datetime | None = None
) -> int:
    # Conferma così com'è ogni revisione scaduta del campionato: le giocate non annullate
    # vengono consumate e la gara si chiude. Va chiamata prima di leggere lo stato di una
    # revisione e prima di creare una nuova gara. Ogni gara ha il suo commit; se una carta
    # giocata non è più nell'inventario quella gara resta com'è e la sistema l'admin.
    # Ritorna: il numero di revisioni confermate.
    # Errori: ChampionshipNotFoundError.
    get_championship(db, championship_id)
    stmt = select(Race).where(
        Race.championship_id == championship_id,
        Race.review_closed_at.is_(None),
        Race.review_started_at.is_not(None),
    )
    candidates = [
        race.id
        for race in db.scalars(stmt)
        if count_participants(db, race.id) > 0 and not is_review_active(race, now)
    ]
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


def reopen_review(
    db: Session, championship_id: int, race_id: int, user: User, is_admin: bool
) -> Race:
    # L'admin riapre la revisione di una gara già confermata, solo se è l'ultima del
    # campionato: da quel momento è lui il revisore, con 15 minuti di tempo. Un solo commit.
    # Errori: ChampionshipNotFoundError, RaceNotFoundError, ChampionshipClosedError,
    # ReviewReopenForbiddenError, RaceNotClosedError, ReviewNotConfirmedError,
    # RaceNotLastError.
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
