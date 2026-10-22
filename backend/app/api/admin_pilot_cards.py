"""API admin carte: letture e conferma unica dei trasferimenti consentiti."""
from collections.abc import Callable
from typing import TypeVar
from fastapi import APIRouter, HTTPException

from app.api.deps import AdminUser, DbDep
from app.schemas.admin_pilot_cards import AdminPilotCardsRead, AdminPilotRead, AdminPilotCardsSave
from app.services.admin_card_transfers import CardTransferError
from app.services.admin_pilot_card_save import CardAdminConflictError, save_admin_pilot_cards
from app.services.admin_pilot_cards import (
    CardAdminForbiddenError, CardAdminPilotNotFoundError, CardAdminStateError,
    list_admin_pilots, read_admin_pilot_cards,
)
from app.services.cards import CardError
from app.services.championships import ChampionshipNotFoundError

router = APIRouter(tags=["admin-pilot-cards"])
T = TypeVar("T")


def _run(operation: Callable[[], T]) -> T:
    """Traduce gli errori di dominio; non assorbe errori SQL o inattesi."""
    try:
        return operation()
    except CardAdminForbiddenError as exc:
        raise HTTPException(403, "Permesso negato") from exc
    except ChampionshipNotFoundError as exc:
        raise HTTPException(404, "Campionato non trovato") from exc
    except CardAdminPilotNotFoundError as exc:
        raise HTTPException(404, "Pilota iscritto non trovato") from exc
    except CardAdminConflictError as exc:
        raise HTTPException(409, str(exc)) from exc
    except CardTransferError as exc:
        raise HTTPException(422, str(exc)) from exc
    except (CardAdminStateError, CardError) as exc:
        raise HTTPException(409, "Contenitori delle carte incoerenti o non validi") from exc


@router.get("/{championship_id}/pilots", response_model=list[AdminPilotRead])
def pilots(championship_id: int, admin: AdminUser, db: DbDep):
    return _run(lambda: list_admin_pilots(db, admin, championship_id))


@router.get("/{championship_id}/pilots/{pilot_id}/cards", response_model=AdminPilotCardsRead)
def cards(championship_id: int, pilot_id: int, admin: AdminUser, db: DbDep):
    return _run(lambda: read_admin_pilot_cards(db, admin, championship_id, pilot_id))


@router.put("/{championship_id}/pilots/{pilot_id}/cards", response_model=AdminPilotCardsRead)
def save_cards(
    championship_id: int, pilot_id: int, data: AdminPilotCardsSave, admin: AdminUser, db: DbDep,
):
    return _run(lambda: save_admin_pilot_cards(db, admin, championship_id, pilot_id, data))
