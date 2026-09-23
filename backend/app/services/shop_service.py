# backend/app/services/shop_service.py
# Logica di business per Negozio: elenco oggetti, wallet, acquisti.

from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.shop import ShopItem, Purchase
from app.models.pilot import Pilot


# list_items_by_championship(db, championship_id)
# db: sessione; championship_id: id del campionato di cui mostrare il negozio.
# Ritorna gli oggetti acquistabili per quel campionato, con prezzi e requisiti.
def list_items_by_championship(db: Session, championship_id: int) -> list[ShopItem]:
    return db.query(ShopItem).filter(ShopItem.championship_id == championship_id).all()


# get_pilot_wallet(db, pilot_id)
# db: sessione; pilot_id: id del pilota di cui recuperare gold e punti correnti.
# Ritorna il pilota (per leggere gold/point), usato per il recap "soldi e punti disponibili".
def get_pilot_wallet(db: Session, pilot_id: int) -> Pilot | None:
    return db.query(Pilot).filter(Pilot.id == pilot_id).first()


# purchase_item(db, user_id, pilot_id, championship_id, item_id)
# db: sessione; user_id: utente che acquista; pilot_id: pilota che spende le risorse;
# championship_id: campionato di riferimento; item_id: oggetto da acquistare.
# Controlla i fondi disponibili, scala gold/point dal pilota e registra l'acquisto.
# Passaggio critico: se i fondi non bastano, l'operazione viene rifiutata prima di ogni scrittura sul DB.
def purchase_item(db: Session, user_id: int, pilot_id: int, championship_id: int, item_id: int) -> Purchase:
    pilot = db.query(Pilot).filter(Pilot.id == pilot_id, Pilot.user_id == user_id).first()
    if pilot is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Pilota non trovato o non appartenente all'utente")

    item = db.query(ShopItem).filter(ShopItem.id == item_id, ShopItem.championship_id == championship_id).first()
    if item is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Oggetto del negozio non trovato")

    if pilot.gold < item.price_gold or pilot.point < item.price_points:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Fondi insufficienti per l'acquisto")

    pilot.gold -= item.price_gold
    pilot.point -= item.price_points

    purchase = Purchase(
        user_id=user_id, pilot_id=pilot_id, championship_id=championship_id, item_id=item_id
    )
    db.add(purchase)
    db.commit()
    db.refresh(purchase)
    return purchase
