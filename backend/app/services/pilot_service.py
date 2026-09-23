# backend/app/services/pilot_service.py
# Logica di business e query riutilizzabili per i Piloti.

from typing import Optional
from sqlalchemy.orm import Session
from app.models.pilot import Pilot
from app.models.team import Team
from app.models.championship import Championship


# list_pilots_alphabetical(db)
# db: sessione SQLAlchemy attiva.
# Ritorna tutti i piloti ordinati alfabeticamente, usato nella pagina Piloti "senza login".
def list_pilots_alphabetical(db: Session) -> list[Pilot]:
    return db.query(Pilot).order_by(Pilot.name.asc()).all()


# list_pilots_without_team(db)
# db: sessione SQLAlchemy attiva.
# Ritorna i piloti che non sono associati a nessun team (campo 'team' nullo).
def list_pilots_without_team(db: Session) -> list[Pilot]:
    return db.query(Pilot).filter(Pilot.team.is_(None)).order_by(Pilot.name.asc()).all()


# list_pilots_by_user(db, user_id)
# db: sessione SQLAlchemy; user_id: id dell'utente loggato.
# Ritorna tutte le schede pilota appartenenti a un utente, in ordine alfabetico.
def list_pilots_by_user(db: Session, user_id: int) -> list[Pilot]:
    return (
        db.query(Pilot)
        .filter(Pilot.user_id == user_id)
        .order_by(Pilot.name.asc())
        .all()
    )


# search_pilots(db, name, team_name, championship_name, user_id)
# db: sessione; name/team_name/championship_name: filtri opzionali di ricerca testuale;
# user_id: se fornito, limita la ricerca ai piloti di quell'utente.
# Applica i filtri via LIKE case-insensitive sulle tabelle collegate, per la barra di ricerca Piloti.
def search_pilots(
    db: Session,
    name: Optional[str] = None,
    team_name: Optional[str] = None,
    championship_name: Optional[str] = None,
    user_id: Optional[int] = None,
) -> list[Pilot]:
    query = db.query(Pilot)
    if user_id is not None:
        query = query.filter(Pilot.user_id == user_id)
    if name:
        query = query.filter(Pilot.name.ilike(f"%{name}%"))
    if team_name:
        query = query.join(Team, Pilot.team == Team.id).filter(Team.name.ilike(f"%{team_name}%"))
    if championship_name:
        query = query.join(
            Championship, Pilot.championship_id == Championship.id
        ).filter(Championship.name.ilike(f"%{championship_name}%"))
    return query.order_by(Pilot.name.asc()).all()


# get_top_pilots_by_user(db, user_id, limit)
# db: sessione; user_id: id utente loggato; limit: numero massimo di piloti da restituire.
# Ritorna i piloti dell'utente ordinati per punteggio decrescente, usato nella Home "con login".
def get_top_pilots_by_user(db: Session, user_id: int, limit: int = 3) -> list[Pilot]:
    return (
        db.query(Pilot)
        .filter(Pilot.user_id == user_id)
        .order_by(Pilot.point.desc())
        .limit(limit)
        .all()
    )


# create_pilot(db, name, user_id, team_id, championship_id)
# db: sessione; name: nome pilota; user_id: proprietario; team_id/championship_id: associazioni opzionali.
# Crea un nuovo pilota associato all'utente loggato.
def create_pilot(
    db: Session,
    name: str,
    user_id: int,
    team_id: Optional[int] = None,
    championship_id: Optional[int] = None,
) -> Pilot:
    pilot = Pilot(
        name=name,
        user_id=user_id,
        team=team_id,
        championship_id=championship_id,
        gold=0,
        sponsor=0,
        point=0,
    )
    db.add(pilot)
    db.commit()
    db.refresh(pilot)
    return pilot
