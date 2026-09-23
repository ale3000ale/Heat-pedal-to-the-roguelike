# backend/app/services/team_service.py
# Logica di business per i Team: ordinamenti, aggregazioni punti, creazione.

from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.team import Team
from app.models.pilot import Pilot


# list_teams_by_points(db, ascending)
# db: sessione SQLAlchemy; ascending: se True ordina crescente per somma punti piloti.
# Calcola la somma dei punti dei piloti di ogni team e ordina, per la pagina Team "senza login".
def list_teams_by_points(db: Session, ascending: bool = True) -> list[dict]:
    rows = (
        db.query(Team, func.coalesce(func.sum(Pilot.point), 0).label("total_points"))
        .outerjoin(Pilot, Pilot.team == Team.id)
        .group_by(Team.id)
        .order_by(func.coalesce(func.sum(Pilot.point), 0).asc() if ascending else func.coalesce(func.sum(Pilot.point), 0).desc())
        .all()
    )
    return [{"team": team, "total_points": total} for team, total in rows]


# list_teams_by_user(db, user_id)
# db: sessione; user_id: id utente loggato.
# Ritorna, senza duplicati, i team a cui appartengono i piloti dell'utente, con relativo totale punti.
def list_teams_by_user(db: Session, user_id: int) -> list[dict]:
    team_ids = (
        db.query(Pilot.team)
        .filter(Pilot.user_id == user_id, Pilot.team.isnot(None))
        .distinct()
        .all()
    )
    ids = [t[0] for t in team_ids]
    if not ids:
        return []
    rows = (
        db.query(Team, func.coalesce(func.sum(Pilot.point), 0).label("total_points"))
        .outerjoin(Pilot, Pilot.team == Team.id)
        .filter(Team.id.in_(ids))
        .group_by(Team.id)
        .all()
    )
    return [{"team": team, "total_points": total} for team, total in rows]


# get_available_user_pilots_without_team(db, user_id)
# db: sessione; user_id: id utente loggato.
# Ritorna i piloti dell'utente che non appartengono ancora a nessun team,
# necessari per validare la creazione di un nuovo team.
def get_available_user_pilots_without_team(db: Session, user_id: int) -> list[Pilot]:
    return (
        db.query(Pilot)
        .filter(Pilot.user_id == user_id, Pilot.team.is_(None))
        .all()
    )


# create_team(db, name, pilot_id)
# db: sessione; name: nome del nuovo team; pilot_id: id del pilota dell'utente da associare subito.
# Crea il team e assegna il pilota indicato.
# Passaggio critico: il pilota viene aggiornato e salvato nella stessa transazione del team.
def create_team(db: Session, name: str, pilot_id: int) -> Team:
    team = Team(name=name)
    db.add(team)
    db.flush()  # ottiene team.id senza chiudere la transazione

    pilot = db.query(Pilot).filter(Pilot.id == pilot_id).first()
    if pilot is not None:
        pilot.team = team.id

    db.commit()
    db.refresh(team)
    return team
