from datetime import timedelta

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
    CardNotRemovableError,
    CardPlayNotActiveError,
    CardPlayNotFoundError,
    cancel_play,
    get_card_summary,
    grant_bonus,
    remove_card,
)
from app.services.card_play import CardNotAvailableError
from app.services.cards import CardError
from app.services.championships import ChampionshipClosedError, ChampionshipNotFoundError
from app.services.pilots import PilotNotFoundError
from app.services.race_review import (
    REVIEW_MINUTES,
    RaceNotClosedError,
    ReviewAlreadyConfirmedError,
    ReviewHeldByOtherError,
    ReviewNotActiveError,
    _utc,
    abandon_review,
    begin_review,
    confirm_review,
    is_review_active,
)
from app.services.races import RaceNotFoundError
from app.services.shop_view import PilotNotEnrolledError

router = APIRouter(tags=["race-review"])

DOMAIN_ERRORS = (
    ChampionshipNotFoundError,
    RaceNotFoundError,
    ChampionshipClosedError,
    RaceNotClosedError,
    ReviewAlreadyConfirmedError,
    ReviewHeldByOtherError,
    ReviewNotActiveError,
    PilotNotFoundError,
    PilotNotEnrolledError,
    CardNotAvailableError,
    CardNotRemovableError,
    CardPlayNotFoundError,
    CardPlayNotActiveError,
    CardError,
)


def _read(race: Race) -> RaceReviewRead:
    # Stato della revisione: revisore e scadenza solo se la revisione è attiva.
    active = is_review_active(race)
    expires = (
        _utc(race.review_started_at) + timedelta(minutes=REVIEW_MINUTES) if active else None
    )
    return RaceReviewRead(
        race_id=race.id,
        in_review=active,
        review_started_at=race.review_started_at,
        reviewer_user_id=race.review_started_by_user_id if active else None,
        review_expires_at=expires,
        review_closed_at=race.review_closed_at,
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
    if isinstance(exc, RaceNotClosedError):
        return HTTPException(status.HTTP_409_CONFLICT, "La gara non ha ancora i risultati")
    if isinstance(exc, ReviewAlreadyConfirmedError):
        return HTTPException(status.HTTP_409_CONFLICT, "La revisione è già stata confermata")
    if isinstance(exc, ReviewHeldByOtherError):
        return HTTPException(status.HTTP_409_CONFLICT, "La revisione è in corso da un altro utente")
    if isinstance(exc, ReviewNotActiveError):
        return HTTPException(status.HTTP_409_CONFLICT, "La revisione non è aperta o è scaduta")
    if isinstance(exc, CardNotAvailableError):
        return HTTPException(status.HTTP_409_CONFLICT, "Carta non disponibile nella pool")
    if isinstance(exc, CardNotRemovableError):
        return HTTPException(status.HTTP_409_CONFLICT, str(exc))
    if isinstance(exc, CardPlayNotActiveError):
        return HTTPException(status.HTTP_409_CONFLICT, "La giocata non è più attiva")
    if isinstance(exc, CardError):
        return HTTPException(status.HTTP_409_CONFLICT, str(exc))
    raise exc


@router.post("/{championship_id}/races/{race_id}/review", response_model=RaceReviewRead)
def open_review(championship_id: int, race_id: int, judge: JudgeUser, db: DbDep):
    # Apre la revisione delle carte dopo i risultati (giudice o admin) o la riprende se
    # è la propria: gli altri ricevono 409 finché non scade.
    try:
        return _read(begin_review(db, championship_id, race_id, judge))
    except DOMAIN_ERRORS as exc:
        raise _http_error(exc)


@router.delete("/{championship_id}/races/{race_id}/review", response_model=RaceReviewRead)
def close_review(championship_id: int, race_id: int, judge: JudgeUser, db: DbDep):
    # Il revisore rinuncia alla revisione: la gara torna "da rivedere".
    try:
        return _read(abandon_review(db, championship_id, race_id, judge))
    except DOMAIN_ERRORS as exc:
        raise _http_error(exc)


@router.post("/{championship_id}/races/{race_id}/review/confirm", response_model=RaceReviewRead)
def confirm_card_review(championship_id: int, race_id: int, judge: JudgeUser, db: DbDep):
    # Conferma la revisione e consuma le carte giocate. Il revisore con la revisione
    # attiva; l'admin con la revisione scaduta o mai aperta.
    try:
        race = confirm_review(db, championship_id, race_id, judge, judge.role == "admin")
        return _read(race)
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
    # Annulla una giocata attiva: solo il revisore, con la revisione attiva.
    try:
        return JudgePlayRead.model_validate(
            cancel_play(db, championship_id, race_id, play_id, judge)
        )
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
    # Bonus del revisore: una copia dalla pool all'inventario del pilota, senza notifica.
    try:
        pilot, card = grant_bonus(
            db, championship_id, race_id, data.pilot_id, data.card_name, judge
        )
        return CardBonusRead(pilot_id=pilot.id, card_name=card.name, card_path=card.path)
    except DOMAIN_ERRORS as exc:
        raise _http_error(exc)


@router.post("/{championship_id}/races/{race_id}/card-removal", response_model=CardBonusRead)
def create_card_removal(
    championship_id: int, race_id: int, data: CardBonusRequest, judge: JudgeUser, db: DbDep
):
    # Rimozione del revisore: una copia libera torna dall'inventario del pilota alla pool.
    try:
        pilot, card = remove_card(
            db, championship_id, race_id, data.pilot_id, data.card_name, judge
        )
        return CardBonusRead(pilot_id=pilot.id, card_name=card.name, card_path=card.path)
    except DOMAIN_ERRORS as exc:
        raise _http_error(exc)
