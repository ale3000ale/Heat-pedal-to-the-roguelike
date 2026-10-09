from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

from app.api.deps import AdminUser, DbDep
from app.schemas.pool import PoolCreate, PoolDetail, PoolKind, PoolRead, PoolReloadResult
from app.services.pool_cards import (
    PoolCardNameTakenError,
    PoolCardNotFoundError,
    rename_pool_card,
)
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


class CardRename(BaseModel):
    # La carta si indica con il suo percorso (non cambia), il nome è quello nuovo.
    path: str
    name: str


def _summary(pool) -> PoolRead:
    # Riga dell'elenco: dati della pool e conteggio di carte e copie.
    cards = pool_cards(pool)
    return PoolRead(
        id=pool.id,
        name=pool.name,
        kind=pool.kind,
        cards_count=len(cards),
        copies_count=sum(card.copies for card in cards),
    )


def _detail(pool) -> PoolDetail:
    cards = pool_cards(pool)
    return PoolDetail(
        id=pool.id,
        name=pool.name,
        kind=pool.kind,
        cards_count=len(cards),
        copies_count=sum(card.copies for card in cards),
        cards=cards,
    )


@router.get("", response_model=list[PoolRead])
def list_all(admin: AdminUser, db: DbDep):
    # Elenco delle pool con il numero di carte e di copie (solo admin).
    return [_summary(pool) for pool in list_pools(db)]


@router.post("/base/{kind}/reload", response_model=PoolReloadResult)
def reload(kind: PoolKind, admin: AdminUser, db: DbDep):
    # Sincronizza una pool di base con la sua cartella (solo admin): aggiunge le carte
    # nuove, toglie quelle il cui file non esiste più e non modifica quelle presenti.
    try:
        result = reload_base_pool(db, kind)
    except PoolNotFoundError:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Pool di base non trovata")
    return PoolReloadResult(
        added=result.added,
        removed=result.removed,
        already_present=result.already_present,
        warnings=result.warnings,
    )


@router.get("/{pool_id}", response_model=PoolDetail)
def detail(pool_id: int, admin: AdminUser, db: DbDep):
    try:
        return _detail(get_pool(db, pool_id))
    except PoolNotFoundError:
        raise NOT_FOUND


@router.patch("/{pool_id}/cards", response_model=PoolDetail)
def rename_card(pool_id: int, data: CardRename, admin: AdminUser, db: DbDep):
    # Rinomina una carta della pool (solo admin): il percorso resta quello.
    try:
        return _detail(rename_pool_card(db, pool_id, data.path, data.name))
    except PoolNotFoundError:
        raise NOT_FOUND
    except PoolCardNotFoundError:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Carta non trovata nella pool")
    except PoolCardNameTakenError:
        raise HTTPException(status.HTTP_409_CONFLICT, "Nome già usato da un'altra carta")
    except PoolRuleError as exc:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_CONTENT, str(exc))


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
