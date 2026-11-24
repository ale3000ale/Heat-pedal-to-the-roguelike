from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

from app.api.deps import AdminUser, DbDep
from app.services.championship.board_pools import (
    POOL_KINDS,
    BoardPoolCard,
    BoardPoolCardNotFoundError,
    BoardPoolCardNotInPoolError,
    BoardPoolChampionshipNotFoundError,
    BoardPoolClosedError,
    BoardPoolConflictError,
    BoardPoolKindError,
    pool_view,
    update_card,
)
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
    blocked: bool
    fields: list[BoardPoolFieldRead]


class BoardPoolRead(BaseModel):
    kind: str
    cards: list[BoardPoolCardRead]


class BoardPoolCardUpdate(BaseModel):
    in_pool: bool | None = None
    blocked: bool | None = None


def _card_read(card: BoardPoolCard) -> BoardPoolCardRead:
    return BoardPoolCardRead(
        id=card.id,
        nome=card.nome,
        image=card.image,
        in_pool=card.in_pool,
        blocked=card.blocked,
        fields=[
            BoardPoolFieldRead(label=field.label, value=field.value)
            for field in card.fields
        ],
    )


@router.get("/{championship_id}/board-pools/{kind}", response_model=BoardPoolRead)
def read_board_pool(championship_id: int, kind: str, admin: AdminUser, db: DbDep):
    # Vista completa di una pool di mappe o eventi (solo admin): tutte le carte del
    # catalogo, con le informazioni del JSON e lo stato in pool / bloccata.
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
    return BoardPoolRead(kind=kind, cards=[_card_read(card) for card in cards])


@router.patch(
    "/{championship_id}/board-pools/{kind}/cards/{card_id}",
    response_model=BoardPoolCardRead,
)
def patch_board_pool_card(
    championship_id: int,
    kind: str,
    card_id: int,
    body: BoardPoolCardUpdate,
    admin: AdminUser,
    db: DbDep,
):
    # Modifica una carta della pool: uscita/reinserimento oppure blocco/sblocco.
    # Una sola operazione per richiesta, sempre solo per gli admin.
    if kind not in POOL_KINDS:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Pool non trovata")
    if (body.in_pool is None) == (body.blocked is None):
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_CONTENT, "Indicare una sola modifica")
    try:
        card = update_card(
            db,
            championship_id,
            kind,
            card_id,
            in_pool=body.in_pool,
            blocked=body.blocked,
        )
    except (BoardPoolCardNotFoundError, BoardPoolChampionshipNotFoundError):
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Carta o campionato non trovato")
    except (BoardPoolCardNotInPoolError, BoardPoolClosedError, BoardPoolConflictError) as exc:
        raise HTTPException(status.HTTP_409_CONFLICT, str(exc) or "Modifica non consentita")
    except BoardPoolKindError:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Pool non trovata")
    return _card_read(card)
