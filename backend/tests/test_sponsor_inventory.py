from app.db.models import User
from app.db.models.championship import Championship
from app.db.models.deck import Deck
from app.db.models.pilot import Pilot
from app.services.cards import dump_cards
from app.services.championships import close_championship, enroll_pilot
from app.services.pilots import create_pilot

PASSWORD = "password123"


def _register(client, username="mario"):
    r = client.post("/api/auth/register", json={"username": username, "password": PASSWORD})
    assert r.status_code == 201
    return r.json()["id"]


def _setup(client, session_factory):
    # Un utente con un team, un pilota creato dal servizio e un campionato attivo.
    user_id = _register(client)
    team_id = client.post("/api/teams", json={"name": "Scuderia Rossa"}).json()["id"]
    with session_factory() as db:
        user = db.get(User, user_id)
        pilot = create_pilot(db, user, "Pilota Uno", team_id)
        championship = Championship(name="Camp", name_key="camp")
        db.add(championship)
        db.commit()
        return user_id, pilot.id, championship.id


def _sponsor_cards(session_factory, pilot_id):
    with session_factory() as db:
        pilot = db.get(Pilot, pilot_id)
        return db.get(Deck, pilot.sponsor_inventory_deck_id).cards


def _fill_sponsor_inventory(session_factory, pilot_id):
    with session_factory() as db:
        pilot = db.get(Pilot, pilot_id)
        db.get(Deck, pilot.sponsor_inventory_deck_id).cards = "da-svuotare"
        db.commit()


def test_new_pilot_has_an_empty_sponsor_inventory_of_its_own(client, session_factory):
    _, pilot_id, _ = _setup(client, session_factory)
    with session_factory() as db:
        pilot = db.get(Pilot, pilot_id)
        deck_ids = {
            pilot.inventory_deck_id,
            pilot.sponsor_inventory_deck_id,
            pilot.game_deck_id,
        }
        assert len(deck_ids) == 3
        assert db.get(Deck, pilot.sponsor_inventory_deck_id).cards == dump_cards([])


def test_enroll_empties_the_sponsor_inventory(client, session_factory):
    user_id, pilot_id, championship_id = _setup(client, session_factory)
    _fill_sponsor_inventory(session_factory, pilot_id)
    with session_factory() as db:
        enroll_pilot(db, db.get(User, user_id), championship_id, pilot_id)
    assert _sponsor_cards(session_factory, pilot_id) == dump_cards([])


def test_close_empties_the_sponsor_inventory(client, session_factory):
    user_id, pilot_id, championship_id = _setup(client, session_factory)
    with session_factory() as db:
        enroll_pilot(db, db.get(User, user_id), championship_id, pilot_id)
    _fill_sponsor_inventory(session_factory, pilot_id)
    with session_factory() as db:
        close_championship(db, championship_id)
    assert _sponsor_cards(session_factory, pilot_id) == dump_cards([])
