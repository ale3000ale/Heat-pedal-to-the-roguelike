from app.db.models.championship import Championship, ChampionshipPilot
from app.db.models.deck import Deck
from app.db.models.pilot import Pilot
from app.db.models.team import Team

PASSWORD = "password123"


def register(client, username="mario"):
    # Crea un utente (che resta loggato nel client) e ne restituisce l'id.
    r = client.post("/api/auth/register", json={"username": username, "password": PASSWORD})
    assert r.status_code == 201
    return r.json()["id"]


def create_team(client, name="Scuderia Rossa"):
    return client.post("/api/teams", json={"name": name})


def add_pilot(session_factory, user_id, team_id, name="Pilota Uno"):
    # Inserisce un pilota direttamente nel database, con i suoi due mazzi vuoti
    # (l'API dei piloti non esiste ancora).
    with session_factory() as db:
        inventory, game = Deck(cards="[]"), Deck(cards="[]")
        db.add_all([inventory, game])
        db.flush()
        pilot = Pilot(
            name=name,
            name_key=name.casefold(),
            user_id=user_id,
            team_id=team_id,
            inventory_deck_id=inventory.id,
            game_deck_id=game.id,
        )
        db.add(pilot)
        db.commit()
        return pilot.id


def enroll(session_factory, pilot_id, closed=False):
    # Iscrive il pilota a un nuovo campionato, aperto o chiuso.
    with session_factory() as db:
        championship = Championship(
            name=f"Campionato {pilot_id}", name_key=f"campionato {pilot_id}", is_closed=closed
        )
        db.add(championship)
        db.flush()
        db.add(ChampionshipPilot(championship_id=championship.id, pilot_id=pilot_id))
        db.commit()


def pilot_deleted_at(session_factory, pilot_id):
    with session_factory() as db:
        return db.get(Pilot, pilot_id).deleted_at


def test_teams_require_login(client):
    assert client.get("/api/teams").status_code == 401
    assert create_team(client).status_code == 401
    assert client.patch("/api/teams/1", json={"name": "Altro"}).status_code == 401
    assert client.delete("/api/teams/1").status_code == 401


def test_create_team_cleans_name_and_lists_it(client):
    register(client)
    r = create_team(client, "  Scuderia   Rossa ")
    assert r.status_code == 201
    assert r.json()["name"] == "Scuderia Rossa"
    teams = client.get("/api/teams").json()
    assert [t["name"] for t in teams] == ["Scuderia Rossa"]


def test_create_team_rejects_invalid_names(client):
    register(client)
    assert create_team(client, "a").status_code == 422
    assert create_team(client, "   ").status_code == 422
    assert create_team(client, "x" * 41).status_code == 422


def test_team_name_is_unique_ignoring_case_across_users(make_client):
    first, second = make_client(), make_client()
    register(first, "mario")
    register(second, "luigi")
    assert create_team(first, "Écurie Bleue").status_code == 201
    assert create_team(second, "ÉCURIE  bleue").status_code == 409
    assert create_team(second, "écurie bleue").status_code == 409


def test_teams_list_only_shows_own_teams(make_client):
    first, second = make_client(), make_client()
    register(first, "mario")
    register(second, "luigi")
    create_team(first, "Team Mario")
    create_team(second, "Team Luigi")
    assert [t["name"] for t in first.get("/api/teams").json()] == ["Team Mario"]
    assert [t["name"] for t in second.get("/api/teams").json()] == ["Team Luigi"]


def test_other_users_team_looks_non_existent(make_client):
    first, second = make_client(), make_client()
    register(first, "mario")
    register(second, "luigi")
    team_id = create_team(first).json()["id"]
    assert second.patch(f"/api/teams/{team_id}", json={"name": "Rubato"}).status_code == 404
    assert second.delete(f"/api/teams/{team_id}").status_code == 404
    assert first.get("/api/teams").json()[0]["name"] == "Scuderia Rossa"


def test_unknown_team_returns_404(client):
    register(client)
    assert client.patch("/api/teams/999", json={"name": "Nulla"}).status_code == 404
    assert client.delete("/api/teams/999").status_code == 404


def test_rename_team_and_change_only_case(client):
    register(client)
    team_id = create_team(client, "scuderia rossa").json()["id"]
    r = client.patch(f"/api/teams/{team_id}", json={"name": "Scuderia Rossa"})
    assert r.status_code == 200
    assert r.json()["name"] == "Scuderia Rossa"
    r = client.patch(f"/api/teams/{team_id}", json={"name": "Scuderia Blu"})
    assert r.json()["name"] == "Scuderia Blu"


def test_rename_to_name_of_another_team_is_rejected(client):
    register(client)
    create_team(client, "Team A")
    team_b = create_team(client, "Team B").json()["id"]
    assert client.patch(f"/api/teams/{team_b}", json={"name": "team a"}).status_code == 409


def test_delete_team_hides_it_but_keeps_the_name_taken(client, session_factory):
    register(client)
    team_id = create_team(client).json()["id"]
    assert client.delete(f"/api/teams/{team_id}").status_code == 204
    assert client.get("/api/teams").json() == []
    assert client.delete(f"/api/teams/{team_id}").status_code == 404
    assert create_team(client).status_code == 409
    with session_factory() as db:
        team = db.get(Team, team_id)
        assert team is not None
        assert team.deleted_at is not None


def test_delete_team_hides_its_pilots(client, session_factory):
    user_id = register(client)
    team_id = create_team(client).json()["id"]
    pilot_id = add_pilot(session_factory, user_id, team_id)
    assert pilot_deleted_at(session_factory, pilot_id) is None
    assert client.delete(f"/api/teams/{team_id}").status_code == 204
    assert pilot_deleted_at(session_factory, pilot_id) is not None


def test_delete_team_blocked_by_pilot_in_active_championship(client, session_factory):
    user_id = register(client)
    team_id = create_team(client).json()["id"]
    pilot_id = add_pilot(session_factory, user_id, team_id)
    enroll(session_factory, pilot_id, closed=False)
    assert client.delete(f"/api/teams/{team_id}").status_code == 409
    assert len(client.get("/api/teams").json()) == 1
    assert pilot_deleted_at(session_factory, pilot_id) is None


def test_delete_team_allowed_when_championship_is_closed(client, session_factory):
    user_id = register(client)
    team_id = create_team(client).json()["id"]
    pilot_id = add_pilot(session_factory, user_id, team_id)
    enroll(session_factory, pilot_id, closed=True)
    assert client.delete(f"/api/teams/{team_id}").status_code == 204
    assert pilot_deleted_at(session_factory, pilot_id) is not None