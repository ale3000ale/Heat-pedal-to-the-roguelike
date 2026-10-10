from fastapi import APIRouter, HTTPException, status

from app.api.deps import AdminUser, CurrentUser, DbDep
from app.schemas.history import HistoryRead, PilotHistoryRead, PurchaseItemRead
from app.schemas.purchase import (
    DrawnCardRead,
    PurchaseRead,
    PurchaseRequest,
    ShopPackRead,
    ShopPilotRead,
    ShopViewRead,
)
from app.schemas.shop_inventory import InventoryRead
from app.services.cards import parse_cards
from app.services.championships import ChampionshipClosedError, ChampionshipNotFoundError
from app.services.packs import PackNotFoundError
from app.services.pilots import PilotNotFoundError
from app.services.shop_draw import PackSoldOutError
from app.services.shop_history import group_by_pilot, list_all_history, list_own_history
from app.services.shop_inventory import inventory_summary
from app.services.shop_purchase import (
    InsufficientFundsError,
    InventoryLimitError,
    ShopLockedError,
    purchase_pack,
)
from app.services.shop_view import PilotNotEnrolledError, ShopAccessDeniedError, open_shop

router = APIRouter(tags=["shop-play"])

CHAMPIONSHIP_NOT_FOUND = HTTPException(status.HTTP_404_NOT_FOUND, "Campionato non trovato")
PILOT_NOT_FOUND = HTTPException(status.HTTP_404_NOT_FOUND, "Pilota non trovato")
NOT_ENROLLED = HTTPException(status.HTTP_403_FORBIDDEN, "Il pilota non è iscritto al campionato")
ACCESS_DENIED = HTTPException(status.HTTP_403_FORBIDDEN, "Accesso al negozio non consentito")


def _cards_read(cards) -> list[DrawnCardRead]:
    return [DrawnCardRead(**card.model_dump()) for card in cards]


def _history_read(purchases) -> HistoryRead:
    # Storico diviso per pilota; gli acquisti conservano le carte come testo JSON.
    return HistoryRead(
        pilots=[
            PilotHistoryRead(
                pilot_id=group.pilot_id,
                pilot_name=group.pilot_name,
                purchases=[
                    PurchaseItemRead(
                        id=item.id,
                        pack_name=item.pack_name,
                        currency=item.currency,
                        cost=item.cost,
                        purchased_at=item.purchased_at,
                        cards_modifiche=_cards_read(parse_cards(item.cards_modifiche)),
                        cards_sponsor=_cards_read(parse_cards(item.cards_sponsor)),
                    )
                    for item in group.purchases
                ],
            )
            for group in group_by_pilot(purchases)
        ]
    )


@router.get("/{championship_id}/shop", response_model=ShopViewRead)
def read_shop(
    championship_id: int, user: CurrentUser, db: DbDep, pilot_id: int | None = None
):
    # Il negozio di un campionato con il pilota scelto (pilot_id). L'admin può entrare
    # senza pilota o a campionato chiuso, in sola lettura. 403 se l'accesso non è consentito.
    try:
        view = open_shop(db, user, championship_id, pilot_id)
    except ChampionshipNotFoundError:
        raise CHAMPIONSHIP_NOT_FOUND
    except PilotNotFoundError:
        raise PILOT_NOT_FOUND
    except PilotNotEnrolledError:
        raise NOT_ENROLLED
    except ShopAccessDeniedError:
        raise ACCESS_DENIED
    pilot = view.pilot
    return ShopViewRead(
        championship_id=view.championship.id,
        championship_name=view.championship.name,
        pilot=(
            ShopPilotRead(id=pilot.id, name=pilot.name, gold=pilot.gold, sponsor=pilot.sponsor)
            if pilot is not None
            else None
        ),
        read_only=view.read_only,
        locked=view.locked,
        packs=[
            ShopPackRead(
                id=pack.id,
                name=pack.name,
                image_path=pack.image_path,
                currency=pack.currency,
                cost=pack.cost,
                modifiche_count=pack.modifiche_count,
                sponsor_count=pack.sponsor_count,
                filter_enabled=pack.filter_enabled,
                filter_text=pack.filter_text,
                sold_out=sold_out,
            )
            for pack, sold_out in view.packs
        ],
    )


@router.post(
    "/{championship_id}/shop/purchases",
    response_model=PurchaseRead,
    status_code=status.HTTP_201_CREATED,
)
def buy_pack(championship_id: int, data: PurchaseRequest, user: CurrentUser, db: DbDep):
    # Acquista un pacchetto con un proprio pilota iscritto e restituisce le carte uscite.
    # 409 per campionato chiuso, gara in corso, saldo insufficiente, pacchetto terminato
    # o tetto di copie raggiunto.
    try:
        result = purchase_pack(db, user, championship_id, data.pack_id, data.pilot_id)
    except ChampionshipNotFoundError:
        raise CHAMPIONSHIP_NOT_FOUND
    except PilotNotFoundError:
        raise PILOT_NOT_FOUND
    except PackNotFoundError:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Pacchetto non trovato")
    except PilotNotEnrolledError:
        raise NOT_ENROLLED
    except ChampionshipClosedError:
        raise HTTPException(status.HTTP_409_CONFLICT, "Campionato chiuso")
    except ShopLockedError:
        raise HTTPException(status.HTTP_409_CONFLICT, "Negozio bloccato: gara in corso")
    except InsufficientFundsError:
        raise HTTPException(status.HTTP_409_CONFLICT, "Saldo insufficiente")
    except PackSoldOutError:
        raise HTTPException(status.HTTP_409_CONFLICT, "Pacchetto terminato")
    except InventoryLimitError:
        raise HTTPException(status.HTTP_409_CONFLICT, "Limite di copie dell'inventario raggiunto")
    purchase = result.purchase
    return PurchaseRead(
        purchase_id=purchase.id,
        pack_name=purchase.pack_name,
        currency=purchase.currency,
        cost=purchase.cost,
        cards_modifiche=_cards_read(result.cards_modifiche),
        cards_sponsor=_cards_read(result.cards_sponsor),
        gold=result.pilot.gold,
        sponsor=result.pilot.sponsor,
    )


@router.get("/{championship_id}/shop/inventory", response_model=InventoryRead)
def read_inventory(championship_id: int, pilot_id: int, user: CurrentUser, db: DbDep):
    # Riepilogo per il popup del negozio: carte del pilota senza Velocità 1-4.
    try:
        pilot, modifiche, sponsor = inventory_summary(db, user, championship_id, pilot_id)
    except ChampionshipNotFoundError:
        raise CHAMPIONSHIP_NOT_FOUND
    except PilotNotFoundError:
        raise PILOT_NOT_FOUND
    except PilotNotEnrolledError:
        raise NOT_ENROLLED
    except ShopAccessDeniedError:
        raise ACCESS_DENIED
    return InventoryRead(
        pilot_id=pilot.id,
        pilot_name=pilot.name,
        modifiche=_cards_read(modifiche),
        sponsor=_cards_read(sponsor),
    )


@router.get("/{championship_id}/shop/history", response_model=HistoryRead)
def read_own_history(championship_id: int, user: CurrentUser, db: DbDep):
    # Storico degli acquisti dei propri piloti, diviso per pilota.
    try:
        purchases = list_own_history(db, user, championship_id)
    except ChampionshipNotFoundError:
        raise CHAMPIONSHIP_NOT_FOUND
    except ShopAccessDeniedError:
        raise ACCESS_DENIED
    return _history_read(purchases)


@router.get("/{championship_id}/shop/history/all", response_model=HistoryRead)
def read_all_history(championship_id: int, _admin: AdminUser, db: DbDep):
    # Cronologia completa del campionato (impostazioni del negozio, solo admin).
    try:
        purchases = list_all_history(db, championship_id)
    except ChampionshipNotFoundError:
        raise CHAMPIONSHIP_NOT_FOUND
    return _history_read(purchases)
