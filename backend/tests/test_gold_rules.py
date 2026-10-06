from .test_races_api import (
    PASSWORD,
    make_admin,
    make_judge,
    make_player,
    new_race,
    put_results,
    setup,
)

DEFAULT_RULES = {"base": 20, "positions": [0, 0, 0, 0, 0, 0], "other": 0}


def gold_of(client, pilot_id):
    return client.get(f"/api/pilots/{pilot_id}").json()["gold"]


def put_rules(client, championship_id, base, positions, other):
    return client.put(
        f"/api/championships/{championship_id}/gold-rules",
        json={"base": base, "positions": positions, "other": other},
    )


def test_new_championship_starts_with_default_rules(make_client, session_factory):
    admin, player, cid, pilots = setup(make_client, session_factory, ["Anna"])
    assert admin.get(f"/api/championships/{cid}/gold-rules").json() == DEFAULT_RULES
    assert player.get(f"/api/championships/{cid}/gold-rules").json() == DEFAULT_RULES
    assert admin.get("/api/admin/championship-defaults").json() == DEFAULT_RULES


def test_everyone_gets_the_base_even_who_does_not_race(make_client, session_factory):
    admin, player, cid, pilots = setup(make_client, session_factory, ["Anna", "Beppe", "Carlo"])
    race_id = new_race(admin, cid)
    assert put_results(admin, cid, race_id, [pilots["Beppe"], pilots["Anna"]]).status_code == 200
    assert [gold_of(player, pilots[n]) for n in ("Anna", "Beppe", "Carlo")] == [20, 20, 20]


def test_position_modifiers_add_and_subtract(make_client, session_factory):
    admin, player, cid, pilots = setup(make_client, session_factory, ["Anna", "Beppe", "Carlo"])
    assert put_rules(admin, cid, 10, [5, -20, 0, 0, 0, 0], 0).status_code == 200
    race_id = new_race(admin, cid)
    put_results(admin, cid, race_id, [pilots["Anna"], pilots["Beppe"]])
    assert gold_of(player, pilots["Anna"]) == 15
    assert gold_of(player, pilots["Beppe"]) == 0
    assert gold_of(player, pilots["Carlo"]) == 10


def test_one_modifier_covers_every_position_from_seventh(make_client, session_factory):
    names = [f"Pilota {n}" for n in range(1, 9)]
    admin, player, cid, pilots = setup(make_client, session_factory, names)
    assert put_rules(admin, cid, 10, [0, 0, 0, 0, 0, 0], -4).status_code == 200
    race_id = new_race(admin, cid)
    put_results(admin, cid, race_id, [pilots[n] for n in names[:7]])
    assert [gold_of(player, pilots[n]) for n in names[:6]] == [10] * 6
    assert gold_of(player, pilots[names[6]]) == 6
    assert gold_of(player, pilots[names[7]]) == 10


def test_a_negative_modifier_never_goes_below_zero(make_client, session_factory):
    admin, player, cid, pilots = setup(make_client, session_factory, ["Anna"])
    assert put_rules(admin, cid, 10, [-1000, 0, 0, 0, 0, 0], 0).status_code == 200
    put_results(admin, cid, new_race(admin, cid), [pilots["Anna"]])
    assert gold_of(player, pilots["Anna"]) == 0


def test_gold_adds_up_over_several_races(make_client, session_factory):
    admin, player, cid, pilots = setup(make_client, session_factory, ["Anna"])
    for _ in range(3):
        put_results(admin, cid, new_race(admin, cid), [pilots["Anna"]])
    assert gold_of(player, pilots["Anna"]) == 60


def test_changed_rules_apply_only_from_the_next_race(make_client, session_factory):
    admin, player, cid, pilots = setup(make_client, session_factory, ["Anna", "Beppe"])
    anna, beppe = pilots["Anna"], pilots["Beppe"]
    first = new_race(admin, cid)
    put_results(admin, cid, first, [anna, beppe])
    assert gold_of(player, anna) == 20
    assert put_rules(admin, cid, 50, [10, 0, 0, 0, 0, 0], 0).status_code == 200
    assert gold_of(player, anna) == 20
    put_results(admin, cid, first, [beppe, anna])
    assert gold_of(player, anna) == 20
    assert gold_of(player, beppe) == 20
    second = new_race(admin, cid)
    put_results(admin, cid, second, [beppe, anna])
    assert gold_of(player, beppe) == 80
    assert gold_of(player, anna) == 70


def test_race_gold_uses_the_rules_when_the_race_is_closed(make_client, session_factory):
    admin, player, cid, pilots = setup(make_client, session_factory, ["Anna"])
    race_id = new_race(admin, cid)
    assert put_rules(admin, cid, 30, [0, 0, 0, 0, 0, 0], 0).status_code == 200
    put_results(admin, cid, race_id, [pilots["Anna"]])
    assert gold_of(player, pilots["Anna"]) == 30


def test_judge_closing_a_race_gives_the_gold(make_client, session_factory):
    admin, player, cid, pilots = setup(make_client, session_factory, ["Anna"])
    judge = make_judge(make_client, session_factory)
    race_id = new_race(judge, cid)
    assert put_results(judge, cid, race_id, [pilots["Anna"]]).status_code == 200
    assert gold_of(player, pilots["Anna"]) == 20


def test_defaults_are_copied_to_new_championships_only(make_client, session_factory):
    admin, player, cid, pilots = setup(make_client, session_factory, ["Anna"])
    new_defaults = {"base": 35, "positions": [10, 5, 0, 0, 0, -5], "other": -2}
    r = admin.put("/api/admin/championship-defaults", json=new_defaults)
    assert r.status_code == 200
    assert r.json() == new_defaults
    assert admin.get("/api/admin/championship-defaults").json() == new_defaults
    assert admin.get(f"/api/championships/{cid}/gold-rules").json() == DEFAULT_RULES
    other = admin.post("/api/championships", json={"name": "Inverno"}).json()["id"]
    assert admin.get(f"/api/championships/{other}/gold-rules").json() == new_defaults


def test_changing_a_championship_does_not_touch_the_defaults(make_client, session_factory):
    admin, player, cid, pilots = setup(make_client, session_factory, ["Anna"])
    assert put_rules(admin, cid, 99, [1, 2, 3, 4, 5, 6], 7).status_code == 200
    assert admin.get("/api/admin/championship-defaults").json() == DEFAULT_RULES
    other = admin.post("/api/championships", json={"name": "Inverno"}).json()["id"]
    assert admin.get(f"/api/championships/{other}/gold-rules").json() == DEFAULT_RULES


def test_only_the_admin_can_change_rules(make_client, session_factory):
    admin, player, cid, pilots = setup(make_client, session_factory, ["Anna"])
    judge = make_judge(make_client, session_factory)
    assert put_rules(player, cid, 10, [0] * 6, 0).status_code == 403
    assert put_rules(judge, cid, 10, [0] * 6, 0).status_code == 403
    assert put_rules(make_client(), cid, 10, [0] * 6, 0).status_code == 401
    body = {"base": 10, "positions": [0] * 6, "other": 0}
    assert player.get("/api/admin/championship-defaults").status_code == 403
    assert player.put("/api/admin/championship-defaults", json=body).status_code == 403
    assert judge.put("/api/admin/championship-defaults", json=body).status_code == 403
    assert make_client().get("/api/admin/championship-defaults").status_code == 401
    assert admin.get(f"/api/championships/{cid}/gold-rules").json() == DEFAULT_RULES


def test_invalid_rules_are_rejected(make_client, session_factory):
    admin, player, cid, pilots = setup(make_client, session_factory, ["Anna"])
    assert put_rules(admin, cid, -1, [0] * 6, 0).status_code == 422
    assert put_rules(admin, cid, 10001, [0] * 6, 0).status_code == 422
    assert put_rules(admin, cid, 10, [0] * 5, 0).status_code == 422
    assert put_rules(admin, cid, 10, [0] * 7, 0).status_code == 422
    assert put_rules(admin, cid, 10, [1001, 0, 0, 0, 0, 0], 0).status_code == 422
    assert put_rules(admin, cid, 10, [0] * 6, -1001).status_code == 422
    assert put_rules(admin, cid, 10, [0] * 6, 1001).status_code == 422
    assert put_rules(admin, cid, 10000, [-1000] * 6, 1000).status_code == 200
    body = {"base": -5, "positions": [0] * 6, "other": 0}
    assert admin.put("/api/admin/championship-defaults", json=body).status_code == 422
    assert admin.get("/api/admin/championship-defaults").json() == DEFAULT_RULES


def test_rules_of_unknown_championship_are_404(make_client, session_factory):
    admin, player, cid, pilots = setup(make_client, session_factory, ["Anna"])
    assert admin.get("/api/championships/999/gold-rules").status_code == 404
    assert put_rules(admin, 999, 10, [0] * 6, 0).status_code == 404


def test_closed_championship_rules_cannot_change(make_client, session_factory):
    admin, player, cid, pilots = setup(make_client, session_factory, ["Anna"])
    admin.post(f"/api/championships/{cid}/close")
    assert put_rules(admin, cid, 10, [0] * 6, 0).status_code == 409
    assert admin.get(f"/api/championships/{cid}/gold-rules").json() == DEFAULT_RULES
