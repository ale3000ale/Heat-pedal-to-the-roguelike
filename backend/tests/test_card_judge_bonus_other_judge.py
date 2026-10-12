from tests.test_card_judge import (
    CARD,
    bonus,
    other_judge,
    reviewing,
    scenario,
    sponsor_inventory,
    sponsor_pool,
)


def test_another_judge_cannot_grant_a_bonus_during_someone_elses_review(
    make_client, session_factory
):
    admin, _, champ, pilot, race = scenario(make_client, session_factory)
    reviewing(admin, champ, race, pilot)
    judge = other_judge(make_client, session_factory)
    assert bonus(judge, champ, race, pilot).status_code == 409
    assert sponsor_inventory(session_factory, pilot) == {CARD: 2}
    assert sponsor_pool(session_factory, champ) == {CARD: 2}
