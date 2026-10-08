from fastapi import APIRouter, HTTPException, status

from app.api.deps import AdminUser, DbDep
from app.schemas.pack import PackRead
from app.schemas.shop import PackData
from app.services.championships import ChampionshipClosedError, ChampionshipNotFoundError
from app.services.pack_images import PackImageError
from app.services.packs import (
    PackNotFoundError,
    create_pack,
    delete_pack,
    list_packs,
    update_pack,
)

router = APIRouter(tags=["packs"])

CHAMPIONSHIP_NOT_FOUND = HTTPException(status.HTTP_404_NOT_FOUND, "Campionato non trovato")
PACK_NOT_FOUND = HTTPException(status.HTTP_404_NOT_FOUND, "Pacchetto non trovato")
CHAMPIONSHIP_CLOSED = HTTPException(status.HTTP_409_CONFLICT, "Campionato chiuso")


@router.get("/{championship_id}/packs", response_model=list[PackRead])
def list_championship_packs(championship_id: int, admin: AdminUser, db: DbDep):
    # Pacchetti del negozio di un campionato (solo admin; il negozio dei giocatori arriva
    # nella sottofase 12c).
    try:
        return list_packs(db, championship_id)
    except ChampionshipNotFoundError:
        raise CHAMPIONSHIP_NOT_FOUND


@router.post(
    "/{championship_id}/packs", response_model=PackRead, status_code=status.HTTP_201_CREATED
)
def add_championship_pack(championship_id: int, data: PackData, admin: AdminUser, db: DbDep):
    # Aggiunge un pacchetto (solo admin, campionato attivo). Per partire da un template,
    # il frontend legge i valori del template e li invia qui, anche modificati.
    try:
        return create_pack(db, championship_id, data.model_dump())
    except ChampionshipNotFoundError:
        raise CHAMPIONSHIP_NOT_FOUND
    except ChampionshipClosedError:
        raise CHAMPIONSHIP_CLOSED
    except PackImageError as exc:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_CONTENT, str(exc))


@router.put("/{championship_id}/packs/{pack_id}", response_model=PackRead)
def change_championship_pack(
    championship_id: int, pack_id: int, data: PackData, admin: AdminUser, db: DbDep
):
    # Modifica per intero un pacchetto (solo admin, campionato attivo).
    try:
        return update_pack(db, championship_id, pack_id, data.model_dump())
    except (ChampionshipNotFoundError):
        raise CHAMPIONSHIP_NOT_FOUND
    except ChampionshipClosedError:
        raise CHAMPIONSHIP_CLOSED
    except PackNotFoundError:
        raise PACK_NOT_FOUND
    except PackImageError as exc:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_CONTENT, str(exc))


@router.delete(
    "/{championship_id}/packs/{pack_id}", status_code=status.HTTP_204_NO_CONTENT
)
def remove_championship_pack(championship_id: int, pack_id: int, admin: AdminUser, db: DbDep):
    # Elimina un pacchetto (solo admin, campionato attivo); lo storico acquisti resta.
    try:
        delete_pack(db, championship_id, pack_id)
    except ChampionshipNotFoundError:
        raise CHAMPIONSHIP_NOT_FOUND
    except ChampionshipClosedError:
        raise CHAMPIONSHIP_CLOSED
    except PackNotFoundError:
        raise PACK_NOT_FOUND
