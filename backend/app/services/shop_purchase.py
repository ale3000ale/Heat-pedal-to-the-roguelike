import random
import threading
from dataclasses import dataclass

from sqlalchemy.orm import Session

from app.db.models import User
from app.db.models.deck import Deck
from app.db.models.pilot import Pilot
from app.db.models.shop import PackPurchase
from app.services.cards import CardEntry, card_key, dump_cards, parse_cards
from app.services.championships import ChampionshipClosedError, get_championship
from app.services.packs import get_pack
from app.services.pilots import get_own_pilot
from app.services.races import has_race_in_progress
from app.services.shop_draw import PackSoldOutError, draw_cards
from app.services.shop_view import PilotNotEnrolledError, is_enrolled, load_pool

# Tetto di sicurezza: copie massime di una carta nell'inventario di un pilota.
MAX_COPIES_PER_CARD = 100

# Un solo acquisto alla volta: la pool è la fonte di verità e due acquisti contemporanei
# non devono consumare la stessa copia. Vale per un solo processo del backend (uso locale).
_PURCHASE_LOCK = threading.Lock()


class ShopLockedError(Exception):
    """Gara in corso nel campionato: il negozio è bloccato."""


class InsufficientFundsError(Exception):
    """Il saldo del pilota non copre il costo del pacchetto."""


class InventoryLimitError(Exception):
    """L'acquisto porterebbe una carta oltre il tetto di copie dell'inventario."""


@dataclass
class PurchaseResult:
    purchase: PackPurchase
    pilot: Pilot
    cards_modifiche: list[CardEntry]
    cards_sponsor: list[CardEntry]


def merge_inventory(inventory: list[CardEntry], drawn: list[CardEntry]) -> list[CardEntry]:
    # Somma le copie estratte a quelle già possedute. Errori: InventoryLimitError se una
    # carta supera MAX_COPIES_PER_CARD.
    merged = {card_key(card.name): card.model_copy() for card in inventory}
    for card in drawn:
        key = card_key(card.name)
        if key in merged:
            merged[key].copies += card.copies
        else:
            merged[key] = card.model_copy()
    if any(card.copies > MAX_COPIES_PER_CARD for card in merged.values()):
        raise InventoryLimitError
    return list(merged.values())


def _balance(pilot: Pilot, currency: str) -> int:
    return pilot.gold if currency == "gold" else pilot.sponsor


def purchase_pack(
    db: Session,
    user: User,
    championship_id: int,
    pack_id: int,
    pilot_id: int,
    rng: random.Random | None = None,
) -> PurchaseResult:
    # Acquisto come unica operazione: controlli, saldo, estrazione, aggiornamento delle
    # pool, inventari e storico, con un solo commit. Chiunque compri (anche l'admin) lo fa
    # con un proprio pilota iscritto.
    # Errori: ChampionshipNotFoundError, ChampionshipClosedError, PilotNotFoundError,
    # PilotNotEnrolledError, ShopLockedError, PackNotFoundError, InsufficientFundsError,
    # PackSoldOutError, InventoryLimitError. In caso di errore non cambia nulla.
    rng = rng or random.SystemRandom()
    with _PURCHASE_LOCK:
        try:
            result = _purchase(db, user, championship_id, pack_id, pilot_id, rng)
            db.commit()
        except Exception:
            db.rollback()
            raise
        db.refresh(result.purchase)
        db.refresh(result.pilot)
        return result


def _purchase(db, user, championship_id, pack_id, pilot_id, rng) -> PurchaseResult:
    championship = get_championship(db, championship_id)
    if championship.is_closed:
        raise ChampionshipClosedError
    pilot = get_own_pilot(db, user, pilot_id)
    if not is_enrolled(db, championship_id, pilot.id):
        raise PilotNotEnrolledError
    if has_race_in_progress(db, championship_id):
        raise ShopLockedError
    pack = get_pack(db, championship_id, pack_id)
    if _balance(pilot, pack.currency) < pack.cost:
        raise InsufficientFundsError

    modifiche_pool = load_pool(db, championship.pool_deck_id)
    sponsor_pool = load_pool(db, championship.sponsor_pool_deck_id)
    drawn_modifiche, new_modifiche_pool = draw_cards(
        modifiche_pool, pack.modifiche_count, pack.filter_enabled, pack.filter_text, rng
    )
    drawn_sponsor, new_sponsor_pool = draw_cards(
        sponsor_pool, pack.sponsor_count, pack.filter_enabled, pack.filter_text, rng
    )

    inventory_deck = db.get(Deck, pilot.inventory_deck_id)
    sponsor_inventory_deck = db.get(Deck, pilot.sponsor_inventory_deck_id)
    new_inventory = merge_inventory(parse_cards(inventory_deck.cards), drawn_modifiche)
    new_sponsor_inventory = merge_inventory(
        parse_cards(sponsor_inventory_deck.cards), drawn_sponsor
    )

    # Da qui in poi nessun controllo può fallire: si scrive tutto.
    inventory_deck.cards = dump_cards(new_inventory)
    sponsor_inventory_deck.cards = dump_cards(new_sponsor_inventory)
    if pack.modifiche_count:
        db.get(Deck, championship.pool_deck_id).cards = dump_cards(new_modifiche_pool)
    if pack.sponsor_count:
        db.get(Deck, championship.sponsor_pool_deck_id).cards = dump_cards(new_sponsor_pool)
    if pack.currency == "gold":
        pilot.gold -= pack.cost
    else:
        pilot.sponsor -= pack.cost
    purchase = PackPurchase(
        championship_id=championship_id,
        pilot_id=pilot.id,
        pilot_name=pilot.name,
        pack_id=pack.id,
        pack_name=pack.name,
        currency=pack.currency,
        cost=pack.cost,
        cards_modifiche=dump_cards(drawn_modifiche) if drawn_modifiche else None,
        cards_sponsor=dump_cards(drawn_sponsor) if drawn_sponsor else None,
    )
    db.add(purchase)
    db.flush()
    return PurchaseResult(purchase, pilot, drawn_modifiche, drawn_sponsor)
