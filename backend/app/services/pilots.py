from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.db.models import User
from app.db.models.deck import Deck
from app.db.models.pilot import Pilot
from app.services.cards import STARTER_INVENTORY, CardEntry, dump_cards, parse_cards
from app.services.names import clean_name, name_key
from app.services.teams import get_own_team, pilots_in_active_championship


class PilotNotFoundError(Exception):
    """Il pilota non esiste, è stato eliminato o appartiene a un altro utente."""


class PilotNameTakenError(Exception):
    """Esiste già un pilota con questo nome (anche tra quelli nascosti)."""


class PilotInActiveChampionshipError(Exception):
    """Il pilota è iscritto a un campionato attivo."""


def _now() -> datetime:
    # Data e ora UTC senza fuso, coerenti con le altre colonne DateTime.
    return datetime.now(timezone.utc).replace(tzinfo=None)


def _name_taken(db: Session, key: str, exclude_id: int | None = None) -> bool:
    # Controlla la chiave su tutte le righe, comprese quelle nascoste.
    stmt = select(Pilot.id).where(Pilot.name_key == key)
    if exclude_id is not None:
        stmt = stmt.where(Pilot.id != exclude_id)
    return db.scalar(stmt) is not None


def list_pilots(db: Session, user: User) -> list[Pilot]:
    # I piloti visibili dell'utente, in ordine alfabetico.
    stmt = (
        select(Pilot)
        .where(Pilot.user_id == user.id, Pilot.deleted_at.is_(None))
        .order_by(Pilot.name_key)
    )
    return list(db.scalars(stmt))


def get_own_pilot(db: Session, user: User, pilot_id: int) -> Pilot:
    # Restituisce il pilota solo se è dell'utente e non è eliminato. Per tutti gli altri
    # casi lancia lo stesso errore, così non si scopre se il pilota di altri esiste.
    stmt = select(Pilot).where(
        Pilot.id == pilot_id, Pilot.user_id == user.id, Pilot.deleted_at.is_(None)
    )
    pilot = db.scalar(stmt)
    if pilot is None:
        raise PilotNotFoundError
    return pilot


def create_pilot(db: Session, user: User, name: str, team_id: int | None = None) -> Pilot:
    # Crea un pilota con i suoi due mazzi: inventario di partenza e mazzo da gioco vuoto.
    # Il team è facoltativo, ma se indicato deve essere un team visibile dell'utente.
    name = clean_name(name)
    key = name_key(name)
    if team_id is not None:
        get_own_team(db, user, team_id)
    if _name_taken(db, key):
        raise PilotNameTakenError
    inventory = Deck(cards=dump_cards(STARTER_INVENTORY))
    game = Deck(cards=dump_cards([]))
    db.add_all([inventory, game])
    db.flush()
    pilot = Pilot(
        name=name,
        name_key=key,
        team_id=team_id,
        user_id=user.id,
        inventory_deck_id=inventory.id,
        game_deck_id=game.id,
    )
    db.add(pilot)
    try:
        db.commit()
    except IntegrityError:
        # Due richieste simultanee con lo stesso nome: vince il vincolo del database.
        db.rollback()
        raise PilotNameTakenError
    db.refresh(pilot)
    return pilot


def rename_pilot(db: Session, user: User, pilot_id: int, name: str) -> Pilot:
    # Cambia il nome di un pilota dell'utente (anche solo le maiuscole).
    # Il nome si può cambiare anche se il pilota è iscritto a un campionato.
    pilot = get_own_pilot(db, user, pilot_id)
    name = clean_name(name)
    key = name_key(name)
    if _name_taken(db, key, exclude_id=pilot.id):
        raise PilotNameTakenError
    pilot.name = name
    pilot.name_key = key
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise PilotNameTakenError
    db.refresh(pilot)
    return pilot


def set_pilot_team(db: Session, user: User, pilot_id: int, team_id: int | None) -> Pilot:
    # Assegna il pilota a un team dell'utente, oppure lo toglie (team_id=None).
    # Libero finché il pilota non è iscritto a un campionato attivo.
    pilot = get_own_pilot(db, user, pilot_id)
    if team_id is not None:
        get_own_team(db, user, team_id)
    if pilots_in_active_championship(db, [pilot.id]):
        raise PilotInActiveChampionshipError
    pilot.team_id = team_id
    db.commit()
    db.refresh(pilot)
    return pilot


def delete_pilot(db: Session, user: User, pilot_id: int) -> None:
    # Eliminazione logica: nasconde il pilota senza cancellare righe né mazzi.
    # Rifiutata se il pilota è in un campionato attivo.
    pilot = get_own_pilot(db, user, pilot_id)
    if pilots_in_active_championship(db, [pilot.id]):
        raise PilotInActiveChampionshipError
    pilot.deleted_at = _now()
    db.commit()

def pilot_decks(db: Session, pilot: Pilot) -> tuple[list[CardEntry], list[CardEntry]]:
    # Restituisce (inventario, mazzo da gioco) del pilota come elenchi di carte.
    inventory = db.get(Deck, pilot.inventory_deck_id)
    game = db.get(Deck, pilot.game_deck_id)
    return parse_cards(inventory.cards), parse_cards(game.cards)