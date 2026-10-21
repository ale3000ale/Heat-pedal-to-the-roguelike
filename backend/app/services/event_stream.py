"""Letture brevi del registro e codifica SSE; nessuna transazione durante l'attesa."""
import asyncio
import json
from time import monotonic

from sqlalchemy import func, select, text
from starlette.concurrency import run_in_threadpool

from app.db.models import EventLog
from app.services.event_log import read_events
from app.services.sessions import get_user_by_token


def parse_cursor(value: str | None) -> int | None:
    """Converte Last-Event-ID; ValueError per valori non decimali o oltre int64."""
    if value is None:
        return None
    if not value or len(value) > 19 or not value.isascii() or not value.isdecimal():
        raise ValueError("Last-Event-ID non valido")
    result = int(value)
    if result > 9223372036854775807:
        raise ValueError("Last-Event-ID fuori intervallo")
    return result


def encode_event(kind: str, data: dict, event_id: int | None = None) -> str:
    """Codifica un frame interno JSON su una riga; ValueError per JSON non finito."""
    prefix = f"id: {event_id}\n" if event_id is not None else ""
    return prefix + f"event: {kind}\ndata: " + json.dumps(data, allow_nan=False) + "\n\n"


def poll_events(factory, token: str, cursor: int | None) -> tuple[list[str], int] | None:
    """Verifica sessione e legge un batch, poi chiude la sessione database.

    Parametri: factory SQLAlchemy, token cookie e cursore precedente.
    Ritorna (frame, nuovo cursore), oppure None per sessione revocata/scaduta.
    Primo accesso e cursore non recuperabile richiedono snapshot via REST.
    Errori SQL/JSON propagano: nessun errore viene mascherato da successo.
    """
    with factory() as db:
        user = get_user_by_token(db, token)
        if user is None:
            return None
        oldest, latest = db.execute(select(func.min(EventLog.id), func.max(EventLog.id))).one()
        high = latest or 0
        if db.get_bind().dialect.name == "sqlite":
            sequence = db.scalar(text("SELECT seq FROM sqlite_sequence WHERE name = 'event_log'"))
            high = max(high, sequence or 0)
        expired = cursor is not None and (
            cursor > high or (oldest is not None and cursor < oldest - 1)
            or (oldest is None and cursor < high)
        )
        if cursor is None or expired:
            reason = "initial" if cursor is None else "cursor_unavailable"
            return [encode_event("resync", {"reason": reason}, high)], high
        rows = read_events(db, user.id, cursor)
        frames = [encode_event(row.type, {
            "championship_id": row.championship_id,
            "pilot_id": row.pilot_id,
            "payload": json.loads(row.payload),
        }, row.id) for row in rows]
        return frames, rows[-1].id if rows else cursor


async def stream_events(request, factory, token: str, initial):
    """Genera SSE ogni secondo; keep-alive ogni 15 s e termina alla disconnessione.

    Riceve il batch iniziale gia' autenticato. Le operazioni SQL sincrone girano
    nel thread pool e chiudono la sessione prima di ogni yield o sleep.
    Una sessione revocata produce auth.expired senza dati privati e chiude lo stream.
    Cancellazioni ed errori non vengono intercettati silenziosamente.
    """
    frames, cursor = initial
    yield "retry: 3000\n\n"
    last_sent = monotonic()
    while not await request.is_disconnected():
        for frame in frames:
            yield frame
            last_sent = monotonic()
        if monotonic() - last_sent >= 15:
            yield ": keep-alive\n\n"
            last_sent = monotonic()
        await asyncio.sleep(1)
        if await request.is_disconnected():
            return
        batch = await run_in_threadpool(poll_events, factory, token, cursor)
        if batch is None:
            yield encode_event("auth.expired", {})
            return
        frames, cursor = batch
