# backend/app/routers/pilots.py
# Endpoint per la pagina Piloti: elenco, ricerca, dettaglio, creazione.

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db import get_db
from app.core.deps import get_current_user_optional, get_current_user_required
from app.models.user import User
from app.models.pilot import Pilot
from app.models.team import Team
from app.models.championship import Championship
from app.schemas.pilot import PilotOut, PilotCreate
from app.services import pilot_service

router = APIRouter(prefix="/pilots", tags=["pilots"])


# _to_pilot_out(pilot, db)
# pilot: istanza Pilot dal DB; db: sessione SQLAlchemy per risolvere nomi team/campionato.
# Arricchisce il pilota con i nomi leggibili di team e campionato per la response API.
def _to_pilot_out(pilot: Pilot, db: Session) -> PilotOut:
    team_name = db.query(Team.name).filter(Team.id == pilot.team).scalar() if pilot.team else None
    champ_name = (
        db.query(Championship.name).filter(Championship.id == pilot.championship_id).scalar()
        if pilot.championship_id
        else None
    )
    return PilotOut(
        id=pilot.id, name=pilot.name, gold=pilot.gold, sponsor=pilot.sponsor, point=pilot.point,
        championship_id=pilot.championship_id, team=pilot.team, user_id=pilot.user_id,
        team_name=team_name, championship_name=champ_name,
    )


# list_pilots(search_name, search_team, search_championship, db, current_user)
# search_*: filtri opzionali da query string; db: sessione; current_user: utente autenticato o None.
# Se loggato ritorna solo i piloti dell'utente (con filtri); se anonimo ritorna tutti i piloti.
@router.get("", response_model=list[PilotOut])
def list_pilots(
    search_name: Optional[str] = None,
    search_team: Optional[str] = None,
    search_championship: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional),
):
    user_id = current_user.id if current_user else None
    pilots = pilot_service.search_pilots(db, search_name, search_team, search_championship, user_id)
    return [_to_pilot_out(p, db) for p in pilots]


# list_pilots_no_team(db)
# db: sessione SQLAlchemy attiva.
# Ritorna i piloti senza team, per la seconda colonna della pagina Piloti "senza login".
@router.get("/without-team", response_model=list[PilotOut])
def list_pilots_no_team(db: Session = Depends(get_db)):
    pilots = pilot_service.list_pilots_without_team(db)
    return [_to_pilot_out(p, db) for p in pilots]


# get_pilot(pilot_id, db)
# pilot_id: id del pilota da visualizzare; db: sessione SQLAlchemy.
# Ritorna il dettaglio di un singolo pilota per la pagina dedicata.
@router.get("/{pilot_id}", response_model=PilotOut)
def get_pilot(pilot_id: int, db: Session = Depends(get_db)):
    pilot = db.query(Pilot).filter(Pilot.id == pilot_id).first()
    if pilot is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Pilota non trovato")
    return _to_pilot_out(pilot, db)


# create_pilot(payload, db, current_user)
# payload: dati del nuovo pilota; db: sessione; current_user: utente autenticato (obbligatorio).
# Crea un pilota associato all'utente loggato.
@router.post("", response_model=PilotOut, status_code=status.HTTP_201_CREATED)
def create_pilot(
    payload: PilotCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_required),
):
    pilot = pilot_service.create_pilot(
        db, payload.name, current_user.id, payload.team, payload.championship_id
    )
    return _to_pilot_out(pilot, db)
