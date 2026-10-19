"""Operazioni sul registro: nessuna funzione esegue commit o rollback."""
import json
from datetime import datetime, timedelta, timezone

from sqlalchemy import and_, delete, or_, select
from sqlalchemy.orm import Session

from app.db.models import ChampionshipPilot, EventLog, Pilot, User
from app.schemas.events import EventCreate

RETENTION = timedelta(hours=24)
MAX_BATCH = 100


def append_event(db: Session, data: EventCreate) -> EventLog:
    """Accoda un evento validato nella transazione del chiamante.

    Parametri: sessione SQLAlchemy ed evento interno (mai dati HTTP non autorizzati).
    Ritorna la riga pendente; id disponibile dopo il flush del chiamante.
    Errori: ValidationError o ValueError per payload non JSON finito; errori SQL al
    flush per riferimenti inesistenti. Il chiamante gestisce commit e rollback.
    """
    validated = EventCreate.model_validate(data.model_dump())
    values = validated.model_dump(exclude={"payload"})
    row = EventLog(**values, payload=json.dumps(validated.payload, allow_nan=False))
    db.add(row)
    return row


def read_events(db: Session, user_id: int, after_id: int, limit: int = MAX_BATCH) -> list[EventLog]:
    """Legge eventi ordinati: privati propri, pubblici dei campionati accessibili.

    Parametri: sessione, id dell'utente autenticato dal server, cursore >= 0,
    massimo 1..100 righe. Ritorna una lista vuota per utente non esistente.
    Admin/giudice vedono gli eventi pubblici di tutti i campionati, mai i privati
    altrui; il giocatore vede i pubblici dei campionati con un proprio pilota
    iscritto e non eliminato. ValueError per cursore o limite non validi.
    Non sostituisce la verifica della sessione HTTP a ogni ciclo SSE.
    """
    if type(after_id) is not int or after_id < 0:
        raise ValueError("Cursore non valido")
    if type(limit) is not int or not 1 <= limit <= MAX_BATCH:
        raise ValueError("Limite non valido")
    role = db.scalar(select(User.role).where(User.id == user_id))
    if role is None:
        return []
    public_access = EventLog.recipient_user_id.is_(None)
    if role not in ("admin", "judge"):
        enrolled = (
            select(ChampionshipPilot.id)
            .join(Pilot, Pilot.id == ChampionshipPilot.pilot_id)
            .where(
                ChampionshipPilot.championship_id == EventLog.championship_id,
                Pilot.user_id == user_id,
                Pilot.deleted_at.is_(None),
            ).exists()
        )
        public_access = and_(public_access, enrolled)
    statement = select(EventLog).where(
        EventLog.id > after_id,
        or_(EventLog.recipient_user_id == user_id, public_access),
    ).order_by(EventLog.id).limit(limit)
    return list(db.scalars(statement))


def purge_expired_events(db: Session, now: datetime | None = None) -> int:
    """Elimina eventi piu' vecchi di 24 ore nella transazione del chiamante.

    Parametri: sessione e istante UTC opzionale per i test. Ritorna righe eliminate.
    Converte date con fuso in UTC senza fuso; date naive sono considerate UTC.
    Non elimina eventi esattamente sulla soglia; nessun commit implicito.
    """
    current = now if now is not None else datetime.now(timezone.utc)
    if current.tzinfo is not None:
        current = current.astimezone(timezone.utc).replace(tzinfo=None)
    result = db.execute(delete(EventLog).where(EventLog.created_at < current - RETENTION))
    return result.rowcount
