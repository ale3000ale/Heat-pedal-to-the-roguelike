from tests.test_race_review import (
    closed_scenario,
    confirm_review,
    open_review,
    scenario,
)


def race_url(championship_id, race_id):
    return f"/api/championships/{championship_id}/races/{race_id}"


def race_status(client, championship_id, race_id):
    r = client.get(race_url(championship_id, race_id))
    assert r.status_code == 200
    return r.json()["status"]


def test_a_race_without_results_is_in_progress(make_client, session_factory):
    admin, _, champ, _, race = scenario(make_client, session_factory)
    assert race_status(admin, champ, race) == "in_progress"


def test_a_race_with_results_and_no_review_is_to_review(make_client, session_factory):
    admin, _, champ, pilot, race = scenario(make_client, session_factory)
    r = admin.put(
        f"/api/championships/{champ}/races/{race}/results",
        json={"results": [{"pilot_id": pilot, "sponsor_points": 0}]},
    )
    assert r.status_code == 200
    assert race_status(admin, champ, race) == "to_review"


def test_a_race_with_an_open_review_is_in_review(make_client, session_factory):
    admin, _, champ, _, race = closed_scenario(make_client, session_factory)
    assert race_status(admin, champ, race) == "in_review"


def test_a_race_with_a_confirmed_review_is_closed(make_client, session_factory):
    admin, _, champ, _, race = closed_scenario(make_client, session_factory)
    assert confirm_review(admin, champ, race).status_code == 200
    assert race_status(admin, champ, race) == "closed"


def test_the_status_goes_back_to_in_review_after_the_reopening(make_client, session_factory):
    admin, _, champ, _, race = closed_scenario(make_client, session_factory)
    assert confirm_review(admin, champ, race).status_code == 200
    reopen = admin.post(f"/api/championships/{champ}/races/{race}/review/reopen")
    assert reopen.status_code == 200
    assert race_status(admin, champ, race) == "in_review"
    assert open_review(admin, champ, race).status_code == 200
