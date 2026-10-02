from sqlalchemy import delete, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.db.models import User
from app.db.models.championship import Championship, ChampionshipPilot
from app.db.models.deck import Deck
from app.db.models.pilot import Pilot
from app.db.models.race import Race, RaceResult
from app.services.cards import STARTER_INVENTORY, dump_cards
from app.services.names import clean_name, name_key
from app.services.pilots import PilotInActiveChampionshipError, get_own_pilot
from app.services.pools import get_base_pool, get_pool
from app.services.teams import pilots_in_active_championship


class ChampionshipNotFoundError(Exception):
    """Il campionato non esiste."""


class ChampionshipNameTakenError(Exception):
    """Esiste già un campionato con questo nome."""


class ChampionshipClosedError(Exception):
    """Il campionato è chiuso (sola lettura)."""

class ChampionshipOpenError(Exception):
    """Il campionato è ancora attivo: va chiuso prima di cancellarlo."""

class PilotWithoutTeamError(Exception):
    """Per iscriversi a un campionato il pilota deve avere un team."""


def list_championships(db: Session) -> list[Championship]:
    # Tutti i campionati, attivi e chiusi, dal più recente.
    stmt = select(Championship).order_by(Championship.date.desc(), Championship.id.desc())
    return list(db.scalars(stmt))


def get_championship(db: Session, championship_id: int) -> Championship:
    championship = db.get(Championship, championship_id)
    if championship is None:
        raise ChampionshipNotFoundError
    return championship


def list_entrants(db: Session, championship_id: int) -> list[Pilot]:
    # Piloti iscritti, in ordine alfabetico (anche quelli poi nascosti dai giocatori:
    # restano nello storico del campionato).
    stmt = (
        select(Pilot)
        .join(ChampionshipPilot, ChampionshipPilot.pilot_id == Pilot.id)
        .where(ChampionshipPilot.championship_id == championship_id)
        .order_by(Pilot.name_key)
    )
    return list(db.scalars(stmt))


def create_championship(db: Session, name: str, pool_id: int | None = None) -> Championship:
    # Crea un campionato con una copia indipendente della pool scelta (di base se omessa).
    name = clean_name(name)
    key = name_key(name)
    if db.scalar(select(Championship.id).where(Championship.name_key == key)) is not None:
        raise ChampionshipNameTakenError
    pool = get_pool(db, pool_id) if pool_id is not None else get_base_pool(db)
    deck = Deck(cards=pool.base_cards or dump_cards([]), id_prototype=pool.id)
    db.add(deck)
    db.flush()
    championship = Championship(name=name, name_key=key, pool_deck_id=deck.id)
    db.add(championship)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise ChampionshipNameTakenError
    db.refresh(championship)
    return championship


def close_championship(db: Session, championship_id: int) -> Championship:
    # Chiude il campionato (anche con gare non finite): da qui in poi è in sola lettura.
    championship = get_championship(db, championship_id)
    if championship.is_closed:
        raise ChampionshipClosedError
    championship.is_closed = True
    db.commit()
    db.refresh(championship)
    return championship


def enroll_pilot(db: Session, user: User, championship_id: int, pilot_id: int) -> Pilot:
    # Iscrive un pilota dell'utente e lo reimposta: inventario iniziale, mazzo da gioco
    # vuoto, gold, sponsor e point a zero.
    championship = get_championship(db, championship_id)
    if championship.is_closed:
        raise ChampionshipClosedError
    pilot = get_own_pilot(db, user, pilot_id)
    if pilot.team_id is None:
        raise PilotWithoutTeamError
    if pilots_in_active_championship(db, [pilot.id]):
        raise PilotInActiveChampionshipError
    db.get(Deck, pilot.inventory_deck_id).cards = dump_cards(STARTER_INVENTORY)
    db.get(Deck, pilot.game_deck_id).cards = dump_cards([])
    pilot.gold = 0
    pilot.sponsor = 0
    pilot.point = 0
    db.add(ChampionshipPilot(championship_id=championship.id, pilot_id=pilot.id))
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise PilotInActiveChampionshipError
    db.refresh(pilot)
    return pilot

def delete_championship(db: Session, championship_id: int) -> None:
    # Cancella un campionato chiuso con tutto il suo storico: risultati, gare, iscrizioni
    # e la copia della pool. I piloti restano. Tutto in un'unica transazione.
    championship = get_championship(db, championship_id)
    if not championship.is_closed:
        raise ChampionshipOpenError
    race_ids = select(Race.id).where(Race.championship_id == championship.id)
    db.execute(delete(RaceResult).where(RaceResult.race_id.in_(race_ids)))
    db.execute(delete(Race).where(Race.championship_id == championship.id))
    db.execute(
        delete(ChampionshipPilot).where(ChampionshipPilot.championship_id == championship.id)
    )
    pool_deck_id = championship.pool_deck_id
    db.delete(championship)
    db.flush()
    if pool_deck_id is not None:
        deck = db.get(Deck, pool_deck_id)
        if deck is not None:
            db.delete(deck)
    db.commit()