from datetime import datetime, timedelta, timezone

from app.db.models import User
from app.db.models.deck import DeckPrototype
from app.db.models.race import Race
from app.security import hash_password
from app.services.cards import CardEntry, dump_cards

PASSWORD = "password123"


def setup_world(make_client, session_factory):
    with session_factory() as db:
        db.add(
            DeckPrototype(
                name="default",
                base_cards=dump_cards([CardEntry(name="Turbo", path="cards/base/turbo.webp", copies=1)]),
            )
        )
        db.add(User(username="capo", password=hash_password(PASSWORD), role="admin"))
        db.commit()
    admin = make_client()
    assert (
        admin.post("/api/auth/login", json={"username": "capo", "password": PASSWORD}).status_code
        == 200
    )
    player = make_client()
    assert (
        player.post(
            "/api/auth/register", json={"username": "mario", "password": PASSWORD}
        ).status_code
        == 201
    )
    return admin, player


def make_judge(make_client, session_factory, username):
    with session_factory() as db:
        db.add(User(username=username, password=hash_password(PASSWORD), role="judge"))
        db.commit()
    judge = make_client()
    login = judge.post("/api/auth/login", json={"username": username, "password": PASSWORD})
    assert login.status_code == 200
    return judge


def enrolled_pilot(player, championship_id, name):
    team_id = player.post("/api/teams", json={"name": f"Team {name}"}).json()["id"]
    pilot_id = player.post("/api/pilots", json={"name": name, "team_id": team_id}).json()["id"]
    r = player.post(f"/api/championships/{championship_id}/pilots", json={"pilot_id": pilot_id})
    assert r.status_code == 201
    return pilot_id


def scenario(make_client, session_factory):
    # Campionato con una gara in corso, un pilota iscritto e due giudici.
    admin, player = setup_world(make_client, session_factory)
    championship_id = admin.post("/api/championships", json={"name": "Estate"}).json()["id"]
    pilot_id = enrolled_pilot(player, championship_id, "Ayrton")
    race_id = admin.post(f"/api/championships/{championship_id}/races").json()["id"]
    judge1 = make_judge(make_client, session_factory, "giudice1")
    judge2 = make_judge(make_client, session_factory, "giudice2")
    return admin, player, judge1, judge2, championship_id, race_id, pilot_id


def review_url(championship_id, race_id):
    return f"/api/championships/{championship_id}/races/{race_id}/review"


def results_url(championship_id, race_id):
    return f"/api/championships/{championship_id}/races/{race_id}/results"


def test_judge_opens_the_review_and_the_race_shows_who_is_reviewing(make_client, session_factory):
    _, _, judge1, _, cid, rid, _ = scenario(make_client, session_factory)
    r = judge1.put(review_url(cid, rid))
    assert r.status_code == 200
    assert r.json()["reviewer"] == "giudice1"
    detail = judge1.get(f"/api/championships/{cid}/races/{rid}").json()
    assert detail["reviewer"] == "giudice1"


def test_another_judge_cannot_open_the_review(make_client, session_factory):
    _, _, judge1, judge2, cid, rid, _ = scenario(make_client, session_factory)
    assert judge1.put(review_url(cid, rid)).status_code == 200
    r = judge2.put(review_url(cid, rid))
    assert r.status_code == 409
    assert r.json()["detail"] == "Il giudice giudice1 sta chiudendo la gara"


def test_the_holder_can_renew_the_review(make_client, session_factory):
    _, _, judge1, _, cid, rid, _ = scenario(make_client, session_factory)
    assert judge1.put(review_url(cid, rid)).status_code == 200
    assert judge1.put(review_url(cid, rid)).status_code == 200


def test_a_player_cannot_open_the_review(make_client, session_factory):
    _, player, _, _, cid, rid, _ = scenario(make_client, session_factory)
    assert player.put(review_url(cid, rid)).status_code == 403


def test_another_judge_cannot_save_results_while_locked(make_client, session_factory):
    _, _, judge1, judge2, cid, rid, pilot_id = scenario(make_client, session_factory)
    body = {"results": [{"pilot_id": pilot_id, "sponsor_points": 0}]}
    assert judge1.put(review_url(cid, rid)).status_code == 200
    blocked = judge2.put(results_url(cid, rid), json=body)
    assert blocked.status_code == 409
    assert "giudice1" in blocked.json()["detail"]
    done = judge1.put(results_url(cid, rid), json=body)
    assert done.status_code == 200
    assert done.json()["reviewer"] is None


def test_an_expired_lock_can_be_taken_by_another_judge(make_client, session_factory):
    _, _, judge1, judge2, cid, rid, _ = scenario(make_client, session_factory)
    assert judge1.put(review_url(cid, rid)).status_code == 200
    old = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(minutes=31)
    with session_factory() as db:
        db.get(Race, rid).review_started_at = old
        db.commit()
    r = judge2.put(review_url(cid, rid))
    assert r.status_code == 200
    assert r.json()["reviewer"] == "giudice2"


def test_only_the_holder_or_the_admin_can_release(make_client, session_factory):
    admin, _, judge1, judge2, cid, rid, _ = scenario(make_client, session_factory)
    assert judge1.put(review_url(cid, rid)).status_code == 200
    assert judge2.delete(review_url(cid, rid)).status_code == 403
    assert admin.delete(review_url(cid, rid)).json()["reviewer"] is None
    assert judge2.put(review_url(cid, rid)).status_code == 200
    released = judge2.delete(review_url(cid, rid))
    assert released.status_code == 200
    assert released.json()["reviewer"] is None


def test_a_race_in_review_still_blocks_a_new_race(make_client, session_factory):
    admin, _, judge1, _, cid, rid, _ = scenario(make_client, session_factory)
    assert judge1.put(review_url(cid, rid)).status_code == 200
    assert admin.post(f"/api/championships/{cid}/races").status_code == 409


def test_cannot_open_the_review_of_a_finished_race(make_client, session_factory):
    admin, _, judge1, _, cid, rid, pilot_id = scenario(make_client, session_factory)
    body = {"results": [{"pilot_id": pilot_id, "sponsor_points": 0}]}
    assert admin.put(results_url(cid, rid), json=body).status_code == 200
    assert judge1.put(review_url(cid, rid)).status_code == 409
