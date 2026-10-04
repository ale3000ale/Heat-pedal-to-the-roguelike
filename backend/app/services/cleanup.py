from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

from sqlalchemy import delete, func, select
from sqlalchemy.orm import Session

from app.db.models import User
from app.db.models.championship import ChampionshipPilot
from app.db.models.deck import Deck
from app.db.models.pilot import Pilot
from app.db.models.race import RaceResult
from app.db.models.team import Team
from app.services.pilots import PilotInActiveChampionshipError
from app.services.teams import pilots_in_active_championship

# Dopo questo tempo dal nascondimento l'eliminazione definitiva è automatica.
RETENTION = timedelta(days=365)


class DeletedItemNotFoundError(Exception):
    """L'elemento non esiste oppure non è nascosto."""


class TeamHasPilotsError(Exception):
    """Il team ha ancora dei piloti (anche nascosti)."""


@dataclass
class PurgeResult:
    deleted_pilots: int = 0
    deleted_teams: int = 0
    skipped_pilots: int = 0
    skipped_teams: int = 0


def _now() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


def purge_date(deleted_at: datetime) -> datetime:
    # Quando scatta l'eliminazione automatica.
    return deleted_at + RETENTION


def _owner(db: Session, user_id: int) -> str:
    user = db.get(User, user_id)
    return user.username if user else ""


def _pilots_in_team(db: Session, team_id: int) -> int:
    stmt = select(func.count()).select_from(Pilot).where(Pilot.team_id == team_id)
    return int(db.scalar(stmt))


def list_hidden_pilots(db: Session) -> list[tuple[Pilot, str, bool]]:
    # Piloti nascosti con il nome del proprietario e se si possono eliminare ora.
    pilots = list(db.scalars(select(Pilot).where(Pilot.deleted_at.is_not(None)).order_by(Pilot.id)))
    return [
        (p, _owner(db, p.user_id), not pilots_in_active_championship(db, [p.id])) for p in pilots
    ]


def list_hidden_teams(db: Session) -> list[tuple[Team, str, int, bool]]:
    # Team nascosti con proprietario, numero di piloti rimasti e se si possono eliminare ora.
    teams = list(db.scalars(select(Team).where(Team.deleted_at.is_not(None)).order_by(Team.id)))
    rows = []
    for team in teams:
        count = _pilots_in_team(db, team.id)
        rows.append((team, _owner(db, team.user_id), count, count == 0))
    return rows


def _purge_pilot(db: Session, pilot: Pilot) -> None:
    # Eliminazione definitiva, senza commit. Rifiutata se il pilota è in un campionato attivo;
    # nei campionati chiusi cancella iscrizioni e risultati del pilota.
    if pilots_in_active_championship(db, [pilot.id]):
        raise PilotInActiveChampionshipError
    db.execute(delete(RaceResult).where(RaceResult.pilot_id == pilot.id))
    db.execute(delete(ChampionshipPilot).where(ChampionshipPilot.pilot_id == pilot.id))
    deck_ids = [d for d in (pilot.inventory_deck_id, pilot.game_deck_id) if d is not None]
    db.delete(pilot)
    db.flush()
    if deck_ids:
        db.execute(delete(Deck).where(Deck.id.in_(deck_ids)))


def _purge_team(db: Session, team: Team) -> None:
    # Eliminazione definitiva, senza commit. Rifiutata se ha ancora piloti.
    if _pilots_in_team(db, team.id) > 0:
        raise TeamHasPilotsError
    db.delete(team)
    db.flush()


def purge_pilot(db: Session, pilot_id: int) -> None:
    # Comando dell'admin: elimina subito un pilota nascosto.
    pilot = db.get(Pilot, pilot_id)
    if pilot is None or pilot.deleted_at is None:
        raise DeletedItemNotFoundError
    _purge_pilot(db, pilot)
    db.commit()


def purge_team(db: Session, team_id: int) -> None:
    # Comando dell'admin: elimina subito un team nascosto senza piloti.
    team = db.get(Team, team_id)
    if team is None or team.deleted_at is None:
        raise DeletedItemNotFoundError
    _purge_team(db, team)
    db.commit()


def purge_old_deleted(db: Session, now: datetime | None = None) -> PurgeResult:
    # Pulizia automatica: prima i piloti nascosti da oltre 12 mesi, poi i team.
    # Gli elementi bloccati vengono saltati e riprovati alla prossima esecuzione.
    cutoff = (now or _now()) - RETENTION
    result = PurgeResult()
    old_pilots = list(
        db.scalars(select(Pilot).where(Pilot.deleted_at.is_not(None), Pilot.deleted_at <= cutoff))
    )
    for pilot in old_pilots:
        try:
            _purge_pilot(db, pilot)
            result.deleted_pilots += 1
        except PilotInActiveChampionshipError:
            result.skipped_pilots += 1
    old_teams = list(
        db.scalars(select(Team).where(Team.deleted_at.is_not(None), Team.deleted_at <= cutoff))
    )
    for team in old_teams:
        try:
            _purge_team(db, team)
            result.deleted_teams += 1
        except TeamHasPilotsError:
            result.skipped_teams += 1
    db.commit()
    return result