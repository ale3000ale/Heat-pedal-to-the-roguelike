from fastapi import APIRouter, HTTPException, status

from app.api.deps import AdminUser, CurrentUser, DbDep
from app.schemas.championship import (
    ChampionshipCreate,
    ChampionshipDetail,
    ChampionshipRead,
    EnrollRequest,
    EntrantRead,
)
from app.schemas.gold import GoldRulesData
from app.services.championships import (
    ChampionshipClosedError,
    ChampionshipNameTakenError,
    ChampionshipNotFoundError,
    ChampionshipOpenError,
    PilotWithoutTeamError,
    close_championship,
    create_championship,
    delete_championship,
    enroll_pilot,
    get_championship,
    list_championships,
    list_entrants,
    set_gold_rules,
)
from app.services.gold import rules_of
from app.services.pilots import PilotInActiveChampionshipError, PilotNotFoundError
from app.services.pools import PoolNotFoundError, PoolRuleError

router = APIRouter(tags=["championships"])

NOT_FOUND = HTTPException(status.HTTP_404_NOT_FOUND, "Campionato non trovato")


def _read(db, championship) -> ChampionshipRead:
    return ChampionshipRead(
        id=championship.id,
        name=championship.name,
        date=championship.date,
        is_closed=championship.is_closed,
        pilots_count=len(list_entrants(db, championship.id)),
    )


@router.get("", response_model=list[ChampionshipRead])
def list_all(user: CurrentUser, db: DbDep):
    # Tutti i campionati, attivi e chiusi.
    return [_read(db, championship) for championship in list_championships(db)]


@router.post("", response_model=ChampionshipRead, status_code=status.HTTP_201_CREATED)
def create(data: ChampionshipCreate, admin: AdminUser, db: DbDep):
    # Crea un campionato (solo admin) con le pool di modifiche e sponsor scelte; 404 se
    # una pool non esiste, 422 se non è del tipo giusto, 409 se il nome è in uso.
    try:
        championship = create_championship(
            db, data.name, data.pool_id, data.sponsor_pool_id
        )
        return _read(db, championship)
    except PoolNotFoundError:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Pool non trovata")
    except PoolRuleError as exc:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_CONTENT, str(exc))
    except ChampionshipNameTakenError:
        raise HTTPException(status.HTTP_409_CONFLICT, "Nome già in uso")


@router.get("/{championship_id}", response_model=ChampionshipDetail)
def detail(championship_id: int, user: CurrentUser, db: DbDep):
    # Dettaglio con i piloti iscritti.
    try:
        championship = get_championship(db, championship_id)
    except ChampionshipNotFoundError:
        raise NOT_FOUND
    pilots = [EntrantRead.model_validate(p) for p in list_entrants(db, championship.id)]
    return ChampionshipDetail(**_read(db, championship).model_dump(), pilots=pilots)


@router.get("/{championship_id}/gold-rules", response_model=GoldRulesData)
def read_gold_rules(championship_id: int, user: CurrentUser, db: DbDep):
    # Le regole dell'oro per gara di questo campionato.
    try:
        championship = get_championship(db, championship_id)
    except ChampionshipNotFoundError:
        raise NOT_FOUND
    return GoldRulesData.from_rules(rules_of(championship))


@router.put("/{championship_id}/gold-rules", response_model=GoldRulesData)
def change_gold_rules(
    championship_id: int, data: GoldRulesData, admin: AdminUser, db: DbDep
):
    # Cambia le regole dell'oro (solo admin, campionato attivo): valgono dalla prossima gara.
    try:
        championship = set_gold_rules(db, championship_id, data.to_rules())
    except ChampionshipNotFoundError:
        raise NOT_FOUND
    except ChampionshipClosedError:
        raise HTTPException(status.HTTP_409_CONFLICT, "Campionato chiuso")
    return GoldRulesData.from_rules(rules_of(championship))


@router.post("/{championship_id}/close", response_model=ChampionshipRead)
def close(championship_id: int, admin: AdminUser, db: DbDep):
    # Chiude il campionato (solo admin); 409 se è già chiuso.
    try:
        return _read(db, close_championship(db, championship_id))
    except ChampionshipNotFoundError:
        raise NOT_FOUND
    except ChampionshipClosedError:
        raise HTTPException(status.HTTP_409_CONFLICT, "Campionato già chiuso")


@router.post(
    "/{championship_id}/pilots",
    response_model=EntrantRead,
    status_code=status.HTTP_201_CREATED,
)
def enroll(championship_id: int, data: EnrollRequest, user: CurrentUser, db: DbDep):
    # Iscrive un proprio pilota e lo reimposta.
    try:
        return enroll_pilot(db, user, championship_id, data.pilot_id)
    except ChampionshipNotFoundError:
        raise NOT_FOUND
    except PilotNotFoundError:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Pilota non trovato")
    except ChampionshipClosedError:
        raise HTTPException(status.HTTP_409_CONFLICT, "Campionato chiuso")
    except PilotWithoutTeamError:
        raise HTTPException(status.HTTP_409_CONFLICT, "Il pilota deve avere un team")
    except PilotInActiveChampionshipError:
        raise HTTPException(
            status.HTTP_409_CONFLICT, "Il pilota è già iscritto a un campionato attivo"
        )

@router.delete("/{championship_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove(championship_id: int, admin: AdminUser, db: DbDep):
    # Cancella un campionato chiuso con tutto lo storico (solo admin).
    try:
        delete_championship(db, championship_id)
    except ChampionshipNotFoundError:
        raise NOT_FOUND
    except ChampionshipOpenError:
        raise HTTPException(
            status.HTTP_409_CONFLICT, "Chiudi il campionato prima di cancellarlo"
        )
