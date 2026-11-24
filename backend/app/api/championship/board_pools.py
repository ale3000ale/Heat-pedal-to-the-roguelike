from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

from app.api.deps import AdminUser, DbDep
from app.services.championship.board_pools import POOL_KINDS, BoardPoolKindError, pool_view
from app.services.championship.championships import (
    ChampionshipNotFoundError,
    get_championship,
)

router = APIRouter(tags=["championships"])


class BoardPoolFieldRead(BaseModel):
    label: str
    value: str


class BoardPoolCardRead(BaseModel):
    id: int
    nome: str
    image: str
    in_pool: bool
    fields: list[BoardPoolFieldRead]


class BoardPoolRead(BaseModel):
    kind: str
    cards: list[BoardPoolCardRead]


@router.get("/{championship_id}/board-pools/{kind}", response_model=BoardPoolRead)
def read_board_pool(championship_id: int, kind: str, admin: AdminUser, db: DbDep):
    # Vista completa di una pool di mappe o eventi (solo admin): tutte le carte del
    # catalogo, con le informazioni del JSON e lo stato in pool / fuori pool.
    if kind not in POOL_KINDS:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Pool non trovata")
    try:
        championship = get_championship(db, championship_id)
    except ChampionshipNotFoundError:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Campionato non trovato")
    try:
        cards = pool_view(championship, kind)
    except BoardPoolKindError:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Pool non trovata")
    return BoardPoolRead(
        kind=kind,
        cards=[
            BoardPoolCardRead(
                id=card.id,
                nome=card.nome,
                image=card.image,
                in_pool=card.in_pool,
                fields=[
                    BoardPoolFieldRead(label=field.label, value=field.value)
                    for field in card.fields
                ],
            )
            for card in cards
        ],
    )
