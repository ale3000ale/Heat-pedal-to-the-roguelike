# backend/app/routers/shop.py
# Endpoint per la pagina Negozio: elenco campionati, oggetti, wallet, acquisto.

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db import get_db
from app.core.deps import get_current_user_required
from app.models.user import User
from app.schemas.shop import ShopItemOut, PurchaseCreate, PurchaseOut, WalletOut
from app.services import shop_service, championship_service

router = APIRouter(prefix="/shop", tags=["shop"])


# list_public_items(db)
# db: sessione SQLAlchemy attiva.
# Ritorna tutti gli oggetti di tutti i campionati con soli costi/informazioni, senza possibilita' di acquisto
# (vista "senza login" del negozio).
@router.get("/public", response_model=list[ShopItemOut])
def list_public_items(db: Session = Depends(get_db)):
    items = []
    for champ in championship_service.list_championships(db):
        items.extend(shop_service.list_items_by_championship(db, champ.id))
    return items


# list_items(championship_id, db, current_user)
# championship_id: id del campionato di cui mostrare il negozio; db: sessione;
# current_user: utente autenticato (obbligatorio per la vista con acquisto).
# Ritorna gli oggetti acquistabili per un campionato specifico.
@router.get("/championship/{championship_id}", response_model=list[ShopItemOut])
def list_items(
    championship_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_required),
):
    return shop_service.list_items_by_championship(db, championship_id)


# get_wallet(pilot_id, championship_id, db, current_user)
# pilot_id: pilota di cui mostrare il wallet; championship_id: campionato di riferimento;
# db: sessione; current_user: utente autenticato.
# Ritorna il recap di gold e punti disponibili del pilota nel campionato indicato.
@router.get("/wallet/{pilot_id}", response_model=WalletOut)
def get_wallet(
    pilot_id: int,
    championship_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_required),
):
    pilot = shop_service.get_pilot_wallet(db, pilot_id)
    if pilot is None or pilot.user_id != current_user.id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Pilota non trovato")
    return WalletOut(
        pilot_id=pilot.id, pilot_name=pilot.name, championship_id=championship_id,
        gold=pilot.gold, points=pilot.point,
    )


# purchase(payload, db, current_user)
# payload: pilota, campionato e oggetto da acquistare; db: sessione; current_user: utente autenticato.
# Esegue l'acquisto scalando le risorse del pilota, dopo aver verificato i fondi disponibili.
@router.post("/purchase", response_model=PurchaseOut, status_code=status.HTTP_201_CREATED)
def purchase(
    payload: PurchaseCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_required),
):
    return shop_service.purchase_item(
        db, current_user.id, payload.pilot_id, payload.championship_id, payload.item_id
    )
