from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.db.models import User
from app.db.models.championship import Championship, ChampionshipPilot
from app.db.models.pilot import Pilot
from app.db.models.team import Team
from app.services.names import clean_name, name_key


class TeamNotFoundError(Exception):
    """Il team non esiste, è stato eliminato o appartiene a un altro utente."""


class TeamNameTakenError(Exception):
    """Esiste già un team con questo nome (anche tra quelli nascosti)."""


class TeamInActiveChampionshipError(Exception):
    """Un pilota del team è iscritto a un campionato attivo."""


def _now() -> datetime:
    # Data e ora UTC senza fuso, coerenti con le altre colonne DateTime.
    return datetime.now(timezone.utc).replace(tzinfo=None)


def pilots_in_active_championship(db: Session, pilot_ids: list[int]) -> bool:
    # Vero se almeno uno dei piloti è iscritto a un campionato non chiuso.
    if not pilot_ids:
        return False
    stmt = (
        select(ChampionshipPilot.id)
        .join(Championship, Championship.id == ChampionshipPilot.championship_id)
        .where(ChampionshipPilot.pilot_id.in_(pilot_ids), Championship.is_closed.is_(False))
        .limit(1)
    )
    return db.scalar(stmt) is not None


def list_teams(db: Session, user: User) -> list[Team]:
    # I team visibili dell'utente, in ordine alfabetico.
    stmt = (
        select(Team)
        .where(Team.user_id == user.id, Team.deleted_at.is_(None))
        .order_by(Team.name_key)
    )
    return list(db.scalars(stmt))


def get_own_team(db: Session, user: User, team_id: int) -> Team:
    # Restituisce il team solo se è dell'utente e non è eliminato. Per tutti gli altri
    # casi lancia lo stesso errore, così non si scopre se il team di altri esiste.
    stmt = select(Team).where(
        Team.id == team_id, Team.user_id == user.id, Team.deleted_at.is_(None)
    )
    team = db.scalar(stmt)
    if team is None:
        raise TeamNotFoundError
    return team


def _name_taken(db: Session, key: str, exclude_id: int | None = None) -> bool:
    # Controlla la chiave su tutte le righe, comprese quelle nascoste.
    stmt = select(Team.id).where(Team.name_key == key)
    if exclude_id is not None:
        stmt = stmt.where(Team.id != exclude_id)
    return db.scalar(stmt) is not None


def create_team(db: Session, user: User, name: str) -> Team:
    # Crea un team per l'utente; il nome deve essere unico in tutto il gioco.
    name = clean_name(name)
    key = name_key(name)
    if _name_taken(db, key):
        raise TeamNameTakenError
    team = Team(name=name, name_key=key, user_id=user.id)
    db.add(team)
    try:
        db.commit()
    except IntegrityError:
        # Due richieste simultanee con lo stesso nome: vince il vincolo del database.
        db.rollback()
        raise TeamNameTakenError
    db.refresh(team)
    return team


def rename_team(db: Session, user: User, team_id: int, name: str) -> Team:
    # Cambia il nome di un team dell'utente (si può cambiare solo la grafia
    # delle maiuscole: la chiave esclude il team stesso dal controllo).
    team = get_own_team(db, user, team_id)
    name = clean_name(name)
    key = name_key(name)
    if _name_taken(db, key, exclude_id=team.id):
        raise TeamNameTakenError
    team.name = name
    team.name_key = key
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise TeamNameTakenError
    db.refresh(team)
    return team


def delete_team(db: Session, user: User, team_id: int) -> None:
    # Eliminazione logica: nasconde il team e i suoi piloti, senza cancellare righe.
    # Rifiutata se un pilota è in un campionato attivo.
    team = get_own_team(db, user, team_id)
    pilots = list(
        db.scalars(select(Pilot).where(Pilot.team_id == team.id, Pilot.deleted_at.is_(None)))
    )
    if pilots_in_active_championship(db, [pilot.id for pilot in pilots]):
        raise TeamInActiveChampionshipError
    now = _now()
    team.deleted_at = now
    for pilot in pilots:
        pilot.deleted_at = now
    db.commit()