from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

from app.api.deps import CurrentUser, DbDep
from app.schemas.pilot import (
    PilotCreate,
    PilotDetail,
    PilotRead,
    PilotRename,
    PilotTeamSet,
)
from app.services.cards import MAX_GAME_DECK_CARDS
from app.services.pilot_deck import (
    GameDeckFullError,
    PilotCardNotFoundError,
    active_championship,
    move_card,
)
from app.services.pilots import (
    PilotInActiveChampionshipError,
    PilotNameTakenError,
    PilotNotFoundError,
    create_pilot,
    delete_pilot,
    get_own_pilot,
    list_pilots,
    pilot_decks,
    rename_pilot,
    set_pilot_team,
)
from app.services.teams import TeamNotFoundError

router = APIRouter(tags=["pilots"])

PILOT_NOT_FOUND = HTTPException(status.HTTP_404_NOT_FOUND, "Pilota non trovato")
TEAM_NOT_FOUND = HTTPException(status.HTTP_404_NOT_FOUND, "Team non trovato")
NAME_TAKEN = HTTPException(status.HTTP_409_CONFLICT, "Nome già in uso")
IN_CHAMPIONSHIP = HTTPException(
    status.HTTP_409_CONFLICT, "Il pilota è iscritto a un campionato attivo"
)


class ChampionshipRef(BaseModel):
    id: int
    name: str


class PilotDeckDetail(PilotDetail):
    # Dettaglio del pilota con il campionato attivo a cui è iscritto (se c'è).
    championship: ChampionshipRef | None = None


class CardMove(BaseModel):
    # La carta da spostare, indicata dal suo percorso.
    path: str


def _detail(db, pilot) -> PilotDeckDetail:
    # Costruisce il dettaglio unendo i dati del pilota ai suoi due mazzi.
    inventory, game = pilot_decks(db, pilot)
    championship = active_championship(db, pilot)
    return PilotDeckDetail(
        **PilotRead.model_validate(pilot).model_dump(),
        inventory=inventory,
        game_deck=game,
        championship=(
            ChampionshipRef(id=championship.id, name=championship.name)
            if championship
            else None
        ),
    )


def _move(db, user, pilot_id: int, data: CardMove, to_game: bool) -> PilotDeckDetail:
    try:
        return _detail(db, move_card(db, user, pilot_id, data.path, to_game))
    except PilotNotFoundError:
        raise PILOT_NOT_FOUND
    except PilotInActiveChampionshipError:
        raise HTTPException(
            status.HTTP_409_CONFLICT,
            "Il pilota è iscritto a un campionato attivo: i mazzi non si possono modificare",
        )
    except PilotCardNotFoundError:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Carta non trovata in questo mazzo")
    except GameDeckFullError:
        raise HTTPException(
            status.HTTP_409_CONFLICT,
            f"Il mazzo da gioco ha già {MAX_GAME_DECK_CARDS} carte",
        )


@router.get("", response_model=list[PilotRead])
def list_my_pilots(user: CurrentUser, db: DbDep):
    # Elenco dei piloti dell'utente loggato.
    return list_pilots(db, user)


@router.post("", response_model=PilotDeckDetail, status_code=status.HTTP_201_CREATED)
def create(data: PilotCreate, user: CurrentUser, db: DbDep):
    # Crea un pilota con i suoi mazzi; 404 se il team non è tuo, 409 se il nome è in uso.
    try:
        pilot = create_pilot(db, user, data.name, data.team_id)
    except TeamNotFoundError:
        raise TEAM_NOT_FOUND
    except PilotNameTakenError:
        raise NAME_TAKEN
    return _detail(db, pilot)


@router.get("/{pilot_id}", response_model=PilotDeckDetail)
def detail(pilot_id: int, user: CurrentUser, db: DbDep):
    # Dettaglio di un proprio pilota; 404 se non è tuo.
    try:
        pilot = get_own_pilot(db, user, pilot_id)
    except PilotNotFoundError:
        raise PILOT_NOT_FOUND
    return _detail(db, pilot)


@router.post("/{pilot_id}/deck/add", response_model=PilotDeckDetail)
def add_to_game_deck(pilot_id: int, data: CardMove, user: CurrentUser, db: DbDep):
    # Sposta una copia dall'inventario al mazzo da gioco (massimo 15 carte).
    return _move(db, user, pilot_id, data, to_game=True)


@router.post("/{pilot_id}/deck/remove", response_model=PilotDeckDetail)
def remove_from_game_deck(pilot_id: int, data: CardMove, user: CurrentUser, db: DbDep):
    # Riporta una copia dal mazzo da gioco all'inventario.
    return _move(db, user, pilot_id, data, to_game=False)


@router.patch("/{pilot_id}", response_model=PilotRead)
def rename(pilot_id: int, data: PilotRename, user: CurrentUser, db: DbDep):
    # Rinomina un proprio pilota; 404 se non è tuo, 409 se il nome è in uso.
    try:
        return rename_pilot(db, user, pilot_id, data.name)
    except PilotNotFoundError:
        raise PILOT_NOT_FOUND
    except PilotNameTakenError:
        raise NAME_TAKEN


@router.put("/{pilot_id}/team", response_model=PilotRead)
def change_team(pilot_id: int, data: PilotTeamSet, user: CurrentUser, db: DbDep):
    # Assegna o toglie il team (team_id null); 409 se il pilota è in un campionato attivo.
    try:
        return set_pilot_team(db, user, pilot_id, data.team_id)
    except PilotNotFoundError:
        raise PILOT_NOT_FOUND
    except TeamNotFoundError:
        raise TEAM_NOT_FOUND
    except PilotInActiveChampionshipError:
        raise IN_CHAMPIONSHIP


@router.delete("/{pilot_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove(pilot_id: int, user: CurrentUser, db: DbDep):
    # Elimina (nasconde) un proprio pilota; 409 se è in un campionato attivo.
    try:
        delete_pilot(db, user, pilot_id)
    except PilotNotFoundError:
        raise PILOT_NOT_FOUND
    except PilotInActiveChampionshipError:
        raise IN_CHAMPIONSHIP
