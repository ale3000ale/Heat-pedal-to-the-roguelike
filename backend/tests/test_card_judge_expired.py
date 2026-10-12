from tests.test_card_judge import (
    CARD,
    bonus,
    cancel,
    play,
    removal,
    reviewing,
    scenario,
    sponsor_inventory,
    sponsor_pool,
    summary,
)
from tests.test_race_review import play_statuses
from tests.test_race_review_reopen import make_review_expired


def test_removal_is_refused_when_the_review_is_expired(make_client, session_factory):
    admin, _, champ, pilot, race = scenario(make_client, session_factory)
    reviewing(admin, champ, race, pilot)
    make_review_expired(session_factory, race)
    assert removal(admin, champ, race, pilot).status_code == 409
    assert sponsor_inventory(session_factory, pilot) == {CARD: 2}
    assert sponsor_pool(session_factory, champ) == {CARD: 2}


def test_bonus_is_refused_when_the_review_is_expired(make_client, session_factory):
    admin, _, champ, pilot, race = scenario(make_client, session_factory)
    reviewing(admin, champ, race, pilot)
    make_review_expired(session_factory, race)
    assert bonus(admin, champ, race, pilot).status_code == 409
    assert sponsor_inventory(session_factory, pilot) == {CARD: 2}
    assert sponsor_pool(session_factory, champ) == {CARD: 2}


def test_cancel_is_refused_when_the_review_is_expired(make_client, session_factory):
    admin, player, champ, pilot, race = scenario(make_client, session_factory)
    assert play(player, champ, pilot).status_code == 201
    play_id = summary(admin, champ, race).json()[0]["plays"][0]["id"]
    reviewing(admin, champ, race, pilot)
    make_review_expired(session_factory, race)
    assert cancel(admin, champ, race, play_id).status_code == 409
    assert "annullata" not in play_statuses(session_factory)
