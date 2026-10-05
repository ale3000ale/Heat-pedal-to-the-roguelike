from datetime import datetime

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.db.models.pilot import Pilot
from app.db.models.race import Race, RaceResult
from app.services.championships import (
    ChampionshipClosedError,
    get_championship,
    list_entrants,
    pilot_totals,
)

# Punti per posizione di arrivo; dalla 7ª in poi si prendono 0 punti.
POINTS_BY_POSITION = {1: 9, 2: 6, 3: 4, 4: 3, 5: 2, 6: 1}
MAX_RACE_PILOTS = 12


class RaceNotFoundError(Exception):
    """La gara non esiste in questo campionato."""


class RaceAlreadyClosedError(Exception):
    """La gara ha già i risultati: solo l'admin può correggerli."""


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


def set_results(
    db: Session,
    championship_id: int,
    race_id: int,
    entries: list[tuple[int, int]],
    can_correct: bool = False,
) -> Race:
    # entries: (pilot_id, punti sponsor) nell'ordine di arrivo.
    # Una gara è chiusa quando ha almeno un risultato: da allora solo chi ha
    # can_correct (l'admin) può sostituirli. Il campionato deve essere attivo.
    championship = get_championship(db, championship_id)
    race = get_race(db, championship_id, race_id)
    if championship.is_closed:
        raise ChampionshipClosedError
    old_sponsor = {
        r.pilot_id: r.sponsor_points
        for r in db.scalars(select(RaceResult).where(RaceResult.race_id == race.id))
    }
    if old_sponsor and not can_correct:
        raise RaceAlreadyClosedError
    pilot_ids = [pilot_id for pilot_id, _ in entries]
    if not pilot_ids:
        raise RaceResultError("Serve almeno un pilota")
    if len(pilot_ids) > MAX_RACE_PILOTS:
        raise RaceResultError(f"Una gara può avere al massimo {MAX_RACE_PILOTS} piloti")
    if len(set(pilot_ids)) != len(pilot_ids):
        raise RaceResultError("Pilota ripetuto")
    if any(sponsor < 0 for _, sponsor in entries):
        raise RaceResultError("I punti sponsor non possono essere negativi")
    enrolled = {pilot.id for pilot in list_entrants(db, championship_id)}
    if not set(pilot_ids) <= enrolled:
        raise RaceResultError("Tutti i piloti devono essere iscritti al campionato")
    db.query(RaceResult).where(RaceResult.race_id == race.id).delete()
    for position, (pilot_id, sponsor) in enumerate(entries, start=1):
        db.add(
            RaceResult(
                race_id=race.id,
                pilot_id=pilot_id,
                position=position,
                points=POINTS_BY_POSITION.get(position, 0),
                sponsor_points=sponsor,
            )
        )
    db.flush()
    _sync_pilot_points(db, championship_id)
    _apply_sponsor_delta(db, old_sponsor, dict(entries))
    db.commit()
    db.refresh(race)
    return race


def _sync_pilot_points(db: Session, championship_id: int) -> None:
    # Allinea Pilot.point al totale ottenuto nel campionato.
    totals = pilot_totals(db, championship_id)
    for pilot in list_entrants(db, championship_id):
        pilot.point = totals.get(pilot.id, (0, 0))[0]


def _apply_sponsor_delta(db: Session, old: dict[int, int], new: dict[int, int]) -> None:
    # Lo sponsor si può spendere: si applica solo la differenza rispetto ai valori
    # precedenti della gara, senza ricalcolare il totale (mai sotto zero).
    for pilot_id in old.keys() | new.keys():
        pilot = db.get(Pilot, pilot_id)
        if pilot is not None:
            pilot.sponsor = max(0, pilot.sponsor + new.get(pilot_id, 0) - old.get(pilot_id, 0))


def race_table(
    db: Session, championship_id: int, race_id: int
) -> tuple[Race, list[tuple[Pilot, int | None, int, int]]]:
    # Tutti gli iscritti: prima chi ha corso (per posizione), poi gli altri a 0 punti.
    # Ogni riga: (pilota, posizione, punti, punti sponsor).
    race = get_race(db, championship_id, race_id)
    entrants = list_entrants(db, championship_id)
    results = {
        r.pilot_id: r for r in db.scalars(select(RaceResult).where(RaceResult.race_id == race.id))
    }
    raced = sorted((p for p in entrants if p.id in results), key=lambda p: results[p.id].position)
    absent = [p for p in entrants if p.id not in results]
    rows = [(p, results[p.id].position, results[p.id].points, results[p.id].sponsor_points) for p in raced]
    rows += [(p, None, 0, 0) for p in absent]
    return race, rows
