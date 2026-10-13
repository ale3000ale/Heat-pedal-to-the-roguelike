from tests.test_card_judge import (
    cancel,
    other_judge,
    play,
    reviewing,
    scenario,
    summary,
)
from tests.test_race_review import play_statuses


def test_another_judge_cannot_cancel_an_active_play_during_someone_elses_review(
    make_client, session_factory
):
    admin, player, champ, pilot, race = scenario(make_client, session_factory)
    assert play(player, champ, pilot).status_code == 201
    play_id = summary(admin, champ, race).json()[0]["plays"][0]["id"]
    reviewing(admin, champ, race, pilot)
    judge = other_judge(make_client, session_factory)
    assert cancel(judge, champ, race, play_id).status_code == 409
    assert play_statuses(session_factory) == ["giocata"]
