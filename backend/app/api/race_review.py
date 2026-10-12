from fastapi import APIRouter, HTTPException, status

from app.api.deps import DbDep, JudgeUser
from app.db.models.race import Race
from app.schemas.card_judge import (
    CardBonusRead,
    CardBonusRequest,
    JudgePlayRead,
    PilotPlaysRead,
)
from app.schemas.race_review import RaceReviewRead
from app.services.card_judge import (
    CardPlayNotActiveError,
    CardPlayNotFoundError,
    cancel_play,
    get_card_summary,
    grant_bonus,
)
from app.services.card_play import CardNotAvailableError
from app.services.championships import ChampionshipClosedError, ChampionshipNotFoundError
from app.services.pilots import PilotNotFoundError
from app.services.race_review import RaceNotInProgressError, cancel_review, start_review
from app.services.races import RaceNotFoundError
from app.services.shop_view import PilotNotEnrolledError

router = APIRouter(tags=["race-review"])

DOMAIN_ERRORS = (
    ChampionshipNotFoundError,
    RaceNotFoundError,
    ChampionshipClosedError,
    RaceNotInProgressError,
    PilotNotFoundError,
    PilotNotEnrolledError,
    CardNotAvailableError,
    CardPlayNotFoundError,
    CardPlayNotActiveError,
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
    if isinstance(exc, PilotNotFoundError):
        return HTTPException(status.HTTP_404_NOT_FOUND, "Pilota non trovato")
    if isinstance(exc, CardPlayNotFoundError):
        return HTTPException(status.HTTP_404_NOT_FOUND, "Giocata non trovata")
    if isinstance(exc, PilotNotEnrolledError):
        return HTTPException(status.HTTP_403_FORBIDDEN, "Il pilota non è iscritto al campionato")
    if isinstance(exc, ChampionshipClosedError):
        return HTTPException(status.HTTP_409_CONFLICT, "Campionato chiuso")
    if isinstance(exc, RaceNotInProgressError):
        return HTTPException(status.HTTP_409_CONFLICT, "La gara è già chiusa")
    if isinstance(exc, CardNotAvailableError):
        return HTTPException(status.HTTP_409_CONFLICT, "Carta non disponibile nella pool")
    if isinstance(exc, CardPlayNotActiveError):
        return HTTPException(status.HTTP_409_CONFLICT, "La giocata non è più attiva")
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


@router.get("/{championship_id}/races/{race_id}/card-plays", response_model=list[PilotPlaysRead])
def read_card_summary(championship_id: int, race_id: int, judge: JudgeUser, db: DbDep):
    # Riepilogo delle carte giocate da tutti i piloti nella gara (giudice o admin).
    try:
        return [
            PilotPlaysRead(
                pilot_id=pilot.id,
                pilot_name=pilot.name,
                plays=[JudgePlayRead.model_validate(play) for play in plays],
            )
            for pilot, plays in get_card_summary(db, championship_id, race_id)
        ]
    except DOMAIN_ERRORS as exc:
        raise _http_error(exc)


@router.post(
    "/{championship_id}/races/{race_id}/card-plays/{play_id}/cancel",
    response_model=JudgePlayRead,
)
def cancel_card_play(
    championship_id: int, race_id: int, play_id: int, judge: JudgeUser, db: DbDep
):
    # Annulla una giocata attiva (giudice o admin), solo finché la gara non ha risultati.
    try:
        return JudgePlayRead.model_validate(cancel_play(db, championship_id, race_id, play_id))
    except DOMAIN_ERRORS as exc:
        raise _http_error(exc)


@router.post(
    "/{championship_id}/races/{race_id}/card-bonus",
    response_model=CardBonusRead,
    status_code=status.HTTP_201_CREATED,
)
def create_card_bonus(
    championship_id: int, race_id: int, data: CardBonusRequest, judge: JudgeUser, db: DbDep
):
    # Bonus del giudice: una copia dalla pool all'inventario del pilota, senza notifica.
    try:
        pilot, card = grant_bonus(db, championship_id, race_id, data.pilot_id, data.card_name)
        return CardBonusRead(pilot_id=pilot.id, card_name=card.name, card_path=card.path)
    except DOMAIN_ERRORS as exc:
        raise _http_error(exc)
