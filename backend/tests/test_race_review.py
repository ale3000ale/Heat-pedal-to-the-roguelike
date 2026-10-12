from app.db.models import User
from app.db.models.card_play import CardPlay
from app.db.models.championship import Championship
from app.db.models.deck import Deck, DeckPrototype
from app.db.models.pilot import Pilot
from app.security import hash_password
from app.services.cards import CardEntry, dump_cards, parse_cards

PASSWORD = "password123"
CARD = "Turbo Sponsor"


def setup_world(make_client, session_factory):
    with session_factory() as db:
        db.add(
            DeckPrototype(
                name="default",
                base_cards=dump_cards([CardEntry(name="Turbo", path="cards/base/turbo.webp", copies=1)]),
            )
        )
        db.commit()
    admin = make_client()
    with session_factory() as db:
        db.add(User(username="capo", password=hash_password(PASSWORD), role="admin"))
        db.commit()
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


def judge_client(make_client, session_factory, username="giudice"):
    with session_factory() as db:
        db.add(User(username=username, password=hash_password(PASSWORD), role="judge"))
        db.commit()
    judge = make_client()
    assert (
        judge.post("/api/auth/login", json={"username": username, "password": PASSWORD}).status_code
        == 200
    )
    return judge


def enrolled_pilot(player, championship_id, name="Ayrton"):
    team_id = player.post("/api/teams", json={"name": f"Team {name}"}).json()["id"]
    pilot_id = player.post("/api/pilots", json={"name": name, "team_id": team_id}).json()["id"]
    r = player.post(f"/api/championships/{championship_id}/pilots", json={"pilot_id": pilot_id})
    assert r.status_code == 201
    return pilot_id


def give_sponsor_cards(session_factory, pilot_id, copies):
    with session_factory() as db:
        pilot = db.get(Pilot, pilot_id)
        cards = [CardEntry(name=CARD, path="cards/sponsor/turbo.webp", copies=copies)]
        db.get(Deck, pilot.sponsor_inventory_deck_id).cards = dump_cards(cards)
        db.commit()


def give_sponsor_pool(session_factory, championship_id, copies):
    with session_factory() as db:
        deck = Deck(cards=dump_cards([CardEntry(name=CARD, path="cards/sponsor/turbo.webp", copies=copies)]))
        db.add(deck)
        db.flush()
        db.get(Championship, championship_id).sponsor_pool_deck_id = deck.id
        db.commit()


def remove_sponsor_pool(session_factory, championship_id):
    with session_factory() as db:
        db.get(Championship, championship_id).sponsor_pool_deck_id = None
        db.commit()


def sponsor_inventory(session_factory, pilot_id):
    with session_factory() as db:
        pilot = db.get(Pilot, pilot_id)
        return {c.name: c.copies for c in parse_cards(db.get(Deck, pilot.sponsor_inventory_deck_id).cards)}


def sponsor_pool(session_factory, championship_id):
    with session_factory() as db:
        deck_id = db.get(Championship, championship_id).sponsor_pool_deck_id
        return {c.name: c.copies for c in parse_cards(db.get(Deck, deck_id).cards)}


def play_statuses(session_factory):
    with session_factory() as db:
        return [p.status for p in db.query(CardPlay).order_by(CardPlay.id)]


def start_race(admin, championship_id):
    r = admin.post(f"/api/championships/{championship_id}/races")
    assert r.status_code == 201
    return r.json()["id"]


def finish_race(admin, championship_id, race_id, pilot_id):
    r = admin.put(
        f"/api/championships/{championship_id}/races/{race_id}/results",
        json={"results": [{"pilot_id": pilot_id, "sponsor_points": 0}]},
    )
    assert r.status_code == 200


def play(player, championship_id, pilot_id):
    return player.post(
        f"/api/championships/{championship_id}/card-plays",
        json={"pilot_id": pilot_id, "card_name": CARD},
    )


def undo(player, championship_id, pilot_id):
    return player.post(
        f"/api/championships/{championship_id}/card-plays/undo", json={"pilot_id": pilot_id}
    )


def card_state(player, championship_id, pilot_id):
    return player.get(
        f"/api/championships/{championship_id}/card-plays", params={"pilot_id": pilot_id}
    )


def open_review(client, championship_id, race_id):
    return client.post(f"/api/championships/{championship_id}/races/{race_id}/review")


def leave_review(client, championship_id, race_id):
    return client.delete(f"/api/championships/{championship_id}/races/{race_id}/review")


def confirm_review(client, championship_id, race_id):
    return client.post(f"/api/championships/{championship_id}/races/{race_id}/review/confirm")


def scenario(make_client, session_factory, copies=3, pool_copies=1):
    admin, player = setup_world(make_client, session_factory)
    championship_id = admin.post("/api/championships", json={"name": "Estate"}).json()["id"]
    pilot_id = enrolled_pilot(player, championship_id)
    give_sponsor_cards(session_factory, pilot_id, copies)
    give_sponsor_pool(session_factory, championship_id, pool_copies)
    race_id = start_race(admin, championship_id)
    return admin, player, championship_id, pilot_id, race_id


def closed_scenario(make_client, session_factory, copies=3, pool_copies=1, plays=0):
    # Come scenario, ma con le giocate fatte e la gara chiusa con i risultati.
    admin, player, champ, pilot, race = scenario(make_client, session_factory, copies, pool_copies)
    for _ in range(plays):
        assert play(player, champ, pilot).status_code == 201
    finish_race(admin, champ, race, pilot)
    return admin, player, champ, pilot, race


def test_admin_opens_the_review_after_the_results(make_client, session_factory):
    admin, _, champ, _, race = closed_scenario(make_client, session_factory)
    r = open_review(admin, champ, race)
    assert r.status_code == 200
    body = r.json()
    assert body["race_id"] == race
    assert body["in_review"] is True
    assert body["review_started_at"] is not None
    assert body["reviewer_user_id"] is not None
    assert body["review_expires_at"] is not None
    assert body["review_closed_at"] is None


def test_judge_can_open_and_leave_the_review(make_client, session_factory):
    _, _, champ, _, race = closed_scenario(make_client, session_factory)
    judge = judge_client(make_client, session_factory)
    assert open_review(judge, champ, race).json()["in_review"] is True
    left = leave_review(judge, champ, race)
    assert left.status_code == 200
    assert left.json()["in_review"] is False
    assert left.json()["reviewer_user_id"] is None


def test_a_player_cannot_open_leave_or_confirm_the_review(make_client, session_factory):
    _, player, champ, _, race = closed_scenario(make_client, session_factory)
    assert open_review(player, champ, race).status_code == 403
    assert leave_review(player, champ, race).status_code == 403
    assert confirm_review(player, champ, race).status_code == 403


def test_opening_the_review_twice_keeps_the_first_date(make_client, session_factory):
    admin, _, champ, _, race = closed_scenario(make_client, session_factory)
    first = open_review(admin, champ, race).json()
    second = open_review(admin, champ, race).json()
    assert second["in_review"] is True
    assert second["review_started_at"] == first["review_started_at"]


def test_a_second_reviewer_is_refused_while_the_review_is_active(make_client, session_factory):
    admin, _, champ, _, race = closed_scenario(make_client, session_factory)
    judge = judge_client(make_client, session_factory)
    assert open_review(judge, champ, race).status_code == 200
    assert open_review(admin, champ, race).status_code == 409
    assert leave_review(admin, champ, race).status_code == 409
    assert confirm_review(admin, champ, race).status_code == 409
    assert open_review(judge, champ, race).status_code == 200


def test_leaving_a_review_that_is_not_open_is_refused(make_client, session_factory):
    admin, _, champ, _, race = closed_scenario(make_client, session_factory)
    assert leave_review(admin, champ, race).status_code == 409


def test_review_is_refused_before_the_results(make_client, session_factory):
    admin, _, champ, _, race = scenario(make_client, session_factory)
    assert open_review(admin, champ, race).status_code == 409
    assert leave_review(admin, champ, race).status_code == 409
    assert confirm_review(admin, champ, race).status_code == 409


def test_players_cannot_play_or_undo_during_the_review(make_client, session_factory):
    admin, player, champ, pilot, race = closed_scenario(make_client, session_factory, copies=2, plays=1)
    assert open_review(admin, champ, race).status_code == 200
    assert play(player, champ, pilot).status_code == 409
    assert undo(player, champ, pilot).status_code == 409
    assert play_statuses(session_factory) == ["giocata"]


def test_state_can_still_be_read_during_the_review(make_client, session_factory):
    admin, player, champ, pilot, race = closed_scenario(make_client, session_factory)
    assert open_review(admin, champ, race).status_code == 200
    state = card_state(player, champ, pilot)
    assert state.status_code == 200
    assert state.json()["in_review"] is True


def test_leaving_the_review_keeps_the_plays_unchanged(make_client, session_factory):
    admin, player, champ, pilot, race = closed_scenario(make_client, session_factory, copies=2, plays=1)
    assert open_review(admin, champ, race).status_code == 200
    assert leave_review(admin, champ, race).status_code == 200
    state = card_state(player, champ, pilot).json()
    assert state["in_review"] is False
    assert len(state["plays"]) == 1
    assert play_statuses(session_factory) == ["giocata"]


def test_review_with_unknown_race_or_championship(make_client, session_factory):
    admin, _, champ, _, _ = scenario(make_client, session_factory)
    assert open_review(admin, champ, 9999).status_code == 404
    assert open_review(admin, 9999, 1).status_code == 404


def test_the_reviewer_confirms_and_the_plays_are_consumed(make_client, session_factory):
    admin, _, champ, pilot, race = closed_scenario(make_client, session_factory, copies=3, plays=2)
    assert sponsor_inventory(session_factory, pilot) == {CARD: 3}
    assert open_review(admin, champ, race).status_code == 200
    r = confirm_review(admin, champ, race)
    assert r.status_code == 200
    assert r.json()["in_review"] is False
    assert r.json()["review_closed_at"] is not None
    assert sponsor_inventory(session_factory, pilot) == {CARD: 1}
    assert sponsor_pool(session_factory, champ) == {CARD: 3}
    assert play_statuses(session_factory) == ["consumata", "consumata"]


def test_confirming_twice_does_not_consume_the_cards_twice(make_client, session_factory):
    admin, _, champ, pilot, race = closed_scenario(make_client, session_factory, copies=3, plays=2)
    assert open_review(admin, champ, race).status_code == 200
    assert confirm_review(admin, champ, race).status_code == 200
    assert confirm_review(admin, champ, race).status_code == 409
    assert open_review(admin, champ, race).status_code == 409
    assert sponsor_inventory(session_factory, pilot) == {CARD: 1}
    assert sponsor_pool(session_factory, champ) == {CARD: 3}


def test_admin_confirms_without_opening_the_review(make_client, session_factory):
    admin, _, champ, pilot, race = closed_scenario(make_client, session_factory, copies=3, plays=2)
    assert confirm_review(admin, champ, race).status_code == 200
    assert sponsor_inventory(session_factory, pilot) == {CARD: 1}
    assert play_statuses(session_factory) == ["consumata", "consumata"]


def test_a_judge_cannot_confirm_without_an_active_review(make_client, session_factory):
    _, _, champ, pilot, race = closed_scenario(make_client, session_factory, copies=3, plays=2)
    judge = judge_client(make_client, session_factory)
    assert confirm_review(judge, champ, race).status_code == 409
    assert sponsor_inventory(session_factory, pilot) == {CARD: 3}


def test_a_judge_confirms_his_own_review(make_client, session_factory):
    _, _, champ, pilot, race = closed_scenario(make_client, session_factory, copies=3, plays=2)
    judge = judge_client(make_client, session_factory)
    assert open_review(judge, champ, race).status_code == 200
    assert confirm_review(judge, champ, race).status_code == 200
    assert sponsor_inventory(session_factory, pilot) == {CARD: 1}


def test_without_a_sponsor_pool_the_cards_leave_the_inventory_anyway(make_client, session_factory):
    admin, _, champ, pilot, race = closed_scenario(make_client, session_factory, copies=3, plays=2)
    remove_sponsor_pool(session_factory, champ)
    assert open_review(admin, champ, race).status_code == 200
    assert confirm_review(admin, champ, race).status_code == 200
    assert sponsor_inventory(session_factory, pilot) == {CARD: 1}
    assert play_statuses(session_factory) == ["consumata", "consumata"]
