"""Errori HTTP draft senza esporre dettagli SQL, carte o snapshot."""
from collections.abc import Callable
from typing import TypeVar

from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import ValidationError
from sqlalchemy.exc import IntegrityError, OperationalError
from sqlalchemy.orm import Session
from sqlalchemy.orm.exc import StaleDataError

from app.services.cards import CardError
from app.services.championships import ChampionshipClosedError, ChampionshipNotFoundError
from app.services.draft_guards import DraftLockedError
from app.services.draft_preparation import DraftPermissionError, DraftPreparationError
from app.services.draft_snapshot import DraftSnapshotConflictError
from app.services.draft_transitions import DraftTransitionError, DraftTurnPermissionError
from app.services.draft_view import DraftNotFoundError
from app.services.pilot_deck import GameDeckFullError, PilotCardNotFoundError
from app.services.race_deck_readiness import GameDecksNotReadyError
from app.services.races import RaceInProgressError
from app.services.shop_draw import PackSoldOutError
from app.services.sqlite_write_lock import SQLiteWriteLockError

T = TypeVar("T")


def draft_request(db: Session, operation: Callable[[], T]) -> T:
    """Esegue un servizio e traduce solo errori riconosciuti, con rollback.

    Nessun commit sul successo: appartiene al servizio. Errori SQL inattesi
    propagano. Input HTTP non valido e rifiutato prima da Pydantic con 422.
    """
    try:
        return operation()
    except Exception as exc:
        db.rollback()
        if isinstance(exc, (DraftPermissionError, DraftTurnPermissionError)):
            raise HTTPException(403, str(exc)) from exc
        if isinstance(exc, (DraftNotFoundError, ChampionshipNotFoundError, PilotCardNotFoundError)):
            raise HTTPException(404, "Preparazione, campionato o carta non trovati") from exc
        if isinstance(exc, ChampionshipClosedError):
            raise HTTPException(409, "Campionato chiuso") from exc
        if isinstance(exc, RaceInProgressError):
            raise HTTPException(409, "Esiste una gara non conclusa") from exc
        if isinstance(exc, (ValidationError, CardError)):
            raise HTTPException(409, "Dati delle carte o della preparazione non validi") from exc
        if isinstance(exc, GameDeckFullError):
            raise HTTPException(409, "Il mazzo contiene gia 15 carte") from exc
        if isinstance(exc, PackSoldOutError):
            raise HTTPException(409, "Pool modifiche insufficiente: rileggere lo stato") from exc
        if isinstance(exc, (DraftLockedError, DraftPreparationError, DraftSnapshotConflictError,
                            DraftTransitionError, GameDecksNotReadyError)):
            raise HTTPException(409, str(exc)) from exc
        if isinstance(exc, (StaleDataError, IntegrityError, SQLiteWriteLockError)):
            raise HTTPException(409, "Conflitto di scrittura: rileggere lo stato prima di riprovare") from exc
        if isinstance(exc, OperationalError):
            code = getattr(exc.orig, "sqlite_errorcode", 0) or 0
            if (code & 255) in (5, 6):
                raise HTTPException(409, "Database occupato: rileggere lo stato prima di riprovare") from exc
        raise


async def draft_locked_response(request: Request, exc: DraftLockedError) -> JSONResponse:
    """Handler 409 per i blocchi draft nei router esistenti, senza dettagli privati."""
    return JSONResponse(status_code=409, content={"detail": str(exc)})
