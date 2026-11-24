"""Setup della prossima gara: estrazione, permessi e pulizia."""
import json

import pytest
from sqlalchemy import select

from app.db.models import User
from app.db.models.championship import Championship, ChampionshipPilot
from app.db.models.deck import Deck, DeckPrototype
from app.db.models.draft import DraftPreparation
from app.db.models.event_log import EventLog
from app.db.models.pilot import Pilot
from app.db.models.race import Race
from app.security import hash_password
from app.services.championship import board_pools, race_setup
from app.services.race.races import set_results

PASSWORD = "password123"


def seed_board(
    monkeypatch,
    tmp_path,
    maps=(("mappa-1.webp", 1), ("mappa-2.webp", 2)),
    events=(("evento-1.webp", 1),),
):
    # Media e catalogo JSON del servizio vengono sostituiti solo nel test.
    media = tmp_path / "media"
    json_dir = tmp_path / "JSON"
    json_dir.mkdir(parents=True, exist_ok=True)
    for folder, entries, filename in (
        ("maps", maps, "maps.json"),
        ("events", events, "events.json"),
    ):
        directory = media / "board" / folder
        directory.mkdir(parents=True, exist_ok=True)
        catalog = []
        for name, card_id in entries:
            (directory / name).write_bytes(b"webp")
            catalog.append(
                {
                    "id": card_id,
                    "nome": name.rsplit(".", 1)[0].upper(),
                    "image": f"board/{folder}/{name}",
                }
            )
        (json_dir / filename).write_text(json.dumps(catalog), encoding="utf-8")
    monkeypatch.setattr(board_pools, "MEDIA_DIR", media)
    monkeypatch.setattr(race_setup, "MEDIA_DIR", media)
    monkeypatch.setattr(board_pools, "_choose", lambda values: values[-1])


def seed_championship(session_factory, name="Setup"):
    with session_factory() as db:
        championship = Championship(name=name, name_key=name.lower())
        db.add(championship)
        db.commit()
        return championship.id


def pool_ids(session_factory, championship_id):
    with session_factory() as db:
        championship = db.get(Championship, championship_id)
        return board_pools._pool_ids(championship, "mappe"), board_pools._pool_ids(
            championship, "eventi"
        )


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
    seed_board(monkeypatch, tmp_path)
    championship_id = seed_championship(session_factory)
    admin = make_admin(make_client, session_factory)

    response = admin.post(f"/api/championships/{championship_id}/setup")

    assert response.status_code == 200
    assert response.json()["next_map_path"] == "board/maps/mappa-2.webp"
    assert response.json()["next_event_path"] == "board/events/evento-1.webp"
    detail = admin.get(f"/api/championships/{championship_id}").json()
    assert detail["next_map_path"] == response.json()["next_map_path"]
    assert detail["next_event_path"] == response.json()["next_event_path"]
    assert detail["next_map_stress"] is None
    assert detail["next_map_heat"] is None
    assert detail["next_map_curve"] is None
    assert detail["next_map_caselle"] is None
    # Il setup estrae ma non consuma: le pool contengono ancora tutte le carte.
    assert pool_ids(session_factory, championship_id) == ([1, 2], [1])
    with session_factory() as db:
        kinds = db.scalars(select(EventLog.type).where(
            EventLog.championship_id == championship_id
        )).all()
    assert kinds == ["championship.setup_changed"]
    assert admin.post(f"/api/championships/{championship_id}/setup").status_code == 409


def test_map_card_counts_reads_matching_map(monkeypatch, tmp_path):
    monkeypatch.setattr(race_setup, "MEDIA_DIR", tmp_path / "media")
    json_dir = tmp_path / "JSON"
    json_dir.mkdir()
    (json_dir / "maps.json").write_text(json.dumps([
        {"image": "board/maps/altre.webp", "stress": 9, "heat": 9, "curve": 1, "caselle": 2},
        {
            "image": "board/maps/DEUTSCHLAND.WEBP",
            "stress": 3,
            "heat": 5,
            "curve": 6,
            "caselle": 62,
        },
    ]), encoding="utf-8")

    assert race_setup.map_card_counts("board\\maps\\deutschland.webp") == (3, 5)
    assert race_setup.map_stats("board/maps/deutschland.webp") == (3, 5, 6, 62)


def test_map_card_counts_handles_missing_and_invalid_data(monkeypatch, tmp_path):
    monkeypatch.setattr(race_setup, "MEDIA_DIR", tmp_path / "media")
    assert race_setup.map_card_counts("board/maps/mappa.webp") == (None, None)
    assert race_setup.map_stats("board/maps/mappa.webp") == (None, None, None, None)

    json_dir = tmp_path / "json"
    json_dir.mkdir()
    maps_file = json_dir / "maps.json"
    maps_file.write_text("{non valido", encoding="utf-8")
    assert race_setup.map_card_counts("board/maps/mappa.webp") == (None, None)
    assert race_setup.map_stats("board/maps/mappa.webp") == (None, None, None, None)

    maps_file.write_text(json.dumps([
        {"image": "board/maps/altra.webp", "stress": 1, "heat": 2, "curve": 3, "caselle": 4},
        {
            "image": "board/maps/mappa.webp",
            "stress": "3",
            "heat": -1,
            "curve": "6",
            "caselle": -2,
        },
    ]), encoding="utf-8")
    assert race_setup.map_card_counts("board/maps/mappa.webp") == (None, None)
    assert race_setup.map_stats("board/maps/mappa.webp") == (None, None, None, None)
    assert race_setup.map_card_counts("board/maps/inesistente.webp") == (None, None)
    assert race_setup.map_stats("board/maps/inesistente.webp") == (None, None, None, None)


def test_detail_publishes_map_card_counts(monkeypatch, tmp_path, make_client, session_factory):
    seed_board(monkeypatch, tmp_path)
    json_dir = tmp_path / "JSON"
    (json_dir / "maps.json").write_text(json.dumps([
        {
            "id": 1,
            "nome": "MAPPA-1",
            "image": "board/maps/mappa-1.webp",
            "stress": 1,
            "heat": 1,
            "curve": 1,
            "caselle": 1,
        },
        {
            "id": 2,
            "nome": "MAPPA-2",
            "image": "board/maps/mappa-2.webp",
            "stress": 4,
            "heat": 7,
            "curve": 9,
            "caselle": 80,
        },
    ]), encoding="utf-8")
    championship_id = seed_championship(session_factory, "ConConteggi")
    admin = make_admin(make_client, session_factory)

    assert admin.post(f"/api/championships/{championship_id}/setup").status_code == 200
    detail = admin.get(f"/api/championships/{championship_id}").json()
    assert detail["next_map_stress"] == 4
    assert detail["next_map_heat"] == 7
    assert detail["next_map_curve"] == 9
    assert detail["next_map_caselle"] == 80


def test_setup_requires_session_manager_and_championship(monkeypatch, tmp_path, make_client, session_factory):
    seed_board(monkeypatch, tmp_path)
    championship_id = seed_championship(session_factory)
    url = f"/api/championships/{championship_id}/setup"
    assert make_client().post(url).status_code == 401
    assert make_player(make_client).post(url).status_code == 403
    admin = make_admin(make_client, session_factory)
    assert admin.post("/api/championships/999/setup").status_code == 404


def test_setup_is_blocked_by_open_race_and_closed_championship(
    monkeypatch, tmp_path, make_client, session_factory
):
    seed_board(monkeypatch, tmp_path)
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
    seed_board(monkeypatch, tmp_path)
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
    seed_board(monkeypatch, tmp_path)
    monkeypatch.setattr(board_pools, "MEDIA_DIR", tmp_path / "vuota")
    championship_id = seed_championship(session_factory, "SenzaFile")
    admin = make_admin(make_client, session_factory)

    response = admin.post(f"/api/championships/{championship_id}/setup")

    assert response.status_code == 503
    with session_factory() as db:
        championship = db.get(Championship, championship_id)
        assert championship.next_map_path is None
        assert championship.next_event_path is None


def test_first_results_consume_the_drawn_cards(monkeypatch, tmp_path, make_client, session_factory):
    seed_board(monkeypatch, tmp_path)
    championship_id = seed_championship(session_factory, "Disputata")
    admin = make_admin(make_client, session_factory)
    assert admin.post(f"/api/championships/{championship_id}/setup").status_code == 200
    # La mappa estratta è l'ultima della pool, l'evento l'unico disponibile.
    assert pool_ids(session_factory, championship_id) == ([1, 2], [1])

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
    # Alla prima registrazione dei risultati le carte estratte escono dalla pool.
    assert pool_ids(session_factory, championship_id) == ([1], [])


def test_cancel_setup_clears_paths_without_touching_pools(
    monkeypatch, tmp_path, make_client, session_factory
):
    seed_board(monkeypatch, tmp_path)
    championship_id = seed_championship(session_factory, "Annullata")
    admin = make_admin(make_client, session_factory)
    assert admin.post(f"/api/championships/{championship_id}/setup").status_code == 200

    response = admin.delete(f"/api/championships/{championship_id}/setup")

    assert response.status_code == 200
    assert response.json()["next_map_path"] is None
    assert response.json()["next_event_path"] is None
    assert pool_ids(session_factory, championship_id) == ([1, 2], [1])
    with session_factory() as db:
        kinds = db.scalars(select(EventLog.type).where(
            EventLog.championship_id == championship_id
        )).all()
    assert kinds == ["championship.setup_changed", "championship.setup_changed"]
    assert admin.delete(f"/api/championships/{championship_id}/setup").status_code == 409


def test_cancel_setup_requires_manager(monkeypatch, tmp_path, make_client, session_factory):
    seed_board(monkeypatch, tmp_path)
    championship_id = seed_championship(session_factory, "Permessi")
    url = f"/api/championships/{championship_id}/setup"
    assert make_client().delete(url).status_code == 401
    assert make_player(make_client).delete(url).status_code == 403


def test_board_pool_view_lists_catalog_and_out_of_pool(
    monkeypatch, tmp_path, make_client, session_factory
):
    seed_board(monkeypatch, tmp_path)
    championship_id = seed_championship(session_factory, "VistaPool")
    admin = make_admin(make_client, session_factory)
    with session_factory() as db:
        championship = db.get(Championship, championship_id)
        championship.map_pool_ids = json.dumps([1])
        championship.event_pool_ids = json.dumps([])
        db.commit()

    maps = admin.get(f"/api/championships/{championship_id}/board-pools/mappe")
    events = admin.get(f"/api/championships/{championship_id}/board-pools/eventi")

    assert maps.status_code == 200
    assert [(card["id"], card["in_pool"]) for card in maps.json()["cards"]] == [
        (1, True),
        (2, False),
    ]
    assert events.status_code == 200
    assert [(card["id"], card["in_pool"]) for card in events.json()["cards"]] == [
        (1, False),
    ]
    assert admin.get(f"/api/championships/{championship_id}/board-pools/altro").status_code == 404
    assert make_player(make_client).get(
        f"/api/championships/{championship_id}/board-pools/mappe"
    ).status_code == 403


def test_pool_view_shows_only_first_line_of_event_effect(monkeypatch):
    # L'effetto degli eventi ha descrizione e codifica su due righe: la vista
    # mostra soltanto la prima stringa.
    championship = Championship(name="Effetto", name_key="effetto")
    monkeypatch.setattr(board_pools, "_available_ids", lambda _championship, _kind: [1])
    monkeypatch.setattr(
        board_pools,
        "_catalog",
        lambda _kind: [
            {
                "id": 1,
                "nome": "Giro extra",
                "image": "board/events/giro-extra.webp",
                "effetto": "Giro extra e +1 carta in mano.\nlap+1,hand+1",
                "sponsor": "sì",
            }
        ],
    )

    cards = board_pools.pool_view(championship, "eventi")

    assert [(field.label, field.value) for field in cards[0].fields] == [
        ("Effetto", "Giro extra e +1 carta in mano."),
        ("Sponsor", "sì"),
    ]


def test_new_championship_receives_both_pools(monkeypatch, tmp_path, make_client, session_factory):
    seed_board(monkeypatch, tmp_path)
    admin = make_admin(make_client, session_factory)
    with session_factory() as db:
        db.add(DeckPrototype(name="default", kind="modifiche", base_cards="[]"))
        db.commit()

    response = admin.post("/api/championships", json={"name": "Nuovo"})

    assert response.status_code == 201
    assert pool_ids(session_factory, response.json()["id"]) == ([1, 2], [1])


def test_pool_view_for_uninitialized_pool_shows_all_available(monkeypatch, tmp_path, make_client, session_factory):
    seed_board(monkeypatch, tmp_path)
    championship_id = seed_championship(session_factory, "SenzaPool")
    admin = make_admin(make_client, session_factory)

    assert pool_ids(session_factory, championship_id) == (None, None)
    response = admin.get(f"/api/championships/{championship_id}/board-pools/mappe")

    assert response.status_code == 200
    assert [card["in_pool"] for card in response.json()["cards"]] == [True, True]
    # La vista non scrive: la pool resta da inizializzare fino al primo setup.
    assert pool_ids(session_factory, championship_id) == (None, None)
