import random
from datetime import datetime, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import User
from app.db.models.card_gift import CardGift
from app.db.models.deck import Deck
from app.db.models.pilot import Pilot
from app.db.models.race import Race
from app.services.card_play import (
    _available,
    _ensure_not_in_review,
    _plays,
    _race_in_progress,
)
from app.services.cards import CardEntry, card_key, dump_cards, parse_cards
from app.services.championships import ChampionshipClosedError, get_championship
from app.services.gift_events import record_gift_action
from app.services.pilots import PilotNotFoundError, get_own_pilot
from app.services.shop_purchase import _lock_database
from app.services.shop_view import PilotNotEnrolledError, is_enrolled

# Ruoli che possono dare il tasto S a qualsiasi pilota iscritto; gli altri solo ai propri.
GIFT_ANY_PILOT_ROLES = ("admin", "judge")

# Tempo massimo, dall'assegnazione, per annullare una carta data con il tasto S.
UNDO_WINDOW = timedelta(seconds=60)


class SponsorPoolEmptyError(Exception):
    """La pool sponsor del campionato non ha carte da regalare."""


class GiftNotFoundError(Exception):
    """L'assegnazione non esiste in questo campionato."""


class GiftUndoForbiddenError(Exception):
    """Solo admin e giudice possono annullare un'assegnazione."""


class GiftUndoExpiredError(Exception):
    """Sono passati più di 60 secondi dall'assegnazione."""


class GiftNotUndoableError(Exception):
    """La carta è già stata giocata o la gara non è più quella dell'assegnazione."""


def _load_gift_pilot(db: Session, user: User, pilot_id: int) -> Pilot:
    # Admin e giudice vedono qualsiasi pilota non eliminato; il giocatore solo i propri.
    # Errori: PilotNotFoundError.
    if user.role not in GIFT_ANY_PILOT_ROLES:
        return get_own_pilot(db, user, pilot_id)
    stmt = select(Pilot).where(Pilot.id == pilot_id, Pilot.deleted_at.is_(None))
    pilot = db.scalar(stmt)
    if pilot is None:
        raise PilotNotFoundError
    return pilot


def _authorize_gift(
    db: Session, user: User, championship_id: int, pilot_id: int
) -> tuple[Pilot, Race]:
    # Come _authorize delle giocate, ma admin e giudice possono agire su qualsiasi pilota.
    # Errori: ChampionshipNotFoundError, ChampionshipClosedError, PilotNotFoundError,
    # PilotNotEnrolledError, NoRaceInProgressError.
    championship = get_championship(db, championship_id)
    if championship.is_closed:
        raise ChampionshipClosedError
    pilot = _load_gift_pilot(db, user, pilot_id)
    if not is_enrolled(db, championship_id, pilot.id):
        raise PilotNotEnrolledError
    return pilot, _race_in_progress(db, championship_id)


def _pick_card(pool: list[CardEntry], rng: random.Random) -> CardEntry:
    # Estrae una carta con probabilità proporzionale alle copie in pool.
    # Errori: SponsorPoolEmptyError.
    if sum(card.copies for card in pool) < 1:
        raise SponsorPoolEmptyError
    return rng.choices(pool, weights=[card.copies for card in pool])[0]


def _without_one_copy(pool: list[CardEntry], picked: CardEntry) -> list[CardEntry]:
    # La pool dopo l'estrazione: una copia in meno, riga rimossa se arriva a zero.
    result = []
    for card in pool:
        if card is not picked:
            result.append(card)
        elif card.copies > 1:
            result.append(card.model_copy(update={"copies": card.copies - 1}))
    return result


def _with_one_more_copy(inventory: list[CardEntry], picked: CardEntry) -> list[CardEntry]:
    # L'inventario dopo il regalo: una copia in più, riga nuova se la carta non c'era.
    key = card_key(picked.name)
    if any(card_key(card.name) == key for card in inventory):
        return [
            card.model_copy(update={"copies": card.copies + 1}) if card_key(card.name) == key else card
            for card in inventory
        ]
    return [*inventory, CardEntry(name=picked.name, path=picked.path, copies=1)]


def draw_gift(
    db: Session,
    user: User,
    championship_id: int,
    pilot_id: int,
    rng: random.Random | None = None,
) -> CardGift:
    # Tasto S: pool, inventario, notifica persistente ed eventi nello stesso commit.
    # Admin/giudice agiscono su ogni iscritto, il giocatore sui propri piloti.
    # Errori: quelli di _authorize_gift, RaceInReviewError, SponsorPoolEmptyError,
    # validazione/scrittura eventi; rollback completo su qualsiasi errore.
    try:
        _lock_database(db)
        pilot, race = _authorize_gift(db, user, championship_id, pilot_id)
        _ensure_not_in_review(race)
        championship = get_championship(db, championship_id)
        pool_deck = db.get(Deck, championship.sponsor_pool_deck_id) if championship.sponsor_pool_deck_id else None
        pool = parse_cards(pool_deck.cards) if pool_deck else []
        picked = _pick_card(pool, rng or random.Random())
        inventory_deck = db.get(Deck, pilot.sponsor_inventory_deck_id)
        inventory_deck.cards = dump_cards(_with_one_more_copy(parse_cards(inventory_deck.cards), picked))
        pool_deck.cards = dump_cards(_without_one_copy(pool, picked))
        gift = CardGift(race_id=race.id, pilot_id=pilot.id, card_name=picked.name, card_path=picked.path)
        db.add(gift)
        db.flush()
        db.refresh(gift)
        record_gift_action(db, race, pilot, gift, "card.gifted")
        db.commit()
    except Exception:
        db.rollback()
        raise
    return gift


def _find_gift(db: Session, championship_id: int, gift_id: int) -> CardGift:
    # L'assegnazione deve appartenere a una gara di questo campionato.
    # Errori: GiftNotFoundError.
    stmt = (
        select(CardGift)
        .join(Race, Race.id == CardGift.race_id)
        .where(CardGift.id == gift_id, Race.championship_id == championship_id)
    )
    gift = db.scalar(stmt)
    if gift is None:
        raise GiftNotFoundError
    return gift


def _ensure_within_undo_window(gift: CardGift) -> None:
    # created_at è in UTC senza fuso, come le altre date del database.
    # Errori: GiftUndoExpiredError.
    now = datetime.now(timezone.utc).replace(tzinfo=None)
    if now - gift.created_at > UNDO_WINDOW:
        raise GiftUndoExpiredError


def undo_gift(db: Session, user: User, championship_id: int, gift_id: int) -> None:
    # Annullo entro 60 secondi per admin/giudice, stessa gara, carta non impegnata.
    # Ripristino pool/inventario, eliminazione notifica ed eventi sono atomici.
    # Errori: GiftUndoForbiddenError, ChampionshipNotFoundError, ChampionshipClosedError,
    # GiftNotFoundError, NoRaceInProgressError, RaceInReviewError, GiftUndoExpiredError,
    # GiftNotUndoableError e scrittura eventi; rollback completo.
    try:
        _lock_database(db)
        if user.role not in GIFT_ANY_PILOT_ROLES:
            raise GiftUndoForbiddenError
        championship = get_championship(db, championship_id)
        if championship.is_closed:
            raise ChampionshipClosedError
        gift = _find_gift(db, championship_id, gift_id)
        race = _race_in_progress(db, championship_id)
        if race.id != gift.race_id:
            raise GiftNotUndoableError
        _ensure_not_in_review(race)
        _ensure_within_undo_window(gift)
        pilot = db.get(Pilot, gift.pilot_id)
        inventory_deck = db.get(Deck, pilot.sponsor_inventory_deck_id)
        inventory = parse_cards(inventory_deck.cards)
        key = card_key(gift.card_name)
        state = _available(inventory, _plays(db, race.id, pilot.id))
        free = next((card for card in state if card_key(card.name) == key), None)
        if free is None or free.copies_available < 1:
            raise GiftNotUndoableError
        entry = next(card for card in inventory if card_key(card.name) == key)
        pool_id = championship.sponsor_pool_deck_id
        pool_deck = db.get(Deck, pool_id) if pool_id else None
        if pool_deck is None:
            raise GiftNotUndoableError
        inventory_deck.cards = dump_cards(_without_one_copy(inventory, entry))
        pool_deck.cards = dump_cards(_with_one_more_copy(parse_cards(pool_deck.cards), entry))
        record_gift_action(db, race, pilot, gift, "card.gift_undone")
        db.delete(gift)
        db.commit()
    except Exception:
        db.rollback()
        raise


def _unseen(db: Session, championship_id: int, pilot_id: int) -> list[CardGift]:
    stmt = (
        select(CardGift)
        .join(Race, Race.id == CardGift.race_id)
        .where(
            Race.championship_id == championship_id,
            CardGift.pilot_id == pilot_id,
            CardGift.seen_at.is_(None),
        )
        .order_by(CardGift.id)
    )
    return list(db.scalars(stmt))


def list_unseen_gifts(db: Session, user: User, championship_id: int, pilot_id: int) -> list[CardGift]:
    # Notifiche non ancora viste del proprio pilota nel campionato.
    # Errori: ChampionshipNotFoundError, PilotNotFoundError.
    get_championship(db, championship_id)
    pilot = get_own_pilot(db, user, pilot_id)
    return _unseen(db, championship_id, pilot.id)


def mark_gifts_seen(db: Session, user: User, championship_id: int, pilot_id: int) -> None:
    # Segna come viste tutte le notifiche del pilota nel campionato.
    # Errori: ChampionshipNotFoundError, PilotNotFoundError.
    get_championship(db, championship_id)
    pilot = get_own_pilot(db, user, pilot_id)
    now = datetime.now(timezone.utc).replace(tzinfo=None)
    for gift in _unseen(db, championship_id, pilot.id):
        gift.seen_at = now
    db.commit()
