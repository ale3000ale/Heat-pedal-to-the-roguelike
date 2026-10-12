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


def judge_client(make_client, session_factory):
    with session_factory() as db:
        db.add(User(username="giudice", password=hash_password(PASSWORD), role="judge"))
        db.commit()
    judge = make_client()
    assert (
        judge.post("/api/auth/login", json={"username": "giudice", "password": PASSWORD}).status_code
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


def scenario(make_client, session_factory, copies=3, pool_copies=1):
    admin, player = setup_world(make_client, session_factory)
    championship_id = admin.post("/api/championships", json={"name": "Estate"}).json()["id"]
    pilot_id = enrolled_pilot(player, championship_id)
    give_sponsor_cards(session_factory, pilot_id, copies)
    give_sponsor_pool(session_factory, championship_id, pool_copies)
    race_id = start_race(admin, championship_id)
    return admin, player, championship_id, pilot_id, race_id


def test_admin_opens_the_review(make_client, session_factory):
    admin, _, champ, _, race = scenario(make_client, session_factory)
    r = open_review(admin, champ, race)
    assert r.status_code == 200
    body = r.json()
    assert body["race_id"] == race
    assert body["in_review"] is True
    assert body["review_started_at"] is not None


def test_judge_can_open_and_leave_the_review(make_client, session_factory):
    _, _, champ, _, race = scenario(make_client, session_factory)
    judge = judge_client(make_client, session_factory)
    assert open_review(judge, champ, race).json()["in_review"] is True
    assert leave_review(judge, champ, race).json()["in_review"] is False


def test_a_player_cannot_open_or_leave_the_review(make_client, session_factory):
    _, player, champ, _, race = scenario(make_client, session_factory)
    assert open_review(player, champ, race).status_code == 403
    assert leave_review(player, champ, race).status_code == 403


def test_opening_the_review_twice_keeps_the_first_date(make_client, session_factory):
    admin, _, champ, _, race = scenario(make_client, session_factory)
    first = open_review(admin, champ, race).json()
    second = open_review(admin, champ, race).json()
    assert second["in_review"] is True
    assert second["review_started_at"] == first["review_started_at"]


def test_leaving_a_race_that_is_not_in_review_changes_nothing(make_client, session_factory):
    admin, _, champ, _, race = scenario(make_client, session_factory)
    r = leave_review(admin, champ, race)
    assert r.status_code == 200
    assert r.json()["in_review"] is False


def test_players_cannot_play_or_undo_during_the_review(make_client, session_factory):
    admin, player, champ, pilot, race = scenario(make_client, session_factory, copies=2)
    assert play(player, champ, pilot).status_code == 201
    assert open_review(admin, champ, race).status_code == 200
    assert play(player, champ, pilot).status_code == 409
    assert undo(player, champ, pilot).status_code == 409
    assert play_statuses(session_factory) == ["giocata"]


def test_state_can_still_be_read_during_the_review(make_client, session_factory):
    admin, player, champ, pilot, race = scenario(make_client, session_factory)
    assert card_state(player, champ, pilot).json()["in_review"] is False
    assert open_review(admin, champ, race).status_code == 200
    state = card_state(player, champ, pilot)
    assert state.status_code == 200
    assert state.json()["in_review"] is True


def test_leaving_the_review_gives_back_the_game_with_plays_unchanged(make_client, session_factory):
    admin, player, champ, pilot, race = scenario(make_client, session_factory, copies=2)
    assert play(player, champ, pilot).status_code == 201
    assert open_review(admin, champ, race).status_code == 200
    assert leave_review(admin, champ, race).status_code == 200
    state = card_state(player, champ, pilot).json()
    assert state["in_review"] is False
    assert len(state["plays"]) == 1
    assert play(player, champ, pilot).status_code == 201
    assert undo(player, champ, pilot).status_code == 200


def test_review_is_refused_on_a_closed_race(make_client, session_factory):
    admin, _, champ, pilot, race = scenario(make_client, session_factory)
    finish_race(admin, champ, race, pilot)
    assert open_review(admin, champ, race).status_code == 409
    assert leave_review(admin, champ, race).status_code == 409


def test_review_with_unknown_race_or_championship(make_client, session_factory):
    admin, _, champ, _, _ = scenario(make_client, session_factory)
    assert open_review(admin, champ, 9999).status_code == 404
    assert open_review(admin, 9999, 1).status_code == 404


def test_closing_the_race_from_the_review_consumes_the_plays(make_client, session_factory):
    admin, player, champ, pilot, race = scenario(make_client, session_factory, copies=3, pool_copies=1)
    assert play(player, champ, pilot).status_code == 201
    assert play(player, champ, pilot).status_code == 201
    assert open_review(admin, champ, race).status_code == 200
    finish_race(admin, champ, race, pilot)
    assert sponsor_inventory(session_factory, pilot) == {CARD: 1}
    assert sponsor_pool(session_factory, champ) == {CARD: 3}
    assert play_statuses(session_factory) == ["consumata", "consumata"]


def test_admin_correction_does_not_consume_the_cards_twice(make_client, session_factory):
    admin, player, champ, pilot, race = scenario(make_client, session_factory, copies=3, pool_copies=1)
    assert play(player, champ, pilot).status_code == 201
    assert play(player, champ, pilot).status_code == 201
    finish_race(admin, champ, race, pilot)
    finish_race(admin, champ, race, pilot)
    assert sponsor_inventory(session_factory, pilot) == {CARD: 1}
    assert sponsor_pool(session_factory, champ) == {CARD: 3}
    assert play_statuses(session_factory) == ["consumata", "consumata"]


def test_without_a_sponsor_pool_the_cards_leave_the_inventory_anyway(make_client, session_factory):
    admin, player, champ, pilot, race = scenario(make_client, session_factory, copies=3)
    remove_sponsor_pool(session_factory, champ)
    assert play(player, champ, pilot).status_code == 201
    assert play(player, champ, pilot).status_code == 201
    finish_race(admin, champ, race, pilot)
    assert sponsor_inventory(session_factory, pilot) == {CARD: 1}
    assert play_statuses(session_factory) == ["consumata", "consumata"]
