# backend/app/routers/championships.py
# Endpoint per la pagina Campionati e per la logica Home (ultimo campionato / classifica).

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db import get_db
from app.core.deps import get_current_user_optional
from app.models.user import User
from app.models.championship import Championship
from app.schemas.championship import ChampionshipOut, ParticipantOut
from app.services import championship_service

router = APIRouter(prefix="/championships", tags=["championships"])


# _to_out(championship, db)
# championship: istanza Championship; db: sessione SQLAlchemy per recuperare i partecipanti.
# Costruisce la response con la classifica dei partecipanti ordinata per punteggio decrescente.
def _to_out(championship: Championship, db: Session) -> ChampionshipOut:
    participants = championship_service.get_participants_ordered_by_points(db, championship.id)
    p_out = [
        ParticipantOut(pilot_id=p.pilot_id, pilot_name=p.pilot.name, points=p.points, ranking=p.ranking)
        for p in participants
    ]
    return ChampionshipOut(id=championship.id, name=championship.name, date=championship.date, deck=championship.deck, participants=p_out)


# list_championships(db)
# db: sessione SQLAlchemy attiva.
# Ritorna tutti i campionati per la pagina panoramica Campionati.
@router.get("", response_model=list[ChampionshipOut])
def list_championships(db: Session = Depends(get_db)):
    championships = championship_service.list_championships(db)
    return [_to_out(c, db) for c in championships]


# get_home_data(db, current_user)
# db: sessione SQLAlchemy; current_user: utente autenticato o None.
# Se anonimo ritorna l'ultimo campionato con classifica; se loggato ritorna anche l'ultimo campionato
# in cui ha partecipato almeno un pilota dell'utente (i top piloti sono gestiti dal router pilots).
@router.get("/home", response_model=Optional[ChampionshipOut])
def get_home_data(
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional),
):
    if current_user:
        championship = championship_service.get_latest_championship_for_user(db, current_user.id)
    else:
        championship = championship_service.get_latest_championship(db)
    if championship is None:
        return None
    return _to_out(championship, db)


# get_championship(championship_id, db)
# championship_id: id del campionato richiesto; db: sessione SQLAlchemy.
# Ritorna il dettaglio di un campionato specifico.
@router.get("/{championship_id}", response_model=ChampionshipOut)
def get_championship(championship_id: int, db: Session = Depends(get_db)):
    championship = db.query(Championship).filter(Championship.id == championship_id).first()
    if championship is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Campionato non trovato")
    return _to_out(championship, db)
