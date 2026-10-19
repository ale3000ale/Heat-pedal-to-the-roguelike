from collections import Counter
from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models.card_gift import CardGift
from app.db.models.card_play import STATUS_CONSUMED, STATUS_PLAYED, CardPlay
from app.db.models.deck import Deck, DeckPrototype
from app.db.models.pilot import Pilot
from app.db.models.race import Race
from app.services.cards import card_key, parse_cards
from app.services.championships import get_championship, list_entrants
from app.services.race_review import RaceNotClosedError
from app.services.races import count_participants, get_race


@dataclass
class ReviewCard:
    # Una carta sponsor di un pilota vista dal revisore.
    name: str
    path: str
    total: int
    remaining: int
    gifted: int
    pool_now: int
    pool_max: int | None

    @property
    def start(self) -> int:
        # Copie di partenza: il totale senza i bonus del tasto S.
        return max(0, self.total - self.gifted)


def _deck_copies(deck: Deck | None) -> dict[str, int]:
    # Copie per carta di un mazzo (vuoto se il mazzo non c'è).
    if deck is None:
        return {}
    return {card_key(card.name): card.copies for card in parse_cards(deck.cards)}


def _pool_caps(db: Session, pool_deck: Deck | None) -> dict[str, int]:
    # Massimo di copie per carta = copie nella pool da cui il campionato ha copiato la sua.
    # Se la copia non ricorda la pool di partenza o questa è stata cancellata, nessun massimo.
    if pool_deck is None or pool_deck.id_prototype is None:
        return {}
    prototype = db.get(DeckPrototype, pool_deck.id_prototype)
    if prototype is None:
        return {}
    return {card_key(card.name): card.copies for card in parse_cards(prototype.base_cards)}


def _pilot_cards(
    db: Session,
    race: Race,
    pilot: Pilot,
    pool_now: dict[str, int],
    pool_caps: dict[str, int],
) -> list[ReviewCard]:
    # Le carte del pilota. L'inventario contiene partenza + bonus del tasto S e, finché la
    # revisione non è confermata, anche le copie giocate. Dopo una conferma (revisione
    # riaperta dall'admin) le copie consumate sono già uscite dall'inventario: si sommano
    # al totale così il conteggio riparte dall'ultimo stato salvato.
    inventory = {
        card_key(card.name): card
        for card in parse_cards(db.get(Deck, pilot.sponsor_inventory_deck_id).cards)
    }
    plays = list(
        db.scalars(
            select(CardPlay)
            .where(
                CardPlay.race_id == race.id,
                CardPlay.pilot_id == pilot.id,
                CardPlay.status.in_((STATUS_PLAYED, STATUS_CONSUMED)),
            )
            .order_by(CardPlay.id)
        )
    )
    active = Counter(card_key(play.card_name) for play in plays if play.status == STATUS_PLAYED)
    consumed = Counter(
        card_key(play.card_name) for play in plays if play.status == STATUS_CONSUMED
    )
    gifts = Counter(
        card_key(gift.card_name)
        for gift in db.scalars(
            select(CardGift).where(CardGift.race_id == race.id, CardGift.pilot_id == pilot.id)
        )
    )
    labels = {key: (card.name, card.path) for key, card in inventory.items()}
    for play in plays:
        labels.setdefault(card_key(play.card_name), (play.card_name, play.card_path))
    cards = []
    for key, (name, path) in labels.items():
        held = inventory[key].copies if key in inventory else 0
        cards.append(
            ReviewCard(
                name=name,
                path=path,
                total=held + consumed[key],
                remaining=max(0, held - active[key]),
                gifted=gifts[key],
                pool_now=pool_now.get(key, 0),
                pool_max=pool_caps.get(key),
            )
        )
    return cards


def get_review_inventory(
    db: Session, championship_id: int, race_id: int
) -> tuple[Race, list[tuple[Pilot, list[ReviewCard]]]]:
    # Inventario sponsor di ogni pilota iscritto, per la revisione delle carte. Sola lettura.
    # Ritorna: la gara e, per pilota in ordine alfabetico, le sue carte.
    # Errori: ChampionshipNotFoundError, RaceNotFoundError, RaceNotClosedError (la gara non
    # ha ancora i risultati).
    championship = get_championship(db, championship_id)
    race = get_race(db, championship_id, race_id)
    if count_participants(db, race.id) == 0:
        raise RaceNotClosedError
    pool_deck = (
        db.get(Deck, championship.sponsor_pool_deck_id)
        if championship.sponsor_pool_deck_id
        else None
    )
    pool_now = _deck_copies(pool_deck)
    pool_caps = _pool_caps(db, pool_deck)
    pilots = [
        (pilot, _pilot_cards(db, race, pilot, pool_now, pool_caps))
        for pilot in list_entrants(db, championship_id)
    ]
    return race, pilots
