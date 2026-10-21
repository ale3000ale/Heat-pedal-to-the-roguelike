"""Stream SSE sulla stessa origine delle API REST."""
from typing import Annotated

from fastapi import APIRouter, Cookie, Depends, Header, HTTPException, Request
from fastapi.responses import StreamingResponse

from app.config import SESSION_COOKIE_NAME
from app.db.session import SessionLocal
from app.services.event_stream import parse_cursor, poll_events, stream_events

router = APIRouter(tags=["events"])


def get_event_session_factory():
    """Fornisce sessioni brevi indipendenti; sostituibile nei test."""
    return SessionLocal


@router.get("/stream")
def events_stream(
    request: Request,
    factory: Annotated[object, Depends(get_event_session_factory)],
    token: Annotated[str | None, Cookie(alias=SESSION_COOKIE_NAME)] = None,
    last_event_id: Annotated[str | None, Header(alias="Last-Event-ID")] = None,
):
    """Apre SSE autenticato; 401 senza sessione valida, 422 per cursore non valido."""
    if not token:
        raise HTTPException(401, "Non autenticato")
    try:
        cursor = parse_cursor(last_event_id)
    except ValueError as exc:
        raise HTTPException(422, str(exc)) from exc
    initial = poll_events(factory, token, cursor)
    if initial is None:
        raise HTTPException(401, "Non autenticato")
    return StreamingResponse(
        stream_events(request, factory, token, initial),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache, no-transform", "X-Accel-Buffering": "no"},
    )
