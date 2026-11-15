from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import User
from app.db.models.card_play import STATUS_PLAYED, STATUS_UNDONE, CardPlay
from app.db.models.deck import Deck
from app.db.models.pilot import Pilot
from app.db.models.race import Race, RaceResult
from app.services.cards.card_events import record_card_action
from app.services.cards.cards import CardEntry, card_key, parse_cards
from app.services.championship.championships import ChampionshipClosedError, get_championship
from app.services.pilots.pilots import get_own_pilot
from app.services.shop.shop_purchase import _lock_database
from app.services.shop.shop_view import PilotNotEnrolledError, is_enrolled

# Annullamenti consecutivi consentiti; si azzerano quando si gioca una nuova carta.
MAX_UNDOS = 5


class NoRaceInProgressError(Exception):
    """Nel campionato non c'è nessuna gara in corso."""


class RaceInReviewError(Exception):
    """La gara è in revisione: i giocatori non possono più giocare né annullare carte."""


class CardNotAvailableError(Exception):
    """La carta non è nell'inventario sponsor del pilota o le copie sono finite."""


class NothingToUndoError(Exception):
    """Non c'è nessuna giocata da annullare."""


class UndoLimitError(Exception):
    """Raggiunto il limite di annullamenti consecutivi."""


@dataclass
class AvailableCard:
    name: str
    path: str
    copies_total: int
    copies_available: int


@dataclass
class PlayState:
    race: Race
    pilot: Pilot
    plays: list[CardPlay]
    available: list[AvailableCard]
    undo_remaining: int
    in_review: bool


def _race_in_progress(db: Session, championship_id: int) -> Race:
    # Gara in corso = senza risultati. Errori: NoRaceInProgressError.
    has_results = select(RaceResult.race_id).where(RaceResult.race_id == Race.id).exists()
    stmt = (
        select(Race)
        .where(Race.championship_id == championship_id, ~has_results)
        .order_by(Race.number.desc())
        .limit(1)
    )
    race = db.scalar(stmt)
    if race is None:
        raise NoRaceInProgressError
    return race


def _race_to_read(db: Session, championship_id: int) -> Race:
    # Gara di cui mostrare lo stato = la più recente con la revisione delle carte non
    # ancora confermata: può essere in corso (senza risultati) o chiusa e in revisione.
    # Errori: NoRaceInProgressError.
    stmt = (
        select(Race)
        .where(Race.championship_id == championship_id, Race.review_closed_at.is_(None))
        .order_by(Race.number.desc())
        .limit(1)
    )
    race = db.scalar(stmt)
    if race is None:
        raise NoRaceInProgressError
    return race


def _authorize(
    db: Session, user: User, championship_id: int, pilot_id: int, find_race=_race_in_progress
) -> tuple[Pilot, Race]:
    # Solo il proprietario del pilota, iscritto, in un campionato attivo. La gara la sceglie
    # find_race: per giocare e annullare la gara in corso, per leggere anche quella in revisione.
    # Errori: ChampionshipNotFoundError, ChampionshipClosedError, PilotNotFoundError,
    # PilotNotEnrolledError, NoRaceInProgressError.
    championship = get_championship(db, championship_id)
    if championship.is_closed:
        raise ChampionshipClosedError
    pilot = get_own_pilot(db, user, pilot_id)
    if not is_enrolled(db, championship_id, pilot.id):
        raise PilotNotEnrolledError
    return pilot, find_race(db, championship_id)


def _ensure_not_in_review(race: Race) -> None:
    # Errori: RaceInReviewError.
    if race.review_started_at is not None:
        raise RaceInReviewError


def _plays(db: Session, race_id: int, pilot_id: int) -> list[CardPlay]:
    stmt = select(CardPlay).where(CardPlay.race_id == race_id, CardPlay.pilot_id == pilot_id)
    return list(db.scalars(stmt.order_by(CardPlay.id)))


def _available(inventory: list[CardEntry], plays: list[CardPlay]) -> list[AvailableCard]:
    # Copie disponibili = copie in inventario meno le giocate non annullate.
    used: dict[str, int] = {}
    for play in plays:
        if play.status == STATUS_PLAYED:
            key = card_key(play.card_name)
            used[key] = used.get(key, 0) + 1
    return [
        AvailableCard(
            name=card.name,
            path=card.path,
            copies_total=card.copies,
            copies_available=max(0, card.copies - used.get(card_key(card.name), 0)),
        )
        for card in inventory
    ]


def _undo_streak(plays: list[CardPlay]) -> int:
    # Annullamenti consecutivi = giocate annullate dopo l'ultima giocata ancora attiva.
    last_active = max((p.id for p in plays if p.status == STATUS_PLAYED), default=0)
    return sum(1 for p in plays if p.status == STATUS_UNDONE and p.id > last_active)


def _state(db: Session, pilot: Pilot, race: Race) -> PlayState:
    plays = _plays(db, race.id, pilot.id)
    inventory = parse_cards(db.get(Deck, pilot.sponsor_inventory_deck_id).cards)
    return PlayState(
        race=race,
        pilot=pilot,
        plays=plays,
        available=_available(inventory, plays),
        undo_remaining=max(0, MAX_UNDOS - _undo_streak(plays)),
        in_review=race.review_started_at is not None,
    )


def get_play_state(db: Session, user: User, championship_id: int, pilot_id: int) -> PlayState:
    # Giocate e copie disponibili del pilota nella gara in corso o in revisione: la lettura
    # resta consentita anche dopo i risultati, il campo in_review indica se la revisione è aperta.
    # Errori: quelli di _authorize.
    pilot, race = _authorize(db, user, championship_id, pilot_id, _race_to_read)
    return _state(db, pilot, race)


def play_card(
    db: Session, user: User, championship_id: int, pilot_id: int, card_name: str
) -> PlayState:
    # Giocata ed eventi nello stesso commit; inventario invariato fino alla chiusura.
    # Errori: quelli di _authorize, RaceInReviewError, CardNotAvailableError,
    # validazione/scrittura eventi; ogni errore provoca rollback completo.
    try:
        _lock_database(db)
        pilot, race = _authorize(db, user, championship_id, pilot_id)
        _ensure_not_in_review(race)
        state = _state(db, pilot, race)
        key = card_key(card_name)
        card = next((c for c in state.available if card_key(c.name) == key), None)
        if card is None or card.copies_available < 1:
            raise CardNotAvailableError
        play = CardPlay(race_id=race.id, pilot_id=pilot.id, card_name=card.name, card_path=card.path)
        db.add(play)
        db.flush()
        state = _state(db, pilot, race)
        record_card_action(db, race, pilot, "card.played", play.id)
        db.commit()
    except Exception:
        db.rollback()
        raise
    return state


def undo_last_play(db: Session, user: User, championship_id: int, pilot_id: int) -> PlayState:
    # Annulla l'ultima giocata attiva, fino a MAX_UNDOS volte di fila, con eventi atomici.
    # Errori: quelli di _authorize, RaceInReviewError, NothingToUndoError, UndoLimitError,
    # validazione/scrittura eventi; rollback completo su ogni errore.
    try:
        _lock_database(db)
        pilot, race = _authorize(db, user, championship_id, pilot_id)
        _ensure_not_in_review(race)
        plays = _plays(db, race.id, pilot.id)
        active = [p for p in plays if p.status == STATUS_PLAYED]
        if not active:
            raise NothingToUndoError
        if _undo_streak(plays) >= MAX_UNDOS:
            raise UndoLimitError
        active[-1].status = STATUS_UNDONE
        db.flush()
        state = _state(db, pilot, race)
        record_card_action(db, race, pilot, "card.play_undone", active[-1].id)
        db.commit()
    except Exception:
        db.rollback()
        raise
    return state
