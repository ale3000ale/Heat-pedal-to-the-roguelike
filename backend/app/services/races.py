from datetime import datetime

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.db.models.pilot import Pilot
from app.db.models.race import Race, RaceResult
from app.services.championships import (
    ChampionshipClosedError,
    get_championship,
    list_entrants,
)

# Punti per posizione di arrivo; dalla 7ª in poi si prendono 0 punti.
POINTS_BY_POSITION = {1: 9, 2: 6, 3: 4, 4: 3, 5: 2, 6: 1}
MAX_RACE_PILOTS = 12


class RaceNotFoundError(Exception):
    """La gara non esiste in questo campionato."""


class RaceResultError(ValueError):
    """Elenco dei risultati non valido (messaggio leggibile)."""


def list_races(db: Session, championship_id: int) -> list[Race]:
    get_championship(db, championship_id)
    stmt = select(Race).where(Race.championship_id == championship_id).order_by(Race.number)
    return list(db.scalars(stmt))


def get_race(db: Session, championship_id: int, race_id: int) -> Race:
    # La gara deve appartenere al campionato indicato.
    get_championship(db, championship_id)
    race = db.get(Race, race_id)
    if race is None or race.championship_id != championship_id:
        raise RaceNotFoundError
    return race


def create_race(db: Session, championship_id: int, date: datetime | None = None) -> Race:
    # Nuova gara con il numero successivo; non si crea in un campionato chiuso.
    championship = get_championship(db, championship_id)
    if championship.is_closed:
        raise ChampionshipClosedError
    last = db.scalar(select(func.max(Race.number)).where(Race.championship_id == championship_id))
    race = Race(championship_id=championship_id, number=(last or 0) + 1, date=date)
    db.add(race)
    db.commit()
    db.refresh(race)
    return race


def count_participants(db: Session, race_id: int) -> int:
    return db.scalar(select(func.count()).select_from(RaceResult).where(RaceResult.race_id == race_id))


def set_results(db: Session, championship_id: int, race_id: int, pilot_ids: list[int]) -> Race:
    # Registra l'ordine di arrivo (sostituisce i risultati precedenti) e ricalcola i punti.
    championship = get_championship(db, championship_id)
    race = get_race(db, championship_id, race_id)
    if championship.is_closed:
        raise ChampionshipClosedError
    if not pilot_ids:
        raise RaceResultError("Serve almeno un pilota")
    if len(pilot_ids) > MAX_RACE_PILOTS:
        raise RaceResultError(f"Una gara può avere al massimo {MAX_RACE_PILOTS} piloti")
    if len(set(pilot_ids)) != len(pilot_ids):
        raise RaceResultError("Pilota ripetuto")
    enrolled = {pilot.id for pilot in list_entrants(db, championship_id)}
    if not set(pilot_ids) <= enrolled:
        raise RaceResultError("Tutti i piloti devono essere iscritti al campionato")
    db.query(RaceResult).where(RaceResult.race_id == race.id).delete()
    for position, pilot_id in enumerate(pilot_ids, start=1):
        db.add(
            RaceResult(
                race_id=race.id,
                pilot_id=pilot_id,
                position=position,
                points=POINTS_BY_POSITION.get(position, 0),
            )
        )
    db.flush()
    _sync_pilot_points(db, championship_id)
    db.commit()
    db.refresh(race)
    return race


def _totals(db: Session, championship_id: int) -> dict[int, tuple[int, int]]:
    # Per pilota: (punti totali, gare disputate) nel campionato.
    stmt = (
        select(RaceResult.pilot_id, func.sum(RaceResult.points), func.count())
        .select_from(RaceResult)
        .join(Race, Race.id == RaceResult.race_id)
        .where(Race.championship_id == championship_id)
        .group_by(RaceResult.pilot_id)
    )
    return {pilot_id: (int(points), int(races)) for pilot_id, points, races in db.execute(stmt)}


def _sync_pilot_points(db: Session, championship_id: int) -> None:
    # Allinea Pilot.point al totale ottenuto nel campionato.
    totals = _totals(db, championship_id)
    for pilot in list_entrants(db, championship_id):
        pilot.point = totals.get(pilot.id, (0, 0))[0]


def race_table(
    db: Session, championship_id: int, race_id: int
) -> tuple[Race, list[tuple[Pilot, int | None, int]]]:
    # Tutti gli iscritti: prima chi ha corso (per posizione), poi gli altri a 0 punti.
    race = get_race(db, championship_id, race_id)
    entrants = list_entrants(db, championship_id)
    results = {
        r.pilot_id: r for r in db.scalars(select(RaceResult).where(RaceResult.race_id == race.id))
    }
    raced = sorted((p for p in entrants if p.id in results), key=lambda p: results[p.id].position)
    absent = [p for p in entrants if p.id not in results]
    rows = [(p, results[p.id].position, results[p.id].points) for p in raced]
    rows += [(p, None, 0) for p in absent]
    return race, rows


def standings(db: Session, championship_id: int) -> list[tuple[int, Pilot, int, int]]:
    # Classifica: (posizione, pilota, punti, gare disputate). A pari punti stessa posizione,
    # ordine alfabetico solo per stabilità di visualizzazione.
    get_championship(db, championship_id)
    totals = _totals(db, championship_id)
    entrants = sorted(
        list_entrants(db, championship_id),
        key=lambda p: (-totals.get(p.id, (0, 0))[0], p.name_key),
    )
    all_points = [totals.get(p.id, (0, 0))[0] for p in entrants]
    rows = []
    for pilot in entrants:
        points, races = totals.get(pilot.id, (0, 0))
        rank = 1 + sum(1 for other in all_points if other > points)
        rows.append((rank, pilot, points, races))
    return rows