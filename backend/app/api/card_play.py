from fastapi import APIRouter, HTTPException, status

from app.api.deps import CurrentUser, DbDep
from app.schemas.card_play import (
    AvailableCardRead,
    CardPlayRead,
    CardPlayRequest,
    CardPlayStateRead,
    CardUndoRequest,
)
from app.services.card_play import (
    CardNotAvailableError,
    NoRaceInProgressError,
    NothingToUndoError,
    PlayState,
    RaceInReviewError,
    UndoLimitError,
    get_play_state,
    play_card,
    undo_last_play,
)
from app.services.championships import ChampionshipClosedError, ChampionshipNotFoundError
from app.services.pilots import PilotNotFoundError
from app.services.shop_view import PilotNotEnrolledError

router = APIRouter(tags=["card-plays"])


def _state_read(state: PlayState) -> CardPlayStateRead:
    return CardPlayStateRead(
        race_id=state.race.id,
        pilot_id=state.pilot.id,
        plays=[CardPlayRead.model_validate(play) for play in state.plays],
        available=[AvailableCardRead(**vars(card)) for card in state.available],
        undo_remaining=state.undo_remaining,
        in_review=state.in_review,
    )


def _http_error(exc: Exception) -> HTTPException:
    # Traduce gli errori di dominio in risposte HTTP leggibili.
    if isinstance(exc, ChampionshipNotFoundError):
        return HTTPException(status.HTTP_404_NOT_FOUND, "Campionato non trovato")
    if isinstance(exc, PilotNotFoundError):
        return HTTPException(status.HTTP_404_NOT_FOUND, "Pilota non trovato")
    if isinstance(exc, PilotNotEnrolledError):
        return HTTPException(status.HTTP_403_FORBIDDEN, "Il pilota non è iscritto al campionato")
    if isinstance(exc, ChampionshipClosedError):
        return HTTPException(status.HTTP_409_CONFLICT, "Campionato chiuso")
    if isinstance(exc, NoRaceInProgressError):
        return HTTPException(status.HTTP_409_CONFLICT, "Nessuna gara in corso")
    if isinstance(exc, RaceInReviewError):
        return HTTPException(status.HTTP_409_CONFLICT, "La gara è in revisione")
    if isinstance(exc, CardNotAvailableError):
        return HTTPException(status.HTTP_409_CONFLICT, "Carta non disponibile")
    if isinstance(exc, NothingToUndoError):
        return HTTPException(status.HTTP_409_CONFLICT, "Nessuna giocata da annullare")
    if isinstance(exc, UndoLimitError):
        return HTTPException(status.HTTP_409_CONFLICT, "Limite di annullamenti consecutivi raggiunto")
    raise exc


DOMAIN_ERRORS = (
    ChampionshipNotFoundError,
    PilotNotFoundError,
    PilotNotEnrolledError,
    ChampionshipClosedError,
    NoRaceInProgressError,
    RaceInReviewError,
    CardNotAvailableError,
    NothingToUndoError,
    UndoLimitError,
)


@router.get("/{championship_id}/card-plays", response_model=CardPlayStateRead)
def read_card_plays(championship_id: int, pilot_id: int, user: CurrentUser, db: DbDep):
    # Giocate, copie disponibili e annullamenti rimasti del proprio pilota nella gara in corso.
    try:
        return _state_read(get_play_state(db, user, championship_id, pilot_id))
    except DOMAIN_ERRORS as exc:
        raise _http_error(exc)


@router.post(
    "/{championship_id}/card-plays",
    response_model=CardPlayStateRead,
    status_code=status.HTTP_201_CREATED,
)
def create_card_play(championship_id: int, data: CardPlayRequest, user: CurrentUser, db: DbDep):
    # Gioca una carta sponsor. 409 se la carta non è disponibile, se non c'è una gara in
    # corso o se la gara è in revisione.
    try:
        return _state_read(play_card(db, user, championship_id, data.pilot_id, data.card_name))
    except DOMAIN_ERRORS as exc:
        raise _http_error(exc)


@router.post("/{championship_id}/card-plays/undo", response_model=CardPlayStateRead)
def undo_card_play(championship_id: int, data: CardUndoRequest, user: CurrentUser, db: DbDep):
    # Annulla l'ultima giocata attiva, fino a 5 volte consecutive (409 se la gara è in revisione).
    try:
        return _state_read(undo_last_play(db, user, championship_id, data.pilot_id))
    except DOMAIN_ERRORS as exc:
        raise _http_error(exc)
