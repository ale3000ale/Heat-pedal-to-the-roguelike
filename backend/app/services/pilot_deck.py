from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import User
from app.db.models.championship import Championship, ChampionshipPilot
from app.db.models.deck import Deck
from app.db.models.pilot import Pilot
from app.services.cards import (
    MAX_GAME_DECK_CARDS,
    CardEntry,
    card_key,
    dump_cards,
    parse_cards,
)
from app.services.pilots import PilotInActiveChampionshipError, get_own_pilot
from app.services.teams import pilots_in_active_championship


class PilotCardNotFoundError(Exception):
    """La carta non è nel mazzo da cui si vuole spostarla."""


class GameDeckFullError(Exception):
    """Il mazzo da gioco ha già il massimo di carte."""


def active_championship(db: Session, pilot: Pilot) -> Championship | None:
    # Il campionato attivo a cui il pilota è iscritto (ce n'è al massimo uno), se c'è.
    stmt = (
        select(Championship)
        .join(ChampionshipPilot, ChampionshipPilot.championship_id == Championship.id)
        .where(ChampionshipPilot.pilot_id == pilot.id, Championship.is_closed.is_(False))
    )
    return db.scalars(stmt).first()


def _take_one(cards: list[CardEntry], path: str) -> CardEntry:
    # Toglie una copia della carta indicata dal percorso e restituisce la carta spostata.
    for index, card in enumerate(cards):
        if card.path == path:
            moved = CardEntry(name=card.name, path=card.path, copies=1)
            if card.copies > 1:
                cards[index] = CardEntry(name=card.name, path=card.path, copies=card.copies - 1)
            else:
                del cards[index]
            return moved
    raise PilotCardNotFoundError


def _put_one(cards: list[CardEntry], moved: CardEntry) -> None:
    # Aggiunge una copia: si somma alla carta con lo stesso nome, altrimenti si accoda.
    key = card_key(moved.name)
    for index, card in enumerate(cards):
        if card_key(card.name) == key:
            cards[index] = CardEntry(name=card.name, path=card.path, copies=card.copies + 1)
            return
    cards.append(moved)


def move_card(db: Session, user: User, pilot_id: int, path: str, to_game: bool) -> Pilot:
    # Sposta una copia dall'inventario al mazzo da gioco (to_game=True) o viceversa.
    # Il mazzo da gioco non può superare il limite e, con il pilota in un campionato
    # attivo, i mazzi non si toccano.
    pilot = get_own_pilot(db, user, pilot_id)
    if pilots_in_active_championship(db, [pilot.id]):
        raise PilotInActiveChampionshipError
    inventory_deck = db.get(Deck, pilot.inventory_deck_id)
    game_deck = db.get(Deck, pilot.game_deck_id)
    inventory = parse_cards(inventory_deck.cards)
    game = parse_cards(game_deck.cards)

    source, target = (inventory, game) if to_game else (game, inventory)
    if to_game and sum(card.copies for card in game) >= MAX_GAME_DECK_CARDS:
        raise GameDeckFullError
    _put_one(target, _take_one(source, path))

    inventory_deck.cards = dump_cards(inventory)
    game_deck.cards = dump_cards(game)
    db.commit()
    db.refresh(pilot)
    return pilot
