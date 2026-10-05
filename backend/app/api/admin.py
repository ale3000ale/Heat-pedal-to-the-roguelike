from dataclasses import asdict

from fastapi import APIRouter, HTTPException, status

from app.api.deps import AdminUser, DbDep
from app.schemas.admin import DeletedPilotRead, DeletedTeamRead, PurgeRead
from app.schemas.roles import RoleSet, UserRoleRead
from app.services.cleanup import (
    DeletedItemNotFoundError,
    TeamHasPilotsError,
    list_hidden_pilots,
    list_hidden_teams,
    purge_date,
    purge_old_deleted,
    purge_pilot,
    purge_team,
)
from app.services.pilots import PilotInActiveChampionshipError
from app.services.roles import AdminRoleLockedError, UserNotFoundError, list_users, set_role

router = APIRouter(tags=["admin"])

NOT_FOUND = HTTPException(status.HTTP_404_NOT_FOUND, "Elemento nascosto non trovato")


@router.get("/users", response_model=list[UserRoleRead])
def users(admin: AdminUser, db: DbDep):
    # Elenco degli utenti con il loro ruolo (solo admin).
    return [UserRoleRead(id=u.id, username=u.username, role=u.role) for u in list_users(db)]


@router.put("/users/{user_id}/role", response_model=UserRoleRead)
def change_role(user_id: int, data: RoleSet, admin: AdminUser, db: DbDep):
    # Assegna o toglie il ruolo di giudice (solo admin); i ruoli admin non si cambiano.
    try:
        user = set_role(db, user_id, data.role)
    except UserNotFoundError:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Utente non trovato")
    except AdminRoleLockedError:
        raise HTTPException(status.HTTP_409_CONFLICT, "Il ruolo di un admin non si può cambiare")
    return UserRoleRead(id=user.id, username=user.username, role=user.role)


@router.get("/deleted/pilots", response_model=list[DeletedPilotRead])
def hidden_pilots(admin: AdminUser, db: DbDep):
    # Piloti nascosti dai giocatori (solo admin).
    return [
        DeletedPilotRead(
            id=p.id,
            name=p.name,
            owner=owner,
            deleted_at=p.deleted_at,
            purge_at=purge_date(p.deleted_at),
            can_purge=can_purge,
        )
        for p, owner, can_purge in list_hidden_pilots(db)
    ]


@router.get("/deleted/teams", response_model=list[DeletedTeamRead])
def hidden_teams(admin: AdminUser, db: DbDep):
    # Team nascosti dai giocatori (solo admin).
    return [
        DeletedTeamRead(
            id=t.id,
            name=t.name,
            owner=owner,
            deleted_at=t.deleted_at,
            purge_at=purge_date(t.deleted_at),
            pilots_count=count,
            can_purge=can_purge,
        )
        for t, owner, count, can_purge in list_hidden_teams(db)
    ]


@router.delete("/deleted/pilots/{pilot_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_pilot(pilot_id: int, admin: AdminUser, db: DbDep):
    # Elimina subito un pilota nascosto; 409 se è in un campionato attivo.
    try:
        purge_pilot(db, pilot_id)
    except DeletedItemNotFoundError:
        raise NOT_FOUND
    except PilotInActiveChampionshipError:
        raise HTTPException(
            status.HTTP_409_CONFLICT, "Il pilota è iscritto a un campionato attivo"
        )


@router.delete("/deleted/teams/{team_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_team(team_id: int, admin: AdminUser, db: DbDep):
    # Elimina subito un team nascosto; 409 se ha ancora piloti.
    try:
        purge_team(db, team_id)
    except DeletedItemNotFoundError:
        raise NOT_FOUND
    except TeamHasPilotsError:
        raise HTTPException(
            status.HTTP_409_CONFLICT, "Il team ha ancora dei piloti: eliminali prima"
        )


@router.post("/purge-expired", response_model=PurgeRead)
def purge_expired_now(admin: AdminUser, db: DbDep):
    # Esegue subito la pulizia automatica (elementi nascosti da oltre 12 mesi).
    return PurgeRead(**asdict(purge_old_deleted(db)))
