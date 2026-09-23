# backend/app/services/championship_service.py
# Logica di business per Championship e ChampionshipParticipant.

from sqlalchemy.orm import Session
from app.models.championship import Championship, ChampionshipParticipant
from app.models.pilot import Pilot


# get_latest_championship(db)
# db: sessione SQLAlchemy attiva.
# Ritorna il campionato con la data piu' recente, usato nella Home "senza login".
def get_latest_championship(db: Session) -> Championship | None:
    return db.query(Championship).order_by(Championship.date.desc()).first()


# get_participants_ordered_by_points(db, championship_id)
# db: sessione; championship_id: id del campionato di cui mostrare la classifica.
# Ritorna i partecipanti al campionato ordinati per punteggio decrescente.
def get_participants_ordered_by_points(db: Session, championship_id: int) -> list[ChampionshipParticipant]:
    return (
        db.query(ChampionshipParticipant)
        .filter(ChampionshipParticipant.championship_id == championship_id)
        .order_by(ChampionshipParticipant.points.desc())
        .all()
    )


# get_latest_championship_for_user(db, user_id)
# db: sessione; user_id: id dell'utente loggato.
# Trova l'ultimo campionato (data piu' recente) in cui almeno un pilota dell'utente ha partecipato,
# incrociando ChampionshipParticipant con i piloti posseduti dall'utente. Usato nella Home "con login".
def get_latest_championship_for_user(db: Session, user_id: int) -> Championship | None:
    return (
        db.query(Championship)
        .join(ChampionshipParticipant, ChampionshipParticipant.championship_id == Championship.id)
        .join(Pilot, Pilot.id == ChampionshipParticipant.pilot_id)
        .filter(Pilot.user_id == user_id)
        .order_by(Championship.date.desc())
        .first()
    )


# list_championships(db)
# db: sessione SQLAlchemy attiva.
# Ritorna tutti i campionati, usato nella panoramica Campionati e nella selezione del Negozio.
def list_championships(db: Session) -> list[Championship]:
    return db.query(Championship).order_by(Championship.date.desc()).all()
