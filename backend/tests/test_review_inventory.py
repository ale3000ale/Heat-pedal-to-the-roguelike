from app.db.models.championship import Championship
from app.db.models.deck import Deck, DeckPrototype
from app.services.cards import CardEntry, dump_cards
from tests.test_card_judge import (
    CARD,
    cancel,
    confirm_review,
    finish_race,
    gift,
    play,
    reviewing,
    scenario,
    summary,
)


def inventory(client, championship_id, race_id):
    return client.get(f"/api/championships/{championship_id}/races/{race_id}/review/inventory")


def cards_of(response):
    return response.json()["pilots"][0]["cards"]


def test_inventory_shows_copies_left_over_the_total(make_client, session_factory):
    admin, player, champ, pilot, race = scenario(make_client, session_factory, copies=2)
    assert play(player, champ, pilot).status_code == 201
    reviewing(admin, champ, race, pilot)
    r = inventory(admin, champ, race)
    assert r.status_code == 200
    assert r.json()["race_id"] == race
    assert r.json()["pilots"][0]["pilot_id"] == pilot
    assert cards_of(r) == [
        {
            "card_name": CARD,
            "card_path": "cards/sponsor/turbo.webp",
            "total": 2,
            "remaining": 1,
            "gifted": 0,
            "start": 2,
            "pool_now": 2,
            "pool_max": None,
        }
    ]


def test_inventory_counts_the_bonus_copies_from_the_s_key(make_client, session_factory):
    admin, player, champ, pilot, race = scenario(
        make_client, session_factory, copies=1, pool_copies=2
    )
    assert gift(player, champ, pilot).status_code == 201
    assert play(player, champ, pilot).status_code == 201
    assert play(player, champ, pilot).status_code == 201
    reviewing(admin, champ, race, pilot)
    card = cards_of(inventory(admin, champ, race))[0]
    assert (card["total"], card["remaining"], card["gifted"], card["start"]) == (2, 0, 1, 1)
    assert card["pool_now"] == 1


def test_a_cancelled_play_gives_the_copy_back(make_client, session_factory):
    admin, player, champ, pilot, race = scenario(make_client, session_factory, copies=1)
    assert play(player, champ, pilot).status_code == 201
    play_id = summary(admin, champ, race).json()[0]["plays"][0]["id"]
    reviewing(admin, champ, race, pilot)
    assert cards_of(inventory(admin, champ, race))[0]["remaining"] == 0
    assert cancel(admin, champ, race, play_id).status_code == 200
    card = cards_of(inventory(admin, champ, race))[0]
    assert (card["total"], card["remaining"]) == (1, 1)


def test_a_reopened_review_starts_from_the_last_saved_state(make_client, session_factory):
    admin, player, champ, pilot, race = scenario(
        make_client, session_factory, copies=1, pool_copies=2
    )
    assert play(player, champ, pilot).status_code == 201
    reviewing(admin, champ, race, pilot)
    assert confirm_review(admin, champ, race).status_code == 200
    reopened = admin.post(f"/api/championships/{champ}/races/{race}/review/reopen")
    assert reopened.status_code == 200
    card = cards_of(inventory(admin, champ, race))[0]
    assert (card["total"], card["remaining"], card["pool_now"]) == (1, 0, 3)


def test_pool_max_comes_from_the_pool_the_championship_was_copied_from(
    make_client, session_factory
):
    admin, _, champ, pilot, race = scenario(make_client, session_factory)
    with session_factory() as db:
        prototype = DeckPrototype(
            name="sponsor-prova",
            kind="sponsor",
            base_cards=dump_cards(
                [CardEntry(name=CARD, path="cards/sponsor/turbo.webp", copies=7)]
            ),
        )
        db.add(prototype)
        db.flush()
        pool_deck_id = db.get(Championship, champ).sponsor_pool_deck_id
        db.get(Deck, pool_deck_id).id_prototype = prototype.id
        db.commit()
    reviewing(admin, champ, race, pilot)
    assert cards_of(inventory(admin, champ, race))[0]["pool_max"] == 7


def test_a_player_cannot_read_the_review_inventory(make_client, session_factory):
    admin, player, champ, pilot, race = scenario(make_client, session_factory)
    reviewing(admin, champ, race, pilot)
    assert inventory(player, champ, race).status_code in (401, 403)


def test_inventory_is_refused_for_a_race_without_results(make_client, session_factory):
    admin, _, champ, _, race = scenario(make_client, session_factory)
    assert inventory(admin, champ, race).status_code == 409


def test_inventory_of_an_unknown_race_gives_404(make_client, session_factory):
    admin, _, champ, pilot, race = scenario(make_client, session_factory)
    finish_race(admin, champ, race, pilot)
    assert inventory(admin, champ, 99999).status_code == 404
