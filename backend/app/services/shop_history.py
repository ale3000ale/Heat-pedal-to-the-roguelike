from dataclasses import dataclass

from sqlalchemy import desc, select
from sqlalchemy.orm import Session

from app.db.models import User
from app.db.models.pilot import Pilot
from app.db.models.shop import PackPurchase
from app.services.championships import get_championship
from app.services.shop_view import ShopAccessDeniedError


@dataclass
class PilotHistory:
    # Acquisti di un pilota, dal più recente. Il nome è quello dell'ultimo acquisto.
    pilot_id: int | None
    pilot_name: str
    purchases: list[PackPurchase]


def _newest_first(stmt):
    return stmt.order_by(desc(PackPurchase.purchased_at), desc(PackPurchase.id))


def list_own_history(db: Session, user: User, championship_id: int) -> list[PackPurchase]:
    # Acquisti fatti nel campionato dai piloti dell'utente (anche l'admin vede solo i
    # propri qui). A campionato chiuso il negozio non è più disponibile per gli utenti.
    # Errori: ChampionshipNotFoundError, ShopAccessDeniedError.
    championship = get_championship(db, championship_id)
    if championship.is_closed and user.role != "admin":
        raise ShopAccessDeniedError
    own_pilots = select(Pilot.id).where(Pilot.user_id == user.id)
    stmt = select(PackPurchase).where(
        PackPurchase.championship_id == championship_id,
        PackPurchase.pilot_id.in_(own_pilots),
    )
    return list(db.scalars(_newest_first(stmt)))


def list_all_history(db: Session, championship_id: int) -> list[PackPurchase]:
    # Cronologia completa del campionato, per le impostazioni del negozio (admin).
    # Errori: ChampionshipNotFoundError.
    get_championship(db, championship_id)
    stmt = select(PackPurchase).where(PackPurchase.championship_id == championship_id)
    return list(db.scalars(_newest_first(stmt)))


def group_by_pilot(purchases: list[PackPurchase]) -> list[PilotHistory]:
    # Raggruppa per pilota, in ordine alfabetico di nome. I piloti eliminati (senza id)
    # si raggruppano per il nome copiato nello storico. L'ordine degli acquisti resta
    # quello ricevuto.
    groups: dict[object, PilotHistory] = {}
    for purchase in purchases:
        key = purchase.pilot_id if purchase.pilot_id is not None else ("deleted", purchase.pilot_name)
        if key not in groups:
            groups[key] = PilotHistory(purchase.pilot_id, purchase.pilot_name, [])
        groups[key].purchases.append(purchase)
    return sorted(groups.values(), key=lambda group: group.pilot_name.casefold())
