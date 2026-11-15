from datetime import timedelta

from app.db.models.deck import Deck
from app.db.models.pilot import Pilot
from app.db.models.race import Race
from app.services.cards.cards import CardEntry, dump_cards, parse_cards
from app.services.race.race_review import settle_expired_reviews
from tests.test_card_judge import CARD, reviewing, scenario, sponsor_inventory, sponsor_pool
from tests.test_review_counts_api import base, body


def expire(session_factory, champ, race):
    with session_factory() as db:
        row = db.get(Race, race)
        row.review_started_at -= timedelta(minutes=16)
        db.commit()
    with session_factory() as db:
        return settle_expired_reviews(db, champ)


def test_expiry_applies_valid_card_and_leaves_invalid_card_untouched(make_client, session_factory):
    admin, _, champ, pilot, race = scenario(make_client, session_factory, copies=2)
    with session_factory() as db:
        deck = db.get(Deck, db.get(Pilot, pilot).sponsor_inventory_deck_id)
        cards = parse_cards(deck.cards)
        cards.append(CardEntry(name="Casco", path="cards/sponsor/casco.webp", copies=1))
        deck.cards = dump_cards(cards)
        db.commit()
    reviewing(admin, champ, race, pilot)
    data = body(pilot, 3)
    data["pilots"][0]["cards"].append({"card_name": "Casco", "remaining": 0})
    assert admin.post(base(champ, race) + "/counts/confirm", json=data).status_code == 409
    assert expire(session_factory, champ, race) == 1
    assert sponsor_inventory(session_factory, pilot) == {CARD: 2}
    assert sponsor_pool(session_factory, champ) == {CARD: 2, "Casco": 1}
    with session_factory() as db:
        row = db.get(Race, race)
        assert row.review_closed_at is not None
        assert row.review_draft is not None
        assert settle_expired_reviews(db, champ) == 0


def test_expiry_applies_fully_valid_draft_and_clears_it(make_client, session_factory):
    admin, _, champ, pilot, race = scenario(make_client, session_factory, copies=2)
    reviewing(admin, champ, race, pilot)
    assert admin.put(base(champ, race) + "/draft", json=body(pilot, 0)).status_code == 204
    assert expire(session_factory, champ, race) == 1
    assert sponsor_inventory(session_factory, pilot) == {}
    assert sponsor_pool(session_factory, champ) == {CARD: 4}
    with session_factory() as db:
        assert db.get(Race, race).review_draft is None


def test_corrupt_draft_does_not_close_or_change_inventory(make_client, session_factory):
    admin, _, champ, pilot, race = scenario(make_client, session_factory, copies=2)
    reviewing(admin, champ, race, pilot)
    with session_factory() as db:
        db.get(Race, race).review_draft = "not-json"
        db.commit()
    assert expire(session_factory, champ, race) == 0
    assert sponsor_inventory(session_factory, pilot) == {CARD: 2}
    with session_factory() as db:
        assert db.get(Race, race).review_closed_at is None
        assert db.get(Race, race).review_draft == "not-json"
