from fastapi import APIRouter, HTTPException, status

from app.api.deps import CurrentUser, DbDep
from app.schemas.team import TeamRead, TeamWrite
from app.services.teams import (
    TeamInActiveChampionshipError,
    TeamNameTakenError,
    TeamNotFoundError,
    create_team,
    delete_team,
    list_teams,
    rename_team,
)

router = APIRouter(tags=["teams"])

NOT_FOUND = HTTPException(status.HTTP_404_NOT_FOUND, "Team non trovato")


@router.get("", response_model=list[TeamRead])
def list_my_teams(user: CurrentUser, db: DbDep):
    # Elenco dei team dell'utente loggato.
    return list_teams(db, user)


@router.post("", response_model=TeamRead, status_code=status.HTTP_201_CREATED)
def create(data: TeamWrite, user: CurrentUser, db: DbDep):
    # Crea un team; 409 se il nome è già in uso.
    try:
        return create_team(db, user, data.name)
    except TeamNameTakenError:
        raise HTTPException(status.HTTP_409_CONFLICT, "Nome già in uso")


@router.patch("/{team_id}", response_model=TeamRead)
def rename(team_id: int, data: TeamWrite, user: CurrentUser, db: DbDep):
    # Rinomina un proprio team; 404 se non è tuo, 409 se il nome è in uso.
    try:
        return rename_team(db, user, team_id, data.name)
    except TeamNotFoundError:
        raise NOT_FOUND
    except TeamNameTakenError:
        raise HTTPException(status.HTTP_409_CONFLICT, "Nome già in uso")


@router.delete("/{team_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove(team_id: int, user: CurrentUser, db: DbDep):
    # Elimina (nasconde) un proprio team e i suoi piloti.
    try:
        delete_team(db, user, team_id)
    except TeamNotFoundError:
        raise NOT_FOUND
    except TeamInActiveChampionshipError:
        raise HTTPException(
            status.HTTP_409_CONFLICT,
            "Un pilota del team è iscritto a un campionato attivo",
        )