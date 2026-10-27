from datetime import timedelta

from fastapi import APIRouter, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import CurrentUser, DbDep, JudgeUser
from app.db.models.race import Race
from app.schemas.cards.card_judge import (
    CardBonusRead,
    CardBonusRequest,
    CardRemovalRead,
    CardRemovalRequest,
    JudgePlayRead,
    PilotPlaysRead,
)
from app.schemas.race.race_review import RaceReviewRead
from app.schemas.race.review_inventory import ReviewCardRead, ReviewInventoryRead, ReviewPilotRead
from app.services.cards.card_judge import (
    CardNotRemovableError,
    CardPlayNotActiveError,
    CardPlayNotFoundError,
    cancel_play,
    get_card_summary,
    grant_bonus,
    remove_card,
)
from app.services.cards.card_play import CardNotAvailableError
from app.services.cards.cards import CardError
from app.services.championship.championships import ChampionshipClosedError, ChampionshipNotFoundError
from app.services.pilots.pilots import PilotNotFoundError
from app.services.race.race_review import (
    REVIEW_MINUTES,
    RaceNotClosedError,
    RaceNotLastError,
    ReviewAlreadyConfirmedError,
    ReviewHeldByOtherError,
    ReviewNotActiveError,
    ReviewNotConfirmedError,
    ReviewReopenForbiddenError,
    _utc,
    abandon_review,
    begin_review,
    confirm_review,
    is_last_race as _is_last_race,
    is_review_active,
    reopen_review,
    settle_expired_reviews,
)
from app.services.race.races import RaceNotFoundError, get_race
from app.services.race.review_inventory import get_review_inventory
from app.services.shop.shop_view import PilotNotEnrolledError

router = APIRouter(tags=["race-review"])

DOMAIN_ERRORS = (
    ChampionshipNotFoundError,
    RaceNotFoundError,
    ChampionshipClosedError,
    RaceNotClosedError,
    RaceNotLastError,
    ReviewAlreadyConfirmedError,
    ReviewHeldByOtherError,
    ReviewNotActiveError,
    ReviewNotConfirmedError,
    ReviewReopenForbiddenError,
    PilotNotFoundError,
    PilotNotEnrolledError,
    CardNotAvailableError,
    CardNotRemovableError,
    CardPlayNotFoundError,
    CardPlayNotActiveError,
    CardError,
)


def _read(db: Session, race: Race) -> RaceReviewRead:
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
        is_last_race=_is_last_race(db, race),
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
    if isinstance(exc, ReviewReopenForbiddenError):
        return HTTPException(
            status.HTTP_403_FORBIDDEN, "Solo l'admin può riaprire una revisione confermata"
        )
    if isinstance(exc, ChampionshipClosedError):
        return HTTPException(status.HTTP_409_CONFLICT, "Campionato chiuso")
    if isinstance(exc, RaceNotClosedError):
        return HTTPException(status.HTTP_409_CONFLICT, "La gara non ha ancora i risultati")
    if isinstance(exc, RaceNotLastError):
        return HTTPException(
            status.HTTP_409_CONFLICT, "Solo l'ultima gara del campionato si può rivedere di nuovo"
        )
    if isinstance(exc, ReviewNotConfirmedError):
        return HTTPException(
            status.HTTP_409_CONFLICT, "La revisione non è ancora stata confermata"
        )
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


@router.get("/{championship_id}/races/{race_id}/review", response_model=RaceReviewRead)
def read_review(championship_id: int, race_id: int, user: CurrentUser, db: DbDep):
    # Stato della revisione. Prima conferma così com'è le revisioni scadute del campionato,
    # così chi legge non vede mai una revisione scaduta come attiva.
    try:
        settle_expired_reviews(db, championship_id)
        return _read(db, get_race(db, championship_id, race_id))
    except DOMAIN_ERRORS as exc:
        raise _http_error(exc)


@router.post("/{championship_id}/races/{race_id}/review", response_model=RaceReviewRead)
def open_review(championship_id: int, race_id: int, judge: JudgeUser, db: DbDep):
    # Apre la revisione delle carte dopo i risultati (giudice o admin) o la riprende se
    # è la propria: gli altri ricevono 409 finché non scade.
    try:
        return _read(db, begin_review(db, championship_id, race_id, judge))
    except DOMAIN_ERRORS as exc:
        raise _http_error(exc)


@router.delete("/{championship_id}/races/{race_id}/review", response_model=RaceReviewRead)
def close_review(championship_id: int, race_id: int, judge: JudgeUser, db: DbDep):
    # Il revisore rinuncia alla revisione: la gara torna "da rivedere".
    try:
        return _read(db, abandon_review(db, championship_id, race_id, judge))
    except DOMAIN_ERRORS as exc:
        raise _http_error(exc)


@router.post("/{championship_id}/races/{race_id}/review/confirm", response_model=RaceReviewRead)
def confirm_card_review(championship_id: int, race_id: int, judge: JudgeUser, db: DbDep):
    # Conferma la revisione e consuma le carte giocate. Il revisore con la revisione
    # attiva; l'admin con la revisione scaduta o mai aperta.
    try:
        race = confirm_review(db, championship_id, race_id, judge, judge.role == "admin")
        return _read(db, race)
    except DOMAIN_ERRORS as exc:
        raise _http_error(exc)


@router.post("/{championship_id}/races/{race_id}/review/reopen", response_model=RaceReviewRead)
def reopen_card_review(championship_id: int, race_id: int, judge: JudgeUser, db: DbDep):
    # Riapre la revisione di una gara già confermata: solo l'admin e solo l'ultima gara.
    # L'admin diventa il revisore, con 15 minuti di tempo.
    try:
        race = reopen_review(db, championship_id, race_id, judge, judge.role == "admin")
        return _read(db, race)
    except DOMAIN_ERRORS as exc:
        raise _http_error(exc)


@router.get(
    "/{championship_id}/races/{race_id}/review/inventory",
    response_model=ReviewInventoryRead,
)
def read_review_inventory(championship_id: int, race_id: int, judge: JudgeUser, db: DbDep):
    # Inventario sponsor di ogni pilota per la revisione: copie rimaste su copie totali
    # (partenza + bonus del tasto S) e massimo della pool per carta. Giudice o admin, in
    # sola lettura: non richiede di essere il revisore.
    try:
        race, pilots = get_review_inventory(db, championship_id, race_id)
        return ReviewInventoryRead(
            race_id=race.id,
            pilots=[
                ReviewPilotRead(
                    pilot_id=pilot.id,
                    pilot_name=pilot.name,
                    cards=[
                        ReviewCardRead(
                            card_name=card.name,
                            card_path=card.path,
                            total=card.total,
                            remaining=card.remaining,
                            gifted=card.gifted,
                            start=card.start,
                            pool_now=card.pool_now,
                            pool_max=card.pool_max,
                        )
                        for card in cards
                    ],
                )
                for pilot, cards in pilots
            ],
        )
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
    # Annulla una giocata (anche già consumata): solo il revisore, con la revisione attiva.
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


@router.post(
    "/{championship_id}/races/{race_id}/card-removal",
    response_model=CardRemovalRead,
)
def create_card_removal(
    championship_id: int, race_id: int, data: CardRemovalRequest, judge: JudgeUser, db: DbDep
):
    # Rimozione del revisore: una copia dall'inventario del pilota alla pool sponsor.
    try:
        pilot, card = remove_card(
            db, championship_id, race_id, data.pilot_id, data.card_name, judge
        )
        return CardRemovalRead(pilot_id=pilot.id, card_name=card.name, card_path=card.path)
    except DOMAIN_ERRORS as exc:
        raise _http_error(exc)
