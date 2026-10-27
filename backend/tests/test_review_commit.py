import pytest

from app.db.models import User
from app.db.models.race import Race
from app.schemas.race.review_counts import ReviewCountsRequest
from app.services.race.review_commit import commit_review_counts, ReviewPlanConflict, save_review_counts
from tests.test_card_judge import (
    CARD, play, reviewing, scenario, sponsor_inventory, sponsor_pool,
)
from tests.test_review_inventory import inventory, cards_of


def request(pilot, remaining):
    return ReviewCountsRequest.model_validate({"pilots": [{"pilot_id": pilot, "cards": [
        {"card_name": CARD, "remaining": remaining}
    ]}]})


def reviewer(db, race_id):
    return db.get(User, db.get(Race, race_id).review_started_by_user_id)


def test_commit_corrects_counts_once(make_client, session_factory):
    admin, player, champ, pilot, race = scenario(make_client, session_factory, copies=2)
    assert play(player, champ, pilot).status_code == 201
    reviewing(admin, champ, race, pilot)
    with session_factory() as db:
        row = commit_review_counts(db, champ, race, reviewer(db, race), request(pilot, 0))
        assert row.review_closed_at is not None
    assert sponsor_inventory(session_factory, pilot) == {}
    assert sponsor_pool(session_factory, champ) == {CARD: 4}


def test_conflict_keeps_inventory_and_saves_only_draft(make_client, session_factory):
    admin, _, champ, pilot, race = scenario(make_client, session_factory, copies=2)
    reviewing(admin, champ, race, pilot)
    with session_factory() as db:
        with pytest.raises(ReviewPlanConflict):
            commit_review_counts(db, champ, race, reviewer(db, race), request(pilot, 3))
    assert sponsor_inventory(session_factory, pilot) == {CARD: 2}
    assert sponsor_pool(session_factory, champ) == {CARD: 2}
    with session_factory() as db:
        row = db.get(Race, race)
        assert row.review_closed_at is None
        assert ReviewCountsRequest.model_validate_json(row.review_draft).to_counts() == {(pilot, CARD.casefold()): 3}


def test_saved_draft_does_not_move_cards(make_client, session_factory):
    admin, _, champ, pilot, race = scenario(make_client, session_factory, copies=2)
    reviewing(admin, champ, race, pilot)
    with session_factory() as db:
        save_review_counts(db, champ, race, reviewer(db, race), request(pilot, 0))
    assert sponsor_inventory(session_factory, pilot) == {CARD: 2}
    assert sponsor_pool(session_factory, champ) == {CARD: 2}


def test_reopened_review_restores_from_last_state(make_client, session_factory):
    admin, player, champ, pilot, race = scenario(make_client, session_factory, copies=2)
    assert play(player, champ, pilot).status_code == 201
    reviewing(admin, champ, race, pilot)
    with session_factory() as db:
        commit_review_counts(db, champ, race, reviewer(db, race), request(pilot, 0))
    assert admin.post(f"/api/championships/{champ}/races/{race}/review/reopen").status_code == 200
    assert cards_of(inventory(admin, champ, race))[0]["remaining"] == 0
    with session_factory() as db:
        commit_review_counts(db, champ, race, reviewer(db, race), request(pilot, 1))
    assert sponsor_inventory(session_factory, pilot) == {CARD: 1}
    assert sponsor_pool(session_factory, champ) == {CARD: 3}
