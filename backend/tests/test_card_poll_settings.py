from .test_races_api import make_judge, setup

URL = "/api/admin/card-poll"
DEFAULT_RULES = {"base": 20, "positions": [0, 0, 0, 0, 0, 0], "other": 0}


def put_seconds(client, seconds):
    return client.put(URL, json={"seconds": seconds})


def test_default_is_five_seconds_for_everyone(make_client, session_factory):
    admin, player, cid, pilots = setup(make_client, session_factory, ["Anna"])
    judge = make_judge(make_client, session_factory)
    for client in (admin, player, judge):
        response = client.get(URL)
        assert response.status_code == 200
        assert response.json() == {"seconds": 5}


def test_anonymous_user_cannot_read_the_interval(make_client, session_factory):
    setup(make_client, session_factory, ["Anna"])
    assert make_client().get(URL).status_code == 401


def test_admin_changes_the_interval_and_everyone_sees_it(make_client, session_factory):
    admin, player, cid, pilots = setup(make_client, session_factory, ["Anna"])
    judge = make_judge(make_client, session_factory)
    response = put_seconds(admin, 8)
    assert response.status_code == 200
    assert response.json() == {"seconds": 8}
    for client in (admin, player, judge):
        assert client.get(URL).json() == {"seconds": 8}


def test_limits_one_and_ten_are_accepted(make_client, session_factory):
    admin, player, cid, pilots = setup(make_client, session_factory, ["Anna"])
    assert put_seconds(admin, 1).status_code == 200
    assert admin.get(URL).json() == {"seconds": 1}
    assert put_seconds(admin, 10).status_code == 200
    assert admin.get(URL).json() == {"seconds": 10}


def test_values_out_of_range_are_rejected_and_nothing_changes(make_client, session_factory):
    admin, player, cid, pilots = setup(make_client, session_factory, ["Anna"])
    assert put_seconds(admin, 7).status_code == 200
    for invalid in (0, 11, -1, 100):
        assert put_seconds(admin, invalid).status_code == 422
    assert admin.put(URL, json={"seconds": "abc"}).status_code == 422
    assert admin.put(URL, json={}).status_code == 422
    assert admin.get(URL).json() == {"seconds": 7}


def test_only_the_admin_can_change_the_interval(make_client, session_factory):
    admin, player, cid, pilots = setup(make_client, session_factory, ["Anna"])
    judge = make_judge(make_client, session_factory)
    assert put_seconds(player, 3).status_code == 403
    assert put_seconds(judge, 3).status_code == 403
    assert put_seconds(make_client(), 3).status_code == 401
    assert admin.get(URL).json() == {"seconds": 5}


def test_interval_does_not_touch_the_gold_rules(make_client, session_factory):
    admin, player, cid, pilots = setup(make_client, session_factory, ["Anna"])
    assert put_seconds(admin, 2).status_code == 200
    assert admin.get("/api/admin/championship-defaults").json() == DEFAULT_RULES
    new_rules = {"base": 35, "positions": [10, 5, 0, 0, 0, -5], "other": -2}
    assert admin.put("/api/admin/championship-defaults", json=new_rules).status_code == 200
    assert admin.get(URL).json() == {"seconds": 2}


def test_interval_applies_to_existing_championships_too(make_client, session_factory):
    admin, player, cid, pilots = setup(make_client, session_factory, ["Anna"])
    other = admin.post("/api/championships", json={"name": "Inverno"})
    assert other.status_code in (200, 201)
    assert put_seconds(admin, 9).status_code == 200
    assert player.get(URL).json() == {"seconds": 9}
