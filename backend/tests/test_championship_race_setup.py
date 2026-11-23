"""Setup della prossima gara: estrazione, permessi e pulizia."""
import pytest
from sqlalchemy import select

from app.db.models import User
from app.db.models.championship import Championship, ChampionshipPilot
from app.db.models.deck import Deck
from app.db.models.draft import DraftPreparation
from app.db.models.event_log import EventLog
from app.db.models.pilot import Pilot
from app.db.models.race import Race
from app.security import hash_password
from app.services.championship import race_setup
from app.services.race.races import set_results

PASSWORD = "password123"


def seed_media(monkeypatch, tmp_path, maps=("mappa-1.webp", "mappa-2.webp"), events=("evento-1.webp",)):
    # La cartella media del servizio viene sostituita solo nel test.
    for folder, names in (("maps", maps), ("events", events)):
        directory = tmp_path / "board" / folder
        directory.mkdir(parents=True, exist_ok=True)
        for name in names:
            (directory / name).write_bytes(b"webp")
    monkeypatch.setattr(race_setup, "MEDIA_DIR", tmp_path)
    monkeypatch.setattr(race_setup, "_choose", lambda values: values[-1])


def seed_championship(session_factory, name="Setup"):
    with session_factory() as db:
        championship = Championship(name=name, name_key=name.lower())
        db.add(championship)
        db.commit()
        return championship.id


def make_admin(make_client, session_factory):
    client = make_client()
    with session_factory() as db:
        db.add(User(username="capo", password=hash_password(PASSWORD), role="admin"))
        db.commit()
    assert client.post("/api/auth/login", json={"username": "capo", "password": PASSWORD}).status_code == 200
    return client


def make_player(make_client):
    client = make_client()
    assert client.post("/api/auth/register", json={"username": "mario", "password": PASSWORD}).status_code == 201
    return client


def test_setup_draws_and_publishes_cards(monkeypatch, tmp_path, make_client, session_factory):
    seed_media(monkeypatch, tmp_path)
    championship_id = seed_championship(session_factory)
    admin = make_admin(make_client, session_factory)

    response = admin.post(f"/api/championships/{championship_id}/setup")

    assert response.status_code == 200
    assert response.json()["next_map_path"] == "board/maps/mappa-2.webp"
    assert response.json()["next_event_path"] == "board/events/evento-1.webp"
    detail = admin.get(f"/api/championships/{championship_id}").json()
    assert detail["next_map_path"] == response.json()["next_map_path"]
    assert detail["next_event_path"] == response.json()["next_event_path"]
    with session_factory() as db:
        kinds = db.scalars(select(EventLog.type).where(
            EventLog.championship_id == championship_id
        )).all()
    assert kinds == ["championship.setup_changed"]
    assert admin.post(f"/api/championships/{championship_id}/setup").status_code == 409


def test_setup_requires_session_manager_and_championship(monkeypatch, tmp_path, make_client, session_factory):
    seed_media(monkeypatch, tmp_path)
    championship_id = seed_championship(session_factory)
    url = f"/api/championships/{championship_id}/setup"
    assert make_client().post(url).status_code == 401
    assert make_player(make_client).post(url).status_code == 403
    admin = make_admin(make_client, session_factory)
    assert admin.post("/api/championships/999/setup").status_code == 404


def test_setup_is_blocked_by_open_race_and_closed_championship(
    monkeypatch, tmp_path, make_client, session_factory
):
    seed_media(monkeypatch, tmp_path)
    championship_id = seed_championship(session_factory, "Occupata")
    admin = make_admin(make_client, session_factory)
    with session_factory() as db:
        db.add(Race(championship_id=championship_id, number=1))
        db.commit()
    assert admin.post(f"/api/championships/{championship_id}/setup").status_code == 409
    with session_factory() as db:
        db.query(Race).delete()
        db.get(Championship, championship_id).is_closed = True
        db.commit()
    assert admin.post(f"/api/championships/{championship_id}/setup").status_code == 409


def test_setup_is_blocked_by_active_draft(monkeypatch, tmp_path, make_client, session_factory):
    seed_media(monkeypatch, tmp_path)
    championship_id = seed_championship(session_factory, "InDraft")
    admin = make_admin(make_client, session_factory)
    with session_factory() as db:
        user_id = db.scalar(select(User.id).where(User.username == "capo"))
        db.add(DraftPreparation(
            championship_id=championship_id, creator_user_id=user_id, phase="attendance",
            state_json="{}", snapshot_json="{}",
        ))
        db.commit()
    assert admin.post(f"/api/championships/{championship_id}/setup").status_code == 409


def test_setup_without_images_does_not_save_paths(monkeypatch, tmp_path, make_client, session_factory):
    monkeypatch.setattr(race_setup, "MEDIA_DIR", tmp_path / "vuota")
    championship_id = seed_championship(session_factory, "SenzaFile")
    admin = make_admin(make_client, session_factory)

    response = admin.post(f"/api/championships/{championship_id}/setup")

    assert response.status_code == 503
    with session_factory() as db:
        championship = db.get(Championship, championship_id)
        assert championship.next_map_path is None
        assert championship.next_event_path is None


def test_first_results_clear_the_setup(monkeypatch, tmp_path, make_client, session_factory):
    seed_media(monkeypatch, tmp_path)
    championship_id = seed_championship(session_factory, "Disputata")
    admin = make_admin(make_client, session_factory)
    assert admin.post(f"/api/championships/{championship_id}/setup").status_code == 200

    with session_factory() as db:
        user_id = db.scalar(select(User.id).where(User.username == "capo"))
        decks = [Deck(cards="[]") for _ in range(3)]
        db.add_all(decks)
        db.flush()
        pilot = Pilot(
            name="Pilota", name_key="pilota", user_id=user_id,
            inventory_deck_id=decks[0].id, sponsor_inventory_deck_id=decks[1].id,
            game_deck_id=decks[2].id,
        )
        db.add(pilot)
        db.flush()
        db.add(ChampionshipPilot(championship_id=championship_id, pilot_id=pilot.id))
        race = Race(championship_id=championship_id, number=1)
        db.add(race)
        db.commit()
        set_results(db, championship_id, race.id, [(pilot.id, 0)], reviewer_id=user_id)

    detail = admin.get(f"/api/championships/{championship_id}").json()
    assert detail["next_map_path"] is None
    assert detail["next_event_path"] is None
