"""Test SSE con database temporaneo e stream finito controllato, senza server reale."""
import json

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import delete

import app.api.events as events_api
from app.config import SESSION_COOKIE_NAME
from app.db.models import Championship, EventLog, User
from app.schemas.core.events import EventCreate
from app.services.core.event_log import append_event
from app.services.core.event_stream import encode_event, parse_cursor, poll_events
from app.services.accounts.sessions import create_session, delete_session


@pytest.fixture()
def stream_data(session_factory):
    with session_factory() as db:
        user = User(username="stream", password="test-only", role="admin")
        championship = Championship(name="Stream", name_key="stream")
        db.add_all([user, championship])
        db.commit()
        token = create_session(db, user.id)
        yield session_factory, token, championship.id


@pytest.mark.parametrize("value", ["", "-1", "1.5", " 1", "abc", "１２", "9223372036854775808"])
def test_invalid_cursor(value):
    with pytest.raises(ValueError):
        parse_cursor(value)


def test_cursor_and_frame():
    assert parse_cursor(None) is None
    assert parse_cursor("0") == 0
    frame = encode_event("resync", {"text": "a\nb"}, 4)
    assert frame.startswith("id: 4\nevent: resync\ndata: ")
    assert json.loads(frame.split("data: ", 1)[1]) == {"text": "a\nb"}
    assert frame.endswith("\n\n")


def test_initial_replay_and_revocation(stream_data):
    factory, token, championship_id = stream_data
    frames, cursor = poll_events(factory, token, None)
    assert "event: resync" in frames[0]
    with factory() as db:
        row = append_event(db, EventCreate(type="race.started", championship_id=championship_id))
        db.commit()
        event_id = row.id
    frames, cursor = poll_events(factory, token, cursor)
    assert cursor == event_id
    assert "event: race.started" in frames[0]
    assert poll_events(factory, token, cursor) == ([], cursor)
    with factory() as db:
        delete_session(db, token)
    assert poll_events(factory, token, cursor) is None


def test_pruned_and_future_cursor_resync(stream_data):
    factory, token, championship_id = stream_data
    with factory() as db:
        for _ in range(3):
            append_event(db, EventCreate(type="race.started", championship_id=championship_id))
        db.commit()
        db.execute(delete(EventLog))
        db.commit()
    for cursor in (0, 999):
        frames, high = poll_events(factory, token, cursor)
        assert high == 3
        assert "cursor_unavailable" in frames[0]


def test_route_auth_cursor_and_headers(stream_data, monkeypatch):
    factory, token, _ = stream_data
    app = FastAPI()
    app.include_router(events_api.router, prefix="/api/events")
    app.dependency_overrides[events_api.get_event_session_factory] = lambda: factory

    async def finite_stream(request, factory, token, initial):
        for frame in initial[0]:
            yield frame

    monkeypatch.setattr(events_api, "stream_events", finite_stream)
    with TestClient(app) as client:
        assert client.get("/api/events/stream").status_code == 401
        client.cookies.set(SESSION_COOKIE_NAME, token)
        assert client.get("/api/events/stream", headers={"Last-Event-ID": "-1"}).status_code == 422
        response = client.get("/api/events/stream")
        assert response.status_code == 200
        assert response.headers["content-type"].startswith("text/event-stream")
        assert response.headers["x-accel-buffering"] == "no"
        assert "event: resync" in response.text
