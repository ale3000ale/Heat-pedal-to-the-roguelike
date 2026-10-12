from app.db.models import User
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


def sponsor_inventory(session_factory, pilot_id):
    with session_factory() as db:
        pilot = db.get(Pilot, pilot_id)
        return {c.name: c.copies for c in parse_cards(db.get(Deck, pilot.sponsor_inventory_deck_id).cards)}


def sponsor_pool(session_factory, championship_id):
    with session_factory() as db:
        deck_id = db.get(Championship, championship_id).sponsor_pool_deck_id
        return {c.name: c.copies for c in parse_cards(db.get(Deck, deck_id).cards)}


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


def open_review(client, championship_id, race_id):
    return client.post(f"/api/championships/{championship_id}/races/{race_id}/review")


def confirm_review(client, championship_id, race_id):
    return client.post(f"/api/championships/{championship_id}/races/{race_id}/review/confirm")


def play(player, championship_id, pilot_id):
    return player.post(
        f"/api/championships/{championship_id}/card-plays",
        json={"pilot_id": pilot_id, "card_name": CARD},
    )


def gift(player, championship_id, pilot_id):
    return player.post(
        f"/api/championships/{championship_id}/card-gifts", json={"pilot_id": pilot_id}
    )


def summary(admin, championship_id, race_id):
    return admin.get(f"/api/championships/{championship_id}/races/{race_id}/card-plays")


def cancel(admin, championship_id, race_id, play_id):
    return admin.post(
        f"/api/championships/{championship_id}/races/{race_id}/card-plays/{play_id}/cancel"
    )


def bonus(admin, championship_id, race_id, pilot_id, card_name=CARD):
    return admin.post(
        f"/api/championships/{championship_id}/races/{race_id}/card-bonus",
        json={"pilot_id": pilot_id, "card_name": card_name},
    )


def scenario(make_client, session_factory, copies=2, pool_copies=2):
    admin, player = setup_world(make_client, session_factory)
    championship_id = admin.post("/api/championships", json={"name": "Estate"}).json()["id"]
    pilot_id = enrolled_pilot(player, championship_id)
    give_sponsor_cards(session_factory, pilot_id, copies)
    give_sponsor_pool(session_factory, championship_id, pool_copies)
    race_id = start_race(admin, championship_id)
    return admin, player, championship_id, pilot_id, race_id


def reviewing(admin, championship_id, race_id, pilot_id):
    # Chiude la gara con i risultati e apre la revisione delle carte come admin.
    finish_race(admin, championship_id, race_id, pilot_id)
    assert open_review(admin, championship_id, race_id).status_code == 200


def test_summary_lists_the_plays_of_every_pilot(make_client, session_factory):
    admin, player, champ, pilot, race = scenario(make_client, session_factory)
    assert play(player, champ, pilot).status_code == 201
    r = summary(admin, champ, race)
    assert r.status_code == 200
    body = r.json()
    assert [p["pilot_id"] for p in body] == [pilot]
    assert [p["status"] for p in body[0]["plays"]] == ["giocata"]


def test_a_player_cannot_read_the_summary(make_client, session_factory):
    _, player, champ, _, race = scenario(make_client, session_factory)
    assert summary(player, champ, race).status_code in (401, 403)


def test_judge_cancel_keeps_the_log_and_frees_the_copy(make_client, session_factory):
    admin, player, champ, pilot, race = scenario(make_client, session_factory, copies=1)
    assert play(player, champ, pilot).status_code == 201
    play_id = summary(admin, champ, race).json()[0]["plays"][0]["id"]
    reviewing(admin, champ, race, pilot)
    r = cancel(admin, champ, race, play_id)
    assert r.status_code == 200
    assert r.json()["status"] == "annullata"
    state = player.get(f"/api/championships/{champ}/card-plays", params={"pilot_id": pilot}).json()
    assert state["available"][0]["copies_available"] == 1
    assert [p["status"] for p in state["plays"]] == ["annullata"]


def test_judge_cancel_is_refused_without_review_twice_and_after_the_confirm(
    make_client, session_factory
):
    admin, player, champ, pilot, race = scenario(make_client, session_factory)
    assert play(player, champ, pilot).status_code == 201
    assert play(player, champ, pilot).status_code == 201
    first, second = [p["id"] for p in summary(admin, champ, race).json()[0]["plays"]]
    assert cancel(admin, champ, race, first).status_code == 409
    reviewing(admin, champ, race, pilot)
    assert cancel(admin, champ, race, first).status_code == 200
    assert cancel(admin, champ, race, first).status_code == 409
    assert confirm_review(admin, champ, race).status_code == 200
    assert cancel(admin, champ, race, second).status_code == 409


def test_bonus_moves_a_copy_to_the_inventory_without_a_notification(make_client, session_factory):
    admin, player, champ, pilot, race = scenario(make_client, session_factory, copies=1, pool_copies=2)
    reviewing(admin, champ, race, pilot)
    r = bonus(admin, champ, race, pilot)
    assert r.status_code == 201
    assert sponsor_inventory(session_factory, pilot) == {CARD: 2}
    assert sponsor_pool(session_factory, champ) == {CARD: 1}
    gifts = player.get(f"/api/championships/{champ}/card-gifts", params={"pilot_id": pilot})
    assert gifts.json() == []


def test_bonus_is_refused_for_a_card_not_in_the_pool(make_client, session_factory):
    admin, _, champ, pilot, race = scenario(make_client, session_factory)
    reviewing(admin, champ, race, pilot)
    assert bonus(admin, champ, race, pilot, "Inesistente").status_code == 409


def test_bonus_is_refused_without_an_active_review(make_client, session_factory):
    admin, _, champ, pilot, race = scenario(make_client, session_factory)
    assert bonus(admin, champ, race, pilot).status_code == 409
    finish_race(admin, champ, race, pilot)
    assert bonus(admin, champ, race, pilot).status_code == 409


def test_players_cannot_play_or_gift_while_the_race_is_in_review(make_client, session_factory):
    admin, player, champ, pilot, race = scenario(make_client, session_factory)
    reviewing(admin, champ, race, pilot)
    assert play(player, champ, pilot).status_code == 409
    assert gift(player, champ, pilot).status_code == 409
    assert bonus(admin, champ, race, pilot).status_code == 201
