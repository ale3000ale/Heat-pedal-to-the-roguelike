from tests.test_race_review import (
    CARD,
    closed_scenario,
    confirm_review,
    judge_client,
    play_statuses,
    remove_sponsor_pool,
    sponsor_inventory,
    sponsor_pool,
)
from tests.test_race_review_reopen import reopen_review


def play_ids(client, championship_id, race_id):
    # Identificativi delle giocate della gara, in ordine cronologico.
    r = client.get(f"/api/championships/{championship_id}/races/{race_id}/card-plays")
    assert r.status_code == 200
    return [play["id"] for pilot in r.json() for play in pilot["plays"]]


def cancel_play(client, championship_id, race_id, play_id):
    return client.post(
        f"/api/championships/{championship_id}/races/{race_id}/card-plays/{play_id}/cancel"
    )


def confirmed_and_reopened(make_client, session_factory):
    # Due giocate confermate e consumate, poi revisione riaperta dall'admin.
    admin, player, champ, pilot, race = closed_scenario(
        make_client, session_factory, copies=3, pool_copies=1, plays=2
    )
    assert confirm_review(admin, champ, race).status_code == 200
    assert sponsor_inventory(session_factory, pilot) == {CARD: 1}
    assert sponsor_pool(session_factory, champ) == {CARD: 3}
    assert reopen_review(admin, champ, race).status_code == 200
    return admin, player, champ, pilot, race


def test_cancelling_a_consumed_play_returns_the_card_from_the_pool(make_client, session_factory):
    admin, _, champ, pilot, race = confirmed_and_reopened(make_client, session_factory)
    first, _ = play_ids(admin, champ, race)
    r = cancel_play(admin, champ, race, first)
    assert r.status_code == 200
    assert r.json()["status"] == "annullata"
    assert sponsor_inventory(session_factory, pilot) == {CARD: 2}
    assert sponsor_pool(session_factory, champ) == {CARD: 2}
    assert play_statuses(session_factory) == ["annullata", "consumata"]


def test_cancelling_a_consumed_play_twice_is_refused(make_client, session_factory):
    admin, _, champ, pilot, race = confirmed_and_reopened(make_client, session_factory)
    first, _ = play_ids(admin, champ, race)
    assert cancel_play(admin, champ, race, first).status_code == 200
    assert cancel_play(admin, champ, race, first).status_code == 409
    assert sponsor_inventory(session_factory, pilot) == {CARD: 2}
    assert sponsor_pool(session_factory, champ) == {CARD: 2}


def test_cancelling_a_consumed_play_is_refused_when_the_pool_lost_the_card(
    make_client, session_factory
):
    admin, _, champ, pilot, race = confirmed_and_reopened(make_client, session_factory)
    first, _ = play_ids(admin, champ, race)
    remove_sponsor_pool(session_factory, champ)
    assert cancel_play(admin, champ, race, first).status_code == 409
    assert sponsor_inventory(session_factory, pilot) == {CARD: 1}
    assert play_statuses(session_factory) == ["consumata", "consumata"]


def test_cancelling_a_consumed_play_needs_an_active_review(make_client, session_factory):
    admin, _, champ, pilot, race = closed_scenario(
        make_client, session_factory, copies=3, pool_copies=1, plays=2
    )
    first, _ = play_ids(admin, champ, race)
    assert confirm_review(admin, champ, race).status_code == 200
    assert cancel_play(admin, champ, race, first).status_code == 409
    assert sponsor_inventory(session_factory, pilot) == {CARD: 1}
    assert sponsor_pool(session_factory, champ) == {CARD: 3}
    assert play_statuses(session_factory) == ["consumata", "consumata"]


def test_another_judge_cannot_cancel_during_a_reopened_review(make_client, session_factory):
    admin, _, champ, pilot, race = confirmed_and_reopened(make_client, session_factory)
    first, _ = play_ids(admin, champ, race)
    judge = judge_client(make_client, session_factory)
    assert cancel_play(judge, champ, race, first).status_code == 409
    assert sponsor_inventory(session_factory, pilot) == {CARD: 1}
    assert play_statuses(session_factory) == ["consumata", "consumata"]


def test_confirming_again_after_a_cancel_consumes_only_the_remaining_play(
    make_client, session_factory
):
    admin, _, champ, pilot, race = confirmed_and_reopened(make_client, session_factory)
    first, _ = play_ids(admin, champ, race)
    assert cancel_play(admin, champ, race, first).status_code == 200
    assert confirm_review(admin, champ, race).status_code == 200
    assert sponsor_inventory(session_factory, pilot) == {CARD: 2}
    assert sponsor_pool(session_factory, champ) == {CARD: 2}
    assert play_statuses(session_factory) == ["annullata", "consumata"]
