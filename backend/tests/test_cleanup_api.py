from datetime import datetime, timedelta, timezone

from app.db.models import User
from app.db.models.championship import Championship, ChampionshipPilot
from app.db.models.deck import Deck, DeckPrototype
from app.db.models.pilot import Pilot
from app.db.models.race import Race, RaceResult
from app.db.models.team import Team
from app.security import hash_password
from app.services.cards import CardEntry, dump_cards

PASSWORD = "password123"
BASE_CARDS = [CardEntry(name="Velocità 1", path="cards/starter/velocita-1.webp", copies=3)]


def make_admin(make_client, session_factory):
    client = make_client()
    with session_factory() as db:
        db.add(DeckPrototype(name="default", base_cards=dump_cards(BASE_CARDS)))
        db.add(User(username="capo", password=hash_password(PASSWORD), role="admin"))
        db.commit()
    r = client.post("/api/auth/login", json={"username": "capo", "password": PASSWORD})
    assert r.status_code == 200
    return client


def make_player(make_client, username="mario"):
    client = make_client()
    r = client.post("/api/auth/register", json={"username": username, "password": PASSWORD})
    assert r.status_code == 201
    return client


def make_team_with_pilots(player, team_name, pilot_names):
    team_id = player.post("/api/teams", json={"name": team_name}).json()["id"]
    pilot_ids = []
    for name in pilot_names:
        r = player.post("/api/pilots", json={"name": name, "team_id": team_id})
        assert r.status_code == 201
        pilot_ids.append(r.json()["id"])
    return team_id, pilot_ids


def hide_pilot(player, pilot_id):
    assert player.delete(f"/api/pilots/{pilot_id}").status_code < 300


def hide_team(player, team_id):
    assert player.delete(f"/api/teams/{team_id}").status_code < 300


def age(session_factory, days, pilot_ids=(), team_ids=()):
    # Sposta indietro nel tempo la data di nascondimento.
    moment = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(days=days)
    with session_factory() as db:
        for pilot_id in pilot_ids:
            db.get(Pilot, pilot_id).deleted_at = moment
        for team_id in team_ids:
            db.get(Team, team_id).deleted_at = moment
        db.commit()


def add_active_enrollment(session_factory, pilot_id):
    with session_factory() as db:
        championship = Championship(name=f"Attivo {pilot_id}", name_key=f"attivo {pilot_id}")
        db.add(championship)
        db.flush()
        db.add(ChampionshipPilot(championship_id=championship.id, pilot_id=pilot_id))
        db.commit()


def test_cleanup_is_admin_only(make_client, session_factory):
    make_admin(make_client, session_factory)
    player = make_player(make_client)
    anonymous = make_client()
    for client, code in ((anonymous, 401), (player, 403)):
        assert client.get("/api/admin/deleted/pilots").status_code == code
        assert client.get("/api/admin/deleted/teams").status_code == code
        assert client.delete("/api/admin/deleted/pilots/1").status_code == code
        assert client.delete("/api/admin/deleted/teams/1").status_code == code
        assert client.post("/api/admin/purge-expired").status_code == code


def test_lists_show_only_hidden_items(make_client, session_factory):
    admin = make_admin(make_client, session_factory)
    player = make_player(make_client)
    team_id, (p1, p2) = make_team_with_pilots(player, "Rossa", ["Anna", "Beppe"])
    assert admin.get("/api/admin/deleted/pilots").json() == []
    hide_pilot(player, p1)
    pilots = admin.get("/api/admin/deleted/pilots").json()
    assert [(x["id"], x["name"], x["owner"], x["can_purge"]) for x in pilots] == [
        (p1, "Anna", "mario", True)
    ]
    assert admin.get("/api/admin/deleted/teams").json() == []
    hide_team(player, team_id)
    teams = admin.get("/api/admin/deleted/teams").json()
    assert [(x["name"], x["owner"], x["pilots_count"], x["can_purge"]) for x in teams] == [
        ("Rossa", "mario", 2, False)
    ]
    assert len(admin.get("/api/admin/deleted/pilots").json()) == 2


def test_admin_purges_hidden_pilot_and_frees_the_name(make_client, session_factory):
    admin = make_admin(make_client, session_factory)
    player = make_player(make_client)
    team_id, (p1,) = make_team_with_pilots(player, "Rossa", ["Anna"])
    with session_factory() as db:
        pilot = db.get(Pilot, p1)
        deck_ids = [pilot.inventory_deck_id, pilot.game_deck_id]
    assert admin.delete(f"/api/admin/deleted/pilots/{p1}").status_code == 404
    hide_pilot(player, p1)
    assert admin.delete(f"/api/admin/deleted/pilots/{p1}").status_code == 204
    with session_factory() as db:
        assert db.get(Pilot, p1) is None
        assert all(db.get(Deck, deck_id) is None for deck_id in deck_ids)
        assert db.get(Team, team_id) is not None
    assert admin.get("/api/admin/deleted/pilots").json() == []
    assert admin.delete(f"/api/admin/deleted/pilots/{p1}").status_code == 404
    r = player.post("/api/pilots", json={"name": "Anna", "team_id": team_id})
    assert r.status_code == 201


def test_purging_a_pilot_keeps_frozen_closed_championship_standings(
    make_client, session_factory
):
    admin = make_admin(make_client, session_factory)
    player = make_player(make_client)
    team_id, (p1, p2) = make_team_with_pilots(player, "Rossa", ["Anna", "Beppe"])
    cid = admin.post("/api/championships", json={"name": "Estate"}).json()["id"]
    for pilot_id in (p1, p2):
        r = player.post(f"/api/championships/{cid}/pilots", json={"pilot_id": pilot_id})
        assert r.status_code == 201
    race_id = admin.post(f"/api/championships/{cid}/races").json()["id"]
    r = admin.put(
        f"/api/championships/{cid}/races/{race_id}/results",
        json={"results": [{"pilot_id": p1}, {"pilot_id": p2}]},
    )
    assert r.status_code == 200
    admin.post(f"/api/championships/{cid}/close")
    hide_pilot(player, p1)
    assert admin.delete(f"/api/admin/deleted/pilots/{p1}").status_code == 204
    with session_factory() as db:
        assert db.get(Championship, cid) is not None
        assert db.query(Race).count() == 1
        assert [r.pilot_id for r in db.query(RaceResult).all()] == [p2]
        assert [e.pilot_id for e in db.query(ChampionshipPilot).all()] == [p2]
    table = admin.get(f"/api/championships/{cid}/standings").json()
    assert [(x["rank"], x["pilot_name"], x["points"]) for x in table] == [
        (1, "Anna", 9),
        (2, "Beppe", 6),
    ]
    assert all(x["pilot_id"] is None for x in table)


def test_active_championship_blocks_pilot_purge(make_client, session_factory):
    admin = make_admin(make_client, session_factory)
    player = make_player(make_client)
    team_id, (p1,) = make_team_with_pilots(player, "Rossa", ["Anna"])
    hide_pilot(player, p1)
    add_active_enrollment(session_factory, p1)
    assert admin.delete(f"/api/admin/deleted/pilots/{p1}").status_code == 409
    with session_factory() as db:
        assert db.get(Pilot, p1) is not None
    assert admin.get("/api/admin/deleted/pilots").json()[0]["can_purge"] is False


def test_team_purge_needs_a_team_without_pilots(make_client, session_factory):
    admin = make_admin(make_client, session_factory)
    player = make_player(make_client)
    team_id, (p1,) = make_team_with_pilots(player, "Rossa", ["Anna"])
    assert admin.delete(f"/api/admin/deleted/teams/{team_id}").status_code == 404
    hide_team(player, team_id)
    assert admin.delete(f"/api/admin/deleted/teams/{team_id}").status_code == 409
    assert admin.delete(f"/api/admin/deleted/pilots/{p1}").status_code == 204
    assert admin.get("/api/admin/deleted/teams").json()[0]["can_purge"] is True
    assert admin.delete(f"/api/admin/deleted/teams/{team_id}").status_code == 204
    with session_factory() as db:
        assert db.get(Team, team_id) is None
    assert admin.delete(f"/api/admin/deleted/teams/{team_id}").status_code == 404
    assert player.post("/api/teams", json={"name": "Rossa"}).status_code == 201


def test_automatic_purge_removes_only_items_older_than_a_year(make_client, session_factory):
    admin = make_admin(make_client, session_factory)
    player = make_player(make_client)
    old_team, (old_pilot,) = make_team_with_pilots(player, "Vecchia", ["Anna"])
    new_team, (new_pilot,) = make_team_with_pilots(player, "Nuova", ["Beppe"])
    hide_team(player, old_team)
    hide_team(player, new_team)
    age(session_factory, 400, pilot_ids=[old_pilot], team_ids=[old_team])
    age(session_factory, 10, pilot_ids=[new_pilot], team_ids=[new_team])
    r = admin.post("/api/admin/purge-expired")
    assert r.status_code == 200
    assert r.json() == {
        "deleted_pilots": 1,
        "deleted_teams": 1,
        "skipped_pilots": 0,
        "skipped_teams": 0,
    }
    with session_factory() as db:
        assert db.get(Pilot, old_pilot) is None
        assert db.get(Team, old_team) is None
        assert db.get(Pilot, new_pilot) is not None
        assert db.get(Team, new_team) is not None
    assert admin.post("/api/admin/purge-expired").json() == {
        "deleted_pilots": 0,
        "deleted_teams": 0,
        "skipped_pilots": 0,
        "skipped_teams": 0,
    }


def test_automatic_purge_skips_blocked_items(make_client, session_factory):
    admin = make_admin(make_client, session_factory)
    player = make_player(make_client)
    team_id, (p1, p2) = make_team_with_pilots(player, "Vecchia", ["Anna", "Beppe"])
    hide_team(player, team_id)
    age(session_factory, 400, pilot_ids=[p1, p2], team_ids=[team_id])
    add_active_enrollment(session_factory, p1)
    r = admin.post("/api/admin/purge-expired")
    assert r.json() == {
        "deleted_pilots": 1,
        "deleted_teams": 0,
        "skipped_pilots": 1,
        "skipped_teams": 1,
    }
    with session_factory() as db:
        assert db.get(Pilot, p1) is not None
        assert db.get(Pilot, p2) is None
        assert db.get(Team, team_id) is not None
