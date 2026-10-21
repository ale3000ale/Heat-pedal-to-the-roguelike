"""Iscrizioni live su SQLite sintetico: privacy, consegna e atomicita'."""
import json

import pytest
from pydantic import ValidationError
from sqlalchemy import func, select

from app.config import SESSION_COOKIE_NAME
from app.db.models import ChampionshipPilot, Deck, EventLog, Pilot, User
from app.schemas.events import EventCreate
from app.services.championships import enroll_pilot
from app.services.event_log import append_event, read_events
from app.services.event_stream import poll_events
from tests.test_championships_api import (
    enroll, make_admin, make_pilot, make_player, new_championship, seed_base_pool,
)

TOPIC = "championship.pilots_changed"


@pytest.fixture()
def enrollment_case(make_client, session_factory):
    seed_base_pool(session_factory)
    admin = make_admin(make_client, session_factory)
    owner = make_player(make_client, "owner")
    member = make_player(make_client, "member")
    observer = make_player(make_client, "observer")
    champ = new_championship(admin, "Enrollment").json()["id"]
    pilot = make_pilot(owner, "Entrante")
    member_pilot = make_pilot(member, "Iscritto")
    assert enroll(member, champ, member_pilot).status_code == 201
    with session_factory() as db:
        ids = {user.username: user.id for user in db.scalars(select(User))}
        cursor = db.scalar(select(func.max(EventLog.id))) or 0
    return dict(admin=admin, owner=owner, member=member, observer=observer,
                champ=champ, pilot=pilot, ids=ids, cursor=cursor)


def event_ids(factory):
    with factory() as db:
        return list(db.scalars(select(EventLog.id).order_by(EventLog.id)))


def test_signal_reaches_members_and_observers_without_details(enrollment_case, session_factory, make_client):
    c = enrollment_case
    assert c["observer"].get(f"/api/championships/{c['champ']}").status_code == 200
    assert enroll(c["owner"], c["champ"], c["pilot"]).status_code == 201
    with session_factory() as db:
        rows = list(db.scalars(select(EventLog).where(EventLog.id > c["cursor"])))
        assert len(rows) == 1
        row = rows[0]
        assert row.type == TOPIC
        assert row.pilot_id is None and row.recipient_user_id is None
        assert json.loads(row.payload) == {}
        for uid in c["ids"].values():
            assert [r.id for r in read_events(db, uid, c["cursor"])] == [row.id]
        assert read_events(db, 999999, c["cursor"]) == []
    token = c["observer"].cookies.get(SESSION_COOKIE_NAME)
    assert token
    frames, cursor = poll_events(session_factory, token, c["cursor"])
    assert len(frames) == 1 and f"event: {TOPIC}\n" in frames[0]
    data = json.loads(frames[0].split("data: ", 1)[1].strip())
    assert data == {"championship_id": c["champ"], "pilot_id": None, "payload": {}}
    assert poll_events(session_factory, token, cursor) == ([], cursor)
    assert make_client().get("/api/events/stream").status_code == 401


def test_observer_exception_does_not_broaden_other_events(enrollment_case, session_factory):
    c = enrollment_case
    assert enroll(c["owner"], c["champ"], c["pilot"]).status_code == 201
    with session_factory() as db:
        append_event(db, EventCreate(type="card.gifted", championship_id=c["champ"],
                                     recipient_user_id=c["ids"]["owner"], payload={"gift_id": 7}))
        append_event(db, EventCreate(type="cards.changed", championship_id=c["champ"], payload={}))
        db.add(EventLog(type=TOPIC, championship_id=c["champ"], payload='{"private":"hidden"}'))
        db.add(EventLog(type=TOPIC, championship_id=c["champ"], pilot_id=c["pilot"], payload="{}"))
        db.add(EventLog(type=TOPIC, championship_id=c["champ"],
                        recipient_user_id=c["ids"]["owner"], payload="{}"))
        db.commit()
        seen = read_events(db, c["ids"]["observer"], c["cursor"])
        assert [row.type for row in seen] == [TOPIC]
        assert all(row.pilot_id is None and row.payload == "{}" for row in seen)
        assert any(row.type == "cards.changed" for row in read_events(db, c["ids"]["member"], c["cursor"]))
        for name in ("member", "observer", "capo"):
            assert all(row.type != "card.gifted" for row in read_events(db, c["ids"][name], c["cursor"]))


@pytest.mark.parametrize("mode", ["duplicate", "foreign", "closed", "no_team"])
def test_failed_enrollment_does_not_emit(enrollment_case, session_factory, mode):
    c = enrollment_case
    actor, pilot, expected = c["owner"], c["pilot"], 409
    if mode == "duplicate":
        assert enroll(actor, c["champ"], pilot).status_code == 201
    elif mode == "foreign":
        actor, expected = c["member"], 404
    elif mode == "closed":
        assert c["admin"].post(f"/api/championships/{c['champ']}/close").status_code == 200
    elif mode == "no_team":
        pilot = make_pilot(actor, "SenzaTeam", with_team=False)
    before = event_ids(session_factory)
    assert enroll(actor, c["champ"], pilot).status_code == expected
    assert event_ids(session_factory) == before


def state(factory, pilot_id, champ):
    with factory() as db:
        pilot = db.get(Pilot, pilot_id)
        decks = [db.get(Deck, key).cards for key in (
            pilot.inventory_deck_id, pilot.sponsor_inventory_deck_id, pilot.game_deck_id)]
        enrolled = db.scalar(select(ChampionshipPilot.id).where(
            ChampionshipPilot.championship_id == champ, ChampionshipPilot.pilot_id == pilot_id))
        return (pilot.gold, pilot.sponsor, pilot.point), decks, enrolled, event_ids(factory)


def test_event_failure_rolls_back_enrollment_and_reset(enrollment_case, session_factory, monkeypatch):
    c = enrollment_case
    with session_factory() as db:
        pilot = db.get(Pilot, c["pilot"])
        pilot.gold, pilot.sponsor, pilot.point = 50, 4, 7
        db.get(Deck, pilot.inventory_deck_id).cards = "[]"
        db.commit()
    before = state(session_factory, c["pilot"], c["champ"])
    def fail(db, data):
        append_event(db, data)
        db.flush()
        raise RuntimeError("event failure")
    monkeypatch.setattr("app.services.championships.append_event", fail)
    with session_factory() as db:
        with pytest.raises(RuntimeError, match="event failure"):
            enroll_pilot(db, db.get(User, c["ids"]["owner"]), c["champ"], c["pilot"])
    assert state(session_factory, c["pilot"], c["champ"]) == before


@pytest.mark.parametrize("extra", [
    {"pilot_id": 2}, {"recipient_user_id": 2}, {"payload": {"name": "hidden"}},
])
def test_enrollment_schema_forbids_details(extra):
    with pytest.raises(ValidationError):
        EventCreate(type=TOPIC, championship_id=1, **extra)
