from app.db.models.championship import Championship, ChampionshipPilot

PASSWORD = "password123"


def register(client, username="mario"):
    # Crea un utente (che resta loggato nel client).
    r = client.post("/api/auth/register", json={"username": username, "password": PASSWORD})
    assert r.status_code == 201
    return r.json()["id"]


def create_team(client, name="Scuderia Rossa"):
    return client.post("/api/teams", json={"name": name}).json()["id"]


def create_pilot(client, name="Ayrton", team_id=None):
    return client.post("/api/pilots", json={"name": name, "team_id": team_id})


def enroll(session_factory, pilot_id, closed=False):
    # Iscrive il pilota a un nuovo campionato, aperto o chiuso.
    with session_factory() as db:
        championship = Championship(name=f"Campionato {pilot_id}", is_closed=closed)
        db.add(championship)
        db.flush()
        db.add(ChampionshipPilot(championship_id=championship.id, pilot_id=pilot_id))
        db.commit()


def test_pilots_require_login(client):
    assert client.get("/api/pilots").status_code == 401
    assert create_pilot(client).status_code == 401
    assert client.get("/api/pilots/1").status_code == 401
    assert client.patch("/api/pilots/1", json={"name": "Altro"}).status_code == 401
    assert client.put("/api/pilots/1/team", json={"team_id": None}).status_code == 401
    assert client.delete("/api/pilots/1").status_code == 401


def test_create_pilot_returns_detail_with_starter_inventory(client):
    register(client)
    r = create_pilot(client, "  Ayrton   Rossi ")
    assert r.status_code == 201
    body = r.json()
    assert body["name"] == "Ayrton Rossi"
    assert body["team_id"] is None
    assert (body["gold"], body["sponsor"], body["point"]) == (0, 0, 0)
    assert [c["name"] for c in body["inventory"]] == [f"Velocità {n}" for n in range(1, 5)]
    assert all(c["copies"] == 3 for c in body["inventory"])
    assert all(c["path"].startswith("cards/starter/") for c in body["inventory"])
    assert body["game_deck"] == []


def test_create_pilot_rejects_invalid_names(client):
    register(client)
    assert create_pilot(client, "a").status_code == 422
    assert create_pilot(client, "   ").status_code == 422
    assert create_pilot(client, "x" * 41).status_code == 422


def test_create_pilot_with_own_team(client):
    register(client)
    team_id = create_team(client)
    r = create_pilot(client, "Ayrton", team_id)
    assert r.status_code == 201
    assert r.json()["team_id"] == team_id


def test_create_pilot_with_foreign_or_unknown_team_is_404(make_client):
    first, second = make_client(), make_client()
    register(first, "mario")
    register(second, "luigi")
    foreign = create_team(first)
    assert create_pilot(second, "Ayrton", foreign).status_code == 404
    assert create_pilot(second, "Ayrton", 999).status_code == 404


def test_pilot_name_is_unique_ignoring_case_across_users(make_client):
    first, second = make_client(), make_client()
    register(first, "mario")
    register(second, "luigi")
    assert create_pilot(first, "Ayrton").status_code == 201
    assert create_pilot(second, "AYRTON").status_code == 409
    assert create_pilot(second, "  ayrton ").status_code == 409


def test_list_shows_only_own_pilots_alphabetically(make_client):
    first, second = make_client(), make_client()
    register(first, "mario")
    register(second, "luigi")
    create_pilot(first, "Zeta")
    create_pilot(first, "alfa")
    create_pilot(second, "Altro")
    assert [p["name"] for p in first.get("/api/pilots").json()] == ["alfa", "Zeta"]
    assert [p["name"] for p in second.get("/api/pilots").json()] == ["Altro"]


def test_detail_of_own_pilot(client):
    register(client)
    pilot_id = create_pilot(client).json()["id"]
    r = client.get(f"/api/pilots/{pilot_id}")
    assert r.status_code == 200
    assert r.json()["name"] == "Ayrton"
    assert len(r.json()["inventory"]) == 4


def test_other_users_pilot_looks_non_existent(make_client):
    first, second = make_client(), make_client()
    register(first, "mario")
    register(second, "luigi")
    pilot_id = create_pilot(first).json()["id"]
    assert second.get(f"/api/pilots/{pilot_id}").status_code == 404
    assert second.patch(f"/api/pilots/{pilot_id}", json={"name": "Rubato"}).status_code == 404
    assert second.put(f"/api/pilots/{pilot_id}/team", json={"team_id": None}).status_code == 404
    assert second.delete(f"/api/pilots/{pilot_id}").status_code == 404
    assert first.get("/api/pilots").json()[0]["name"] == "Ayrton"


def test_unknown_pilot_returns_404(client):
    register(client)
    assert client.get("/api/pilots/999").status_code == 404
    assert client.patch("/api/pilots/999", json={"name": "Nulla"}).status_code == 404
    assert client.put("/api/pilots/999/team", json={"team_id": None}).status_code == 404
    assert client.delete("/api/pilots/999").status_code == 404


def test_rename_pilot(client):
    register(client)
    pilot_id = create_pilot(client, "ayrton").json()["id"]
    r = client.patch(f"/api/pilots/{pilot_id}", json={"name": "Ayrton"})
    assert r.status_code == 200
    assert r.json()["name"] == "Ayrton"
    assert client.patch(f"/api/pilots/{pilot_id}", json={"name": "a"}).status_code == 422


def test_rename_to_taken_name_is_409(client):
    register(client)
    create_pilot(client, "Ayrton")
    other = create_pilot(client, "Niki").json()["id"]
    assert client.patch(f"/api/pilots/{other}", json={"name": "ayrton"}).status_code == 409


def test_change_and_remove_team(client):
    register(client)
    first = create_team(client, "Team A")
    second = create_team(client, "Team B")
    pilot_id = create_pilot(client, "Ayrton", first).json()["id"]
    r = client.put(f"/api/pilots/{pilot_id}/team", json={"team_id": second})
    assert r.status_code == 200
    assert r.json()["team_id"] == second
    r = client.put(f"/api/pilots/{pilot_id}/team", json={"team_id": None})
    assert r.status_code == 200
    assert r.json()["team_id"] is None


def test_change_team_requires_the_field_and_a_own_team(make_client):
    first, second = make_client(), make_client()
    register(first, "mario")
    register(second, "luigi")
    foreign = create_team(second)
    pilot_id = create_pilot(first).json()["id"]
    assert first.put(f"/api/pilots/{pilot_id}/team", json={}).status_code == 422
    assert first.put(f"/api/pilots/{pilot_id}/team", json={"team_id": foreign}).status_code == 404
    assert first.put(f"/api/pilots/{pilot_id}/team", json={"team_id": 999}).status_code == 404


def test_team_is_locked_in_active_championship_and_free_when_closed(client, session_factory):
    register(client)
    team_id = create_team(client)
    active = create_pilot(client, "Attivo", team_id).json()["id"]
    enroll(session_factory, active, closed=False)
    r = client.put(f"/api/pilots/{active}/team", json={"team_id": None})
    assert r.status_code == 409
    assert client.get(f"/api/pilots/{active}").json()["team_id"] == team_id

    finished = create_pilot(client, "Concluso").json()["id"]
    enroll(session_factory, finished, closed=True)
    r = client.put(f"/api/pilots/{finished}/team", json={"team_id": team_id})
    assert r.status_code == 200
    assert r.json()["team_id"] == team_id


def test_delete_pilot_hides_it_but_keeps_the_name_taken(client):
    register(client)
    pilot_id = create_pilot(client).json()["id"]
    assert client.delete(f"/api/pilots/{pilot_id}").status_code == 204
    assert client.get("/api/pilots").json() == []
    assert client.get(f"/api/pilots/{pilot_id}").status_code == 404
    assert client.delete(f"/api/pilots/{pilot_id}").status_code == 404
    assert create_pilot(client).status_code == 409


def test_delete_blocked_in_active_championship(client, session_factory):
    register(client)
    pilot_id = create_pilot(client).json()["id"]
    enroll(session_factory, pilot_id, closed=False)
    assert client.delete(f"/api/pilots/{pilot_id}").status_code == 409
    assert len(client.get("/api/pilots").json()) == 1


def test_deleting_a_team_hides_its_pilots(client):
    register(client)
    team_id = create_team(client)
    create_pilot(client, "Dentro", team_id)
    create_pilot(client, "Fuori")
    assert client.delete(f"/api/teams/{team_id}").status_code == 204
    assert [p["name"] for p in client.get("/api/pilots").json()] == ["Fuori"]