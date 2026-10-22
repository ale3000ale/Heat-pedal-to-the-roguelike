"""Letture carte riservate all'admin; nessun commit o modifica del DB."""
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models.championship import ChampionshipPilot
from app.db.models.deck import Deck
from app.db.models.pilot import Pilot
from app.db.models.user import User
from app.schemas.admin_pilot_cards import (
    AdminCardContainers, AdminDeckRead, AdminPilotCardsRead, AdminPilotRead,
)
from app.services.cards import parse_cards
from app.services.championships import get_championship
from app.services.races import has_race_in_progress


class CardAdminForbiddenError(Exception):
    """L'utente corrente non e' admin."""


class CardAdminPilotNotFoundError(Exception):
    """Pilota assente, nascosto o non iscritto al campionato richiesto."""


class CardAdminStateError(Exception):
    """Un riferimento ai contenitori e' assente o non indipendente."""


def _authorize(db: Session, user: User) -> None:
    """Rilegge il ruolo corrente; solleva CardAdminForbiddenError senza scrivere."""
    if db.scalar(select(User.role).where(User.id == user.id)) != "admin":
        raise CardAdminForbiddenError


def _entrants_statement(championship_id: int):
    """Query iscritti visibili con username; non seleziona password o sessioni."""
    return (
        select(Pilot, User.username)
        .join(User, User.id == Pilot.user_id)
        .join(ChampionshipPilot, ChampionshipPilot.pilot_id == Pilot.id)
        .where(ChampionshipPilot.championship_id == championship_id, Pilot.deleted_at.is_(None))
        .order_by(Pilot.name_key, Pilot.id)
    )


def _pilot_read(pilot: Pilot, username: str) -> AdminPilotRead:
    return AdminPilotRead(
        pilot_id=pilot.id, name=pilot.name, user_id=pilot.user_id, username=username,
    )


def list_admin_pilots(db: Session, user: User, championship_id: int) -> list[AdminPilotRead]:
    """Elenca gli iscritti con proprietario, anche a campionato chiuso.

    Parametri: sessione, utente autenticato e campionato richiesto.
    Ritorno: elenco ordinato. Errori: CardAdminForbiddenError o
    ChampionshipNotFoundError. Nessuna scrittura, evento o commit.
    """
    _authorize(db, user)
    get_championship(db, championship_id)
    return [_pilot_read(pilot, username) for pilot, username in db.execute(
        _entrants_statement(championship_id)
    )]


def read_admin_pilot_cards(
    db: Session, user: User, championship_id: int, pilot_id: int,
) -> AdminPilotCardsRead:
    """Legge i cinque Deck con una query e conserva i contenitori distinti.

    Parametri: sessione, admin autenticato, campionato e pilota iscritto.
    Ritorno: carte, versioni, username e stato autorevole dei blocchi.
    Errori: permessi, campionato/pilota non trovati, riferimenti incoerenti o
    CardError per JSON non valido. Le pool assenti sono esplicite, non create.
    La lettura non conferma revisioni scadute e non autorizza un futuro salvataggio:
    la scrittura dovra' ricontrollare stato, ruolo, iscrizione e versioni.
    """
    _authorize(db, user)
    championship = get_championship(db, championship_id)
    row = db.execute(_entrants_statement(championship_id).where(Pilot.id == pilot_id)).first()
    if row is None:
        raise CardAdminPilotNotFoundError
    pilot, username = row
    ids = {
        "game_deck": pilot.game_deck_id,
        "modification_inventory": pilot.inventory_deck_id,
        "sponsor_inventory": pilot.sponsor_inventory_deck_id,
        "modification_pool": championship.pool_deck_id,
        "sponsor_pool": championship.sponsor_pool_deck_id,
    }
    present = [deck_id for deck_id in ids.values() if deck_id is not None]
    if any(ids[name] is None for name in (
        "game_deck", "modification_inventory", "sponsor_inventory",
    )) or len(set(present)) != len(present):
        raise CardAdminStateError
    decks = {deck.id: deck for deck in db.scalars(
        select(Deck).where(Deck.id.in_(present)).execution_options(populate_existing=True)
    )}
    if set(decks) != set(present):
        raise CardAdminStateError
    containers = {}
    for name, deck_id in ids.items():
        if deck_id is None:
            containers[name] = AdminDeckRead(available=False, id=None, version=None)
        else:
            deck = decks[deck_id]
            containers[name] = AdminDeckRead(
                available=True, id=deck.id, version=deck.version, cards=parse_cards(deck.cards),
            )
    blocked = "Campionato chiuso" if championship.is_closed else None
    if blocked is None and has_race_in_progress(db, championship_id):
        blocked = "Gara o revisione non ancora confermata"
    return AdminPilotCardsRead(
        championship_id=championship_id, pilot=_pilot_read(pilot, username),
        read_only=blocked is not None, blocked_reason=blocked,
        containers=AdminCardContainers(**containers),
    )
