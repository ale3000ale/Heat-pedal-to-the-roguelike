from datetime import datetime, timedelta, timezone

from app.db.models.race import Race
from tests.test_race_review import (
    CARD,
    closed_scenario,
    confirm_review,
    judge_client,
    open_review,
    play_statuses,
    scenario,
    sponsor_inventory,
    sponsor_pool,
    start_race,
)


def review_url(championship_id, race_id):
    return f"/api/championships/{championship_id}/races/{race_id}/review"


def reopen_review(client, championship_id, race_id):
    return client.post(review_url(championship_id, race_id) + "/reopen")


def read_review(client, championship_id, race_id):
    return client.get(review_url(championship_id, race_id))


def make_review_expired(session_factory, race_id):
    # Porta l'apertura della revisione a 20 minuti fa, oltre i 15 concessi.
    with session_factory() as db:
        db.get(Race, race_id).review_started_at = datetime.now(timezone.utc) - timedelta(minutes=20)
        db.commit()


def test_a_player_can_read_the_review_state_with_is_last_race(make_client, session_factory):
    _, player, champ, _, race = closed_scenario(make_client, session_factory)
    r = read_review(player, champ, race)
    assert r.status_code == 200
    body = r.json()
    assert body["race_id"] == race
    assert body["in_review"] is True
    assert body["is_last_race"] is True


def test_reading_the_state_of_an_unknown_race_or_championship(make_client, session_factory):
    _, player, champ, _, _ = closed_scenario(make_client, session_factory)
    assert read_review(player, champ, 9999).status_code == 404
    assert read_review(player, 9999, 1).status_code == 404


def test_reading_the_state_confirms_an_expired_review(make_client, session_factory):
    _, player, champ, pilot, race = closed_scenario(make_client, session_factory, copies=3, plays=2)
    make_review_expired(session_factory, race)
    body = read_review(player, champ, race).json()
    assert body["in_review"] is False
    assert body["reviewer_user_id"] is None
    assert body["review_closed_at"] is not None
    assert sponsor_inventory(session_factory, pilot) == {CARD: 1}
    assert sponsor_pool(session_factory, champ) == {CARD: 3}
    assert play_statuses(session_factory) == ["consumata", "consumata"]


def test_an_active_review_is_not_confirmed_by_reading_the_state(make_client, session_factory):
    _, player, champ, pilot, race = closed_scenario(make_client, session_factory, copies=3, plays=2)
    body = read_review(player, champ, race).json()
    assert body["in_review"] is True
    assert body["review_closed_at"] is None
    assert sponsor_inventory(session_factory, pilot) == {CARD: 3}


def test_the_admin_reopens_the_last_race_after_the_confirmation(make_client, session_factory):
    admin, _, champ, _, race = closed_scenario(make_client, session_factory, plays=1)
    assert confirm_review(admin, champ, race).status_code == 200
    r = reopen_review(admin, champ, race)
    assert r.status_code == 200
    body = r.json()
    assert body["in_review"] is True
    assert body["review_closed_at"] is None
    assert body["reviewer_user_id"] is not None
    assert body["review_expires_at"] is not None
    assert body["is_last_race"] is True


def test_a_judge_cannot_reopen_a_confirmed_review(make_client, session_factory):
    admin, _, champ, _, race = closed_scenario(make_client, session_factory)
    assert confirm_review(admin, champ, race).status_code == 200
    judge = judge_client(make_client, session_factory)
    assert reopen_review(judge, champ, race).status_code == 403
    assert read_review(judge, champ, race).json()["review_closed_at"] is not None


def test_a_player_cannot_reopen_a_confirmed_review(make_client, session_factory):
    admin, player, champ, _, race = closed_scenario(make_client, session_factory)
    assert confirm_review(admin, champ, race).status_code == 200
    assert reopen_review(player, champ, race).status_code == 403


def test_reopening_a_review_that_is_not_confirmed_is_refused(make_client, session_factory):
    admin, _, champ, _, race = closed_scenario(make_client, session_factory)
    assert reopen_review(admin, champ, race).status_code == 409


def test_reopening_before_the_results_is_refused(make_client, session_factory):
    admin, _, champ, _, race = scenario(make_client, session_factory)
    assert reopen_review(admin, champ, race).status_code == 409


def test_reopening_a_race_that_is_not_the_last_is_refused(make_client, session_factory):
    admin, _, champ, _, race = closed_scenario(make_client, session_factory)
    assert confirm_review(admin, champ, race).status_code == 200
    second_race = start_race(admin, champ)
    assert second_race != race
    assert reopen_review(admin, champ, race).status_code == 409
    assert read_review(admin, champ, race).json()["is_last_race"] is False
    assert read_review(admin, champ, second_race).json()["is_last_race"] is True


def test_reopening_an_unknown_race_or_championship(make_client, session_factory):
    admin, _, champ, _, _ = scenario(make_client, session_factory)
    assert reopen_review(admin, champ, 9999).status_code == 404
    assert reopen_review(admin, 9999, 1).status_code == 404


def test_a_reopened_review_blocks_a_second_reviewer(make_client, session_factory):
    admin, _, champ, _, race = closed_scenario(make_client, session_factory)
    assert confirm_review(admin, champ, race).status_code == 200
    assert reopen_review(admin, champ, race).status_code == 200
    judge = judge_client(make_client, session_factory)
    assert open_review(judge, champ, race).status_code == 409
    assert open_review(admin, champ, race).status_code == 200


def test_confirming_again_after_the_reopening_does_not_consume_twice(make_client, session_factory):
    admin, _, champ, pilot, race = closed_scenario(make_client, session_factory, copies=3, plays=2)
    assert confirm_review(admin, champ, race).status_code == 200
    assert sponsor_inventory(session_factory, pilot) == {CARD: 1}
    assert reopen_review(admin, champ, race).status_code == 200
    assert confirm_review(admin, champ, race).status_code == 200
    assert sponsor_inventory(session_factory, pilot) == {CARD: 1}
    assert sponsor_pool(session_factory, champ) == {CARD: 3}
