from fastapi import APIRouter, HTTPException, status

from app.api.deps import AdminUser, DbDep
from app.schemas.pool import PoolCreate, PoolDetail, PoolKind, PoolRead, PoolReloadResult
from app.services.pools import (
    PoolNameTakenError,
    PoolNotFoundError,
    PoolProtectedError,
    PoolRuleError,
    create_pool,
    delete_pool,
    get_pool,
    list_pools,
    pool_cards,
    reload_base_pool,
)

router = APIRouter(tags=["pools"])

NOT_FOUND = HTTPException(status.HTTP_404_NOT_FOUND, "Pool non trovata")


def _detail(pool) -> PoolDetail:
    return PoolDetail(id=pool.id, name=pool.name, kind=pool.kind, cards=pool_cards(pool))


@router.get("", response_model=list[PoolRead])
def list_all(admin: AdminUser, db: DbDep):
    # Elenco delle pool (solo admin).
    return list_pools(db)


@router.post("/base/{kind}/reload", response_model=PoolReloadResult)
def reload(kind: PoolKind, admin: AdminUser, db: DbDep):
    # Ricarica una pool di base dalla sua cartella: aggiunge le carte nuove, non toglie
    # e non modifica quelle presenti (solo admin).
    try:
        result = reload_base_pool(db, kind)
    except PoolNotFoundError:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Pool di base non trovata")
    return PoolReloadResult(
        added=result.added,
        already_present=result.already_present,
        warnings=result.warnings,
    )


@router.get("/{pool_id}", response_model=PoolDetail)
def detail(pool_id: int, admin: AdminUser, db: DbDep):
    try:
        return _detail(get_pool(db, pool_id))
    except PoolNotFoundError:
        raise NOT_FOUND


@router.post("", response_model=PoolDetail, status_code=status.HTTP_201_CREATED)
def create(data: PoolCreate, admin: AdminUser, db: DbDep):
    # Crea una pool scegliendo carte e copie dalla pool di base del suo tipo.
    choices = [(card.name, card.copies) for card in data.cards]
    try:
        return _detail(create_pool(db, data.name, choices, data.kind))
    except PoolNotFoundError:
        raise NOT_FOUND
    except PoolNameTakenError:
        raise HTTPException(status.HTTP_409_CONFLICT, "Nome già in uso")
    except PoolRuleError as exc:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_CONTENT, str(exc))


@router.delete("/{pool_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove(pool_id: int, admin: AdminUser, db: DbDep):
    try:
        delete_pool(db, pool_id)
    except PoolNotFoundError:
        raise NOT_FOUND
    except PoolProtectedError:
        raise HTTPException(status.HTTP_409_CONFLICT, "Le pool di base non si possono eliminare")
