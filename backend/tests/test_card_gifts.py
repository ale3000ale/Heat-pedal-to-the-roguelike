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


def play(player, championship_id, pilot_id):
    return player.post(
        f"/api/championships/{championship_id}/card-plays",
        json={"pilot_id": pilot_id, "card_name": CARD},
    )


def gift(player, championship_id, pilot_id):
    return player.post(
        f"/api/championships/{championship_id}/card-gifts", json={"pilot_id": pilot_id}
    )


def unseen(player, championship_id, pilot_id):
    return player.get(
        f"/api/championships/{championship_id}/card-gifts", params={"pilot_id": pilot_id}
    )


def scenario(make_client, session_factory, copies=1, pool_copies=2):
    admin, player = setup_world(make_client, session_factory)
    championship_id = admin.post("/api/championships", json={"name": "Estate"}).json()["id"]
    pilot_id = enrolled_pilot(player, championship_id)
    give_sponsor_cards(session_factory, pilot_id, copies)
    give_sponsor_pool(session_factory, championship_id, pool_copies)
    race_id = start_race(admin, championship_id)
    return admin, player, championship_id, pilot_id, race_id


def test_gift_moves_a_copy_from_the_pool_to_the_inventory(make_client, session_factory):
    _, player, champ, pilot, _ = scenario(make_client, session_factory, copies=1, pool_copies=2)
    r = gift(player, champ, pilot)
    assert r.status_code == 201
    assert r.json()["card_name"] == CARD
    assert sponsor_inventory(session_factory, pilot) == {CARD: 2}
    assert sponsor_pool(session_factory, champ) == {CARD: 1}


def test_gift_adds_a_new_inventory_row_when_the_card_is_not_owned(make_client, session_factory):
    _, player, champ, pilot, _ = scenario(make_client, session_factory, copies=1, pool_copies=1)
    with session_factory() as db:
        db.get(Deck, db.get(Pilot, pilot).sponsor_inventory_deck_id).cards = dump_cards([])
        db.commit()
    assert gift(player, champ, pilot).status_code == 201
    assert sponsor_inventory(session_factory, pilot) == {CARD: 1}


def test_gift_is_refused_when_the_pool_is_empty(make_client, session_factory):
    _, player, champ, pilot, _ = scenario(make_client, session_factory, copies=1, pool_copies=1)
    assert gift(player, champ, pilot).status_code == 201
    assert gift(player, champ, pilot).status_code == 409
    assert sponsor_inventory(session_factory, pilot) == {CARD: 2}


def test_gift_is_refused_without_a_race_in_progress(make_client, session_factory):
    admin, player, champ, pilot, race = scenario(make_client, session_factory)
    finish_race(admin, champ, race, pilot)
    assert gift(player, champ, pilot).status_code == 409


def test_a_player_cannot_gift_to_someone_elses_pilot(make_client, session_factory):
    admin, _, champ, pilot, _ = scenario(make_client, session_factory)
    assert gift(admin, champ, pilot).status_code == 404


def test_a_gifted_card_can_be_played_in_the_same_race(make_client, session_factory):
    _, player, champ, pilot, _ = scenario(make_client, session_factory, copies=1, pool_copies=2)
    assert play(player, champ, pilot).status_code == 201
    assert play(player, champ, pilot).status_code == 409
    assert gift(player, champ, pilot).status_code == 201
    assert play(player, champ, pilot).status_code == 201


def test_unseen_gifts_are_listed_until_they_are_marked_seen(make_client, session_factory):
    _, player, champ, pilot, _ = scenario(make_client, session_factory, copies=1, pool_copies=2)
    assert unseen(player, champ, pilot).json() == []
    assert gift(player, champ, pilot).status_code == 201
    listed = unseen(player, champ, pilot).json()
    assert [g["card_name"] for g in listed] == [CARD]
    r = player.post(f"/api/championships/{champ}/card-gifts/seen", json={"pilot_id": pilot})
    assert r.status_code == 204
    assert unseen(player, champ, pilot).json() == []
