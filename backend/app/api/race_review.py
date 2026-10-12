from fastapi import APIRouter, HTTPException, status

from app.api.deps import DbDep, JudgeUser
from app.db.models.race import Race
from app.schemas.race_review import RaceReviewRead
from app.services.championships import ChampionshipClosedError, ChampionshipNotFoundError
from app.services.race_review import RaceNotInProgressError, cancel_review, start_review
from app.services.races import RaceNotFoundError

router = APIRouter(tags=["race-review"])

DOMAIN_ERRORS = (
    ChampionshipNotFoundError,
    RaceNotFoundError,
    ChampionshipClosedError,
    RaceNotInProgressError,
)


def _read(race: Race) -> RaceReviewRead:
    return RaceReviewRead(
        race_id=race.id,
        in_review=race.review_started_at is not None,
        review_started_at=race.review_started_at,
    )


def _http_error(exc: Exception) -> HTTPException:
    # Traduce gli errori di dominio in risposte HTTP leggibili.
    if isinstance(exc, ChampionshipNotFoundError):
        return HTTPException(status.HTTP_404_NOT_FOUND, "Campionato non trovato")
    if isinstance(exc, RaceNotFoundError):
        return HTTPException(status.HTTP_404_NOT_FOUND, "Gara non trovata")
    if isinstance(exc, ChampionshipClosedError):
        return HTTPException(status.HTTP_409_CONFLICT, "Campionato chiuso")
    if isinstance(exc, RaceNotInProgressError):
        return HTTPException(status.HTTP_409_CONFLICT, "La gara è già chiusa")
    raise exc


@router.post("/{championship_id}/races/{race_id}/review", response_model=RaceReviewRead)
def open_review(championship_id: int, race_id: int, judge: JudgeUser, db: DbDep):
    # Porta la gara in revisione (giudice o admin): i giocatori non possono più giocare.
    try:
        return _read(start_review(db, championship_id, race_id))
    except DOMAIN_ERRORS as exc:
        raise _http_error(exc)


@router.delete("/{championship_id}/races/{race_id}/review", response_model=RaceReviewRead)
def close_review(championship_id: int, race_id: int, judge: JudgeUser, db: DbDep):
    # Riporta la gara in corso (giudice o admin), come prima della revisione.
    try:
        return _read(cancel_review(db, championship_id, race_id))
    except DOMAIN_ERRORS as exc:
        raise _http_error(exc)
