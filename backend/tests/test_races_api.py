from app.db.models import User
from app.db.models.deck import DeckPrototype
from app.security import hash_password
from app.services.cards import CardEntry, dump_cards
from app.db.models.championship import ChampionshipStanding

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


def setup(make_client, session_factory, names):
    # Un campionato attivo con i piloti indicati, tutti iscritti.
    admin = make_admin(make_client, session_factory)
    player = make_player(make_client)
    championship_id = admin.post("/api/championships", json={"name": "Estate"}).json()["id"]
    pilots = {}
    for name in names:
        team_id = player.post("/api/teams", json={"name": f"Team {name}"}).json()["id"]
        pilot_id = player.post("/api/pilots", json={"name": name, "team_id": team_id}).json()["id"]
        r = player.post(f"/api/championships/{championship_id}/pilots", json={"pilot_id": pilot_id})
        assert r.status_code == 201
        pilots[name] = pilot_id
    return admin, player, championship_id, pilots


def new_race(admin, championship_id):
    r = admin.post(f"/api/championships/{championship_id}/races")
    assert r.status_code == 201
    return r.json()["id"]


def put_results(admin, championship_id, race_id, pilot_ids):
    return admin.put(
        f"/api/championships/{championship_id}/races/{race_id}/results",
        json={"pilot_ids": pilot_ids},
    )


def test_race_actions_are_admin_only(make_client, session_factory):
    admin, player, cid, pilots = setup(make_client, session_factory, ["Anna"])
    race_id = new_race(admin, cid)
    assert make_client().post(f"/api/championships/{cid}/races").status_code == 401
    assert player.post(f"/api/championships/{cid}/races").status_code == 403
    assert put_results(player, cid, race_id, [pilots["Anna"]]).status_code == 403
    assert player.get(f"/api/championships/{cid}/races").status_code == 200
    assert player.get(f"/api/championships/{cid}/standings").status_code == 200


def test_races_are_numbered_and_unknown_ids_are_404(make_client, session_factory):
    admin, player, cid, pilots = setup(make_client, session_factory, ["Anna"])
    new_race(admin, cid)
    new_race(admin, cid)
    races = player.get(f"/api/championships/{cid}/races").json()
    assert [r["number"] for r in races] == [1, 2]
    assert admin.post("/api/championships/999/races").status_code == 404
    assert player.get("/api/championships/999/races").status_code == 404
    assert player.get(f"/api/championships/{cid}/races/999").status_code == 404
    assert player.get("/api/championships/999/standings").status_code == 404


def test_points_follow_the_position_table(make_client, session_factory):
    names = [f"Pilota {n}" for n in range(1, 8)]
    admin, player, cid, pilots = setup(make_client, session_factory, names)
    race_id = new_race(admin, cid)
    r = put_results(admin, cid, race_id, [pilots[n] for n in names])
    assert r.status_code == 200
    assert [x["position"] for x in r.json()["results"]] == [1, 2, 3, 4, 5, 6, 7]
    assert [x["points"] for x in r.json()["results"]] == [9, 6, 4, 3, 2, 1, 0]
    assert r.json()["participants"] == 7


def test_absent_pilots_appear_with_zero_points(make_client, session_factory):
    admin, player, cid, pilots = setup(make_client, session_factory, ["Anna", "Beppe", "Carlo"])
    race_id = new_race(admin, cid)
    r = put_results(admin, cid, race_id, [pilots["Beppe"], pilots["Anna"]])
    assert r.json()["participants"] == 2
    assert [(x["pilot_name"], x["position"], x["points"]) for x in r.json()["results"]] == [
        ("Beppe", 1, 9),
        ("Anna", 2, 6),
        ("Carlo", None, 0),
    ]
    assert player.get(f"/api/pilots/{pilots['Beppe']}").json()["point"] == 9
    assert player.get(f"/api/pilots/{pilots['Anna']}").json()["point"] == 6
    assert player.get(f"/api/pilots/{pilots['Carlo']}").json()["point"] == 0


def test_invalid_results_are_rejected(make_client, session_factory):
    admin, player, cid, pilots = setup(make_client, session_factory, ["Anna", "Beppe"])
    team_id = player.post("/api/teams", json={"name": "Team Fuori"}).json()["id"]
    outsider = player.post("/api/pilots", json={"name": "Fuori", "team_id": team_id}).json()["id"]
    race_id = new_race(admin, cid)
    anna = pilots["Anna"]
    assert put_results(admin, cid, race_id, []).status_code == 422
    assert put_results(admin, cid, race_id, [anna, anna]).status_code == 422
    assert put_results(admin, cid, race_id, [anna, outsider]).status_code == 422
    assert put_results(admin, cid, race_id, list(range(1, 14))).status_code == 422
    assert put_results(admin, cid, 999, [anna]).status_code == 404
    assert admin.get(f"/api/championships/{cid}/races/{race_id}").json()["participants"] == 0


def test_results_can_be_corrected(make_client, session_factory):
    admin, player, cid, pilots = setup(make_client, session_factory, ["Anna", "Beppe"])
    race_id = new_race(admin, cid)
    put_results(admin, cid, race_id, [pilots["Anna"], pilots["Beppe"]])
    r = put_results(admin, cid, race_id, [pilots["Beppe"]])
    assert r.status_code == 200
    assert [(x["pilot_name"], x["position"], x["points"]) for x in r.json()["results"]] == [
        ("Beppe", 1, 9),
        ("Anna", None, 0),
    ]
    assert player.get(f"/api/pilots/{pilots['Anna']}").json()["point"] == 0
    assert player.get(f"/api/pilots/{pilots['Beppe']}").json()["point"] == 9


def test_standings_sum_points_and_share_rank_on_ties(make_client, session_factory):
    admin, player, cid, pilots = setup(make_client, session_factory, ["Anna", "Beppe", "Carlo"])
    first = new_race(admin, cid)
    second = new_race(admin, cid)
    put_results(admin, cid, first, [pilots["Anna"], pilots["Beppe"]])
    put_results(admin, cid, second, [pilots["Beppe"], pilots["Anna"], pilots["Carlo"]])
    table = player.get(f"/api/championships/{cid}/standings").json()
    assert [(x["rank"], x["pilot_name"], x["points"], x["races_played"]) for x in table] == [
        (1, "Anna", 15, 2),
        (1, "Beppe", 15, 2),
        (3, "Carlo", 4, 1),
    ]


def test_standings_include_pilots_without_races(make_client, session_factory):
    admin, player, cid, pilots = setup(make_client, session_factory, ["Anna", "Beppe"])
    table = player.get(f"/api/championships/{cid}/standings").json()
    assert [(x["rank"], x["points"], x["races_played"]) for x in table] == [(1, 0, 0), (1, 0, 0)]


def test_closed_championship_is_read_only(make_client, session_factory):
    admin, player, cid, pilots = setup(make_client, session_factory, ["Anna"])
    race_id = new_race(admin, cid)
    put_results(admin, cid, race_id, [pilots["Anna"]])
    admin.post(f"/api/championships/{cid}/close")
    assert admin.post(f"/api/championships/{cid}/races").status_code == 409
    assert put_results(admin, cid, race_id, [pilots["Anna"]]).status_code == 409
    assert player.get(f"/api/championships/{cid}/races/{race_id}").status_code == 200
    assert player.get(f"/api/championships/{cid}/standings").json()[0]["points"] == 9


def test_race_of_another_championship_is_404(make_client, session_factory):
    admin, player, cid, pilots = setup(make_client, session_factory, ["Anna"])
    other = admin.post("/api/championships", json={"name": "Inverno"}).json()["id"]
    foreign_race = new_race(admin, other)
    assert player.get(f"/api/championships/{cid}/races/{foreign_race}").status_code == 404
    assert put_results(admin, cid, foreign_race, [pilots["Anna"]]).status_code == 404


def test_closing_freezes_standings_with_names_only(make_client, session_factory):
    admin, player, cid, pilots = setup(make_client, session_factory, ["Anna", "Beppe", "Carlo"])
    race_id = new_race(admin, cid)
    put_results(admin, cid, race_id, [pilots["Beppe"], pilots["Anna"]])
    live = player.get(f"/api/championships/{cid}/standings").json()
    assert all(x["pilot_id"] is not None for x in live)
    admin.post(f"/api/championships/{cid}/close")
    frozen = player.get(f"/api/championships/{cid}/standings").json()
    assert [
        (x["rank"], x["pilot_name"], x["points"], x["races_played"], x["pilot_id"]) for x in frozen
    ] == [
        (1, "Beppe", 9, 1, None),
        (2, "Anna", 6, 1, None),
        (3, "Carlo", 0, 0, None),
    ]
    with session_factory() as db:
        assert db.query(ChampionshipStanding).count() == 3


def test_frozen_standings_survive_pilot_purge(make_client, session_factory):
    admin, player, cid, pilots = setup(make_client, session_factory, ["Anna", "Beppe"])
    race_id = new_race(admin, cid)
    put_results(admin, cid, race_id, [pilots["Anna"], pilots["Beppe"]])
    admin.post(f"/api/championships/{cid}/close")
    assert player.delete(f"/api/pilots/{pilots['Anna']}").status_code < 300
    assert admin.delete(f"/api/admin/deleted/pilots/{pilots['Anna']}").status_code == 204
    table = player.get(f"/api/championships/{cid}/standings").json()
    assert [(x["rank"], x["pilot_name"], x["points"]) for x in table] == [
        (1, "Anna", 9),
        (2, "Beppe", 6),
    ]


def test_deleting_championship_removes_frozen_standings(make_client, session_factory):
    admin, player, cid, pilots = setup(make_client, session_factory, ["Anna"])
    admin.post(f"/api/championships/{cid}/close")
    with session_factory() as db:
        assert db.query(ChampionshipStanding).count() == 1
    assert admin.delete(f"/api/championships/{cid}").status_code == 204
    with session_factory() as db:
        assert db.query(ChampionshipStanding).count() == 0


def test_closed_championship_without_frozen_rows_falls_back_to_live(make_client, session_factory):
    admin, player, cid, pilots = setup(make_client, session_factory, ["Anna"])
    race_id = new_race(admin, cid)
    put_results(admin, cid, race_id, [pilots["Anna"]])
    admin.post(f"/api/championships/{cid}/close")
    with session_factory() as db:
        db.query(ChampionshipStanding).delete()
        db.commit()
    table = player.get(f"/api/championships/{cid}/standings").json()
    assert [(x["pilot_name"], x["points"]) for x in table] == [("Anna", 9)]
    assert table[0]["pilot_id"] == pilots["Anna"]