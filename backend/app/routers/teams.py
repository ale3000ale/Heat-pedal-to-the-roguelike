# backend/app/routers/teams.py
# Endpoint per la pagina Team: elenco, dettaglio, creazione con validazione piloti disponibili.

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db import get_db
from app.core.deps import get_current_user_optional, get_current_user_required
from app.models.user import User
from app.models.pilot import Pilot
from app.schemas.team import TeamOut, TeamPilotOut, TeamCreate
from app.services import team_service

router = APIRouter(prefix="/teams", tags=["teams"])


# _build_team_out(team, total_points, current_user_id)
# team: istanza Team; total_points: somma punti gia' calcolata; current_user_id: id utente loggato o None.
# Costruisce la response con i piloti del team ordinati per punteggio ed evidenzia quelli dell'utente.
def _build_team_out(team, total_points: int, current_user_id: Optional[int]) -> TeamOut:
    pilots_sorted = sorted(team.pilots, key=lambda p: p.point, reverse=True)
    pilots_out = [
        TeamPilotOut(
            id=p.id, name=p.name, point=p.point, user_id=p.user_id,
            is_current_user_pilot=(current_user_id is not None and p.user_id == current_user_id),
        )
        for p in pilots_sorted
    ]
    return TeamOut(id=team.id, name=team.name, total_points=total_points, pilots=pilots_out)


# list_teams(db, current_user)
# db: sessione SQLAlchemy; current_user: utente autenticato o None.
# Se loggato ritorna solo i team dell'utente (senza duplicati); se anonimo tutti i team ordinati per punti.
@router.get("", response_model=list[TeamOut])
def list_teams(
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional),
):
    if current_user:
        rows = team_service.list_teams_by_user(db, current_user.id)
    else:
        rows = team_service.list_teams_by_points(db, ascending=True)
    uid = current_user.id if current_user else None
    return [_build_team_out(r["team"], r["total_points"], uid) for r in rows]


# create_team(payload, db, current_user)
# payload: nome del team e id del pilota dell'utente da associare; db: sessione;
# current_user: utente autenticato (obbligatorio).
# Verifica che l'utente abbia almeno un pilota disponibile (senza team) prima di creare il nuovo team.
# Passaggio critico: se non ci sono piloti disponibili, l'operazione viene bloccata con errore chiaro.
@router.post("", response_model=TeamOut, status_code=status.HTTP_201_CREATED)
def create_team(
    payload: TeamCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_required),
):
    available = team_service.get_available_user_pilots_without_team(db, current_user.id)
    if not available:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            "Non hai piloti disponibili senza team: crea un pilota o rimuovine uno da un team esistente",
        )
    if payload.pilot_id not in [p.id for p in available]:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            "Il pilota indicato non e' tuo o appartiene gia' a un team",
        )
    team = team_service.create_team(db, payload.name, payload.pilot_id)
    db.refresh(team)
    return _build_team_out(team, sum(p.point for p in team.pilots), current_user.id)
