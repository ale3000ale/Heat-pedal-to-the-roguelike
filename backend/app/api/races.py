from fastapi import APIRouter, HTTPException, status

from app.api.deps import CurrentUser, DbDep, JudgeUser
from app.schemas.race import (
    RaceCreate,
    RaceDetail,
    RaceRead,
    RaceResultRead,
    ResultsSet,
    StandingRead,
)
from app.services.championships import standings, ChampionshipClosedError, ChampionshipNotFoundError
from app.services.races import (
    RaceAlreadyClosedError,
    RaceInProgressError,
    RaceNotFoundError,
    RaceResultError,
    count_participants,
    create_race,
    list_races,
    race_table,
    set_results,
)

router = APIRouter(tags=["races"])

CHAMPIONSHIP_NOT_FOUND = HTTPException(status.HTTP_404_NOT_FOUND, "Campionato non trovato")
RACE_NOT_FOUND = HTTPException(status.HTTP_404_NOT_FOUND, "Gara non trovata")
CLOSED = HTTPException(status.HTTP_409_CONFLICT, "Campionato chiuso")
RACE_IN_PROGRESS = HTTPException(
    status.HTTP_409_CONFLICT, "C'è già una gara in corso: va terminata prima di crearne un'altra"
)
RACE_CLOSED = HTTPException(
    status.HTTP_403_FORBIDDEN, "Gara già chiusa: solo l'admin può correggere i risultati"
)


def _read(db, race) -> RaceRead:
    return RaceRead(
        id=race.id,
        number=race.number,
        date=race.date,
        participants=count_participants(db, race.id),
    )


def _detail(db, championship_id: int, race_id: int) -> RaceDetail:
    race, rows = race_table(db, championship_id, race_id)
    results = [
        RaceResultRead(
            pilot_id=p.id,
            pilot_name=p.name,
            position=position,
            points=points,
            sponsor_points=sponsor_points,
        )
        for p, position, points, sponsor_points in rows
    ]
    return RaceDetail(**_read(db, race).model_dump(), results=results)


@router.get("/{championship_id}/races", response_model=list[RaceRead])
def list_all(championship_id: int, user: CurrentUser, db: DbDep):
    # Gare del campionato, in ordine di numero.
    try:
        return [_read(db, race) for race in list_races(db, championship_id)]
    except ChampionshipNotFoundError:
        raise CHAMPIONSHIP_NOT_FOUND


@router.post(
    "/{championship_id}/races", response_model=RaceRead, status_code=status.HTTP_201_CREATED
)
def create(championship_id: int, judge: JudgeUser, db: DbDep, data: RaceCreate | None = None):
    # Crea la gara successiva (giudice o admin), solo se non ce n'è una in corso.
    try:
        return _read(db, create_race(db, championship_id, data.date if data else None))
    except ChampionshipNotFoundError:
        raise CHAMPIONSHIP_NOT_FOUND
    except ChampionshipClosedError:
        raise CLOSED
    except RaceInProgressError:
        raise RACE_IN_PROGRESS


@router.get("/{championship_id}/races/{race_id}", response_model=RaceDetail)
def detail(championship_id: int, race_id: int, user: CurrentUser, db: DbDep):
    # Risultati della gara, con gli iscritti che non hanno partecipato a 0 punti.
    try:
        return _detail(db, championship_id, race_id)
    except ChampionshipNotFoundError:
        raise CHAMPIONSHIP_NOT_FOUND
    except RaceNotFoundError:
        raise RACE_NOT_FOUND


@router.put("/{championship_id}/races/{race_id}/results", response_model=RaceDetail)
def put_results(
    championship_id: int, race_id: int, data: ResultsSet, judge: JudgeUser, db: DbDep
):
    # Chiude la gara registrando i risultati e gli sponsor (giudice o admin).
    # Se la gara ha già i risultati, solo l'admin può correggerli.
    entries = [(entry.pilot_id, entry.sponsor_points) for entry in data.results]
    try:
        set_results(
            db, championship_id, race_id, entries, can_correct=judge.role == "admin"
        )
        return _detail(db, championship_id, race_id)
    except ChampionshipNotFoundError:
        raise CHAMPIONSHIP_NOT_FOUND
    except RaceNotFoundError:
        raise RACE_NOT_FOUND
    except ChampionshipClosedError:
        raise CLOSED
    except RaceAlreadyClosedError:
        raise RACE_CLOSED
    except RaceResultError as exc:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_CONTENT, str(exc))


@router.get("/{championship_id}/standings", response_model=list[StandingRead])
def get_standings(championship_id: int, user: CurrentUser, db: DbDep):
    # Classifica del campionato: tutti gli iscritti, anche a 0 punti.
    # Nei campionati chiusi è quella congelata alla chiusura (pilot_id nullo).
    try:
        return [
            StandingRead(
                rank=row.rank,
                pilot_id=row.pilot_id,
                pilot_name=row.pilot_name,
                points=row.points,
                races_played=row.races_played,
            )
            for row in standings(db, championship_id)
        ]
    except ChampionshipNotFoundError:
        raise CHAMPIONSHIP_NOT_FOUND
