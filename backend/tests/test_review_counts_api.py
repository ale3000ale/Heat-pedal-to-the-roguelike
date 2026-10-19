from tests.test_card_judge import (
    CARD, other_judge, play, reviewing, scenario, sponsor_inventory, sponsor_pool,
)


def base(champ, race):
    return f"/api/championships/{champ}/races/{race}/review"


def body(pilot, remaining):
    return {"pilots": [{"pilot_id": pilot, "cards": [
        {"card_name": CARD, "remaining": remaining}
    ]}]}


def test_draft_round_trip_does_not_move_cards(make_client, session_factory):
    admin, _, champ, pilot, race = scenario(make_client, session_factory, copies=2)
    reviewing(admin, champ, race, pilot)
    url = base(champ, race) + "/draft"
    assert admin.get(url).json() is None
    data = body(pilot, 0)
    response = admin.put(url, json=data)
    assert response.status_code == 204
    assert response.content == b""
    assert admin.get(url).json() == data
    assert sponsor_inventory(session_factory, pilot) == {CARD: 2}
    assert sponsor_pool(session_factory, champ) == {CARD: 2}


def test_confirm_counts_returns_closed_review(make_client, session_factory):
    admin, player, champ, pilot, race = scenario(make_client, session_factory, copies=2)
    assert play(player, champ, pilot).status_code == 201
    reviewing(admin, champ, race, pilot)
    response = admin.post(base(champ, race) + "/counts/confirm", json=body(pilot, 0))
    assert response.status_code == 200
    assert response.json()["review_closed_at"] is not None
    assert response.json()["in_review"] is False
    assert sponsor_inventory(session_factory, pilot) == {}
    assert sponsor_pool(session_factory, champ) == {CARD: 4}
    assert admin.post(base(champ, race) + "/counts/confirm", json=body(pilot, 0)).status_code == 409


def test_conflict_reports_cards_and_preserves_draft(make_client, session_factory):
    admin, _, champ, pilot, race = scenario(make_client, session_factory, copies=2)
    reviewing(admin, champ, race, pilot)
    data = body(pilot, 3)
    response = admin.post(base(champ, race) + "/counts/confirm", json=data)
    assert response.status_code == 409
    assert response.json()["detail"]["incongruities"][0]["card_name"] == CARD
    assert admin.get(base(champ, race) + "/draft").json() == data
    assert sponsor_inventory(session_factory, pilot) == {CARD: 2}


def test_other_judge_cannot_read_or_modify_draft(make_client, session_factory):
    admin, _, champ, pilot, race = scenario(make_client, session_factory)
    reviewing(admin, champ, race, pilot)
    judge = other_judge(make_client, session_factory)
    assert judge.get(base(champ, race) + "/draft").status_code == 409
    assert judge.put(base(champ, race) + "/draft", json=body(pilot, 0)).status_code == 409
    assert judge.post(base(champ, race) + "/counts/confirm", json=body(pilot, 0)).status_code == 409


def test_player_cannot_use_review_count_routes(make_client, session_factory):
    admin, player, champ, pilot, race = scenario(make_client, session_factory)
    reviewing(admin, champ, race, pilot)
    assert player.get(base(champ, race) + "/draft").status_code == 403
    assert player.put(base(champ, race) + "/draft", json=body(pilot, 0)).status_code == 403
    assert player.post(base(champ, race) + "/counts/confirm", json=body(pilot, 0)).status_code == 403


def test_duplicate_counts_are_rejected_without_saving(make_client, session_factory):
    admin, _, champ, pilot, race = scenario(make_client, session_factory)
    reviewing(admin, champ, race, pilot)
    data = body(pilot, 0)
    data["pilots"][0]["cards"].append({"card_name": CARD.lower(), "remaining": 1})
    assert admin.post(base(champ, race) + "/counts/confirm", json=data).status_code == 422
    assert admin.get(base(champ, race) + "/draft").json() is None
