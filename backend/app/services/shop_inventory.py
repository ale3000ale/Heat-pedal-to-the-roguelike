from sqlalchemy.orm import Session

from app.db.models import User
from app.db.models.deck import Deck
from app.db.models.pilot import Pilot
from app.services.cards import STARTER_INVENTORY, CardEntry, card_key, parse_cards
from app.services.championships import get_championship
from app.services.pilots import get_own_pilot
from app.services.shop_view import PilotNotEnrolledError, ShopAccessDeniedError, is_enrolled

_STARTER_KEYS = {card_key(card.name) for card in STARTER_INVENTORY}


def visible_cards(cards: list[CardEntry]) -> list[CardEntry]:
    # Riepilogo dell'inventario: senza le carte di default (Velocità 1-4), in ordine
    # alfabetico senza distinguere le maiuscole.
    shown = [card for card in cards if card_key(card.name) not in _STARTER_KEYS]
    return sorted(shown, key=lambda card: card_key(card.name))


def inventory_summary(
    db: Session, user: User, championship_id: int, pilot_id: int
) -> tuple[Pilot, list[CardEntry], list[CardEntry]]:
    # Inventari (modifiche e sponsor) di un proprio pilota iscritto, per il popup del
    # negozio. A campionato chiuso solo l'admin può vederli.
    # Errori: ChampionshipNotFoundError, PilotNotFoundError, PilotNotEnrolledError,
    # ShopAccessDeniedError.
    championship = get_championship(db, championship_id)
    if championship.is_closed and user.role != "admin":
        raise ShopAccessDeniedError
    pilot = get_own_pilot(db, user, pilot_id)
    if not is_enrolled(db, championship_id, pilot.id):
        raise PilotNotEnrolledError
    modifiche = visible_cards(parse_cards(db.get(Deck, pilot.inventory_deck_id).cards))
    sponsor = visible_cards(parse_cards(db.get(Deck, pilot.sponsor_inventory_deck_id).cards))
    return pilot, modifiche, sponsor
