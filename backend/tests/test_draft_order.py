"""Test delle regole pure: nessuna dipendenza da database o autenticazione."""
import pytest

from app.services.cards import CardEntry
from app.services.draft_order import draft_order, has_draft_copies


def test_inverse_finish_excludes_absent_and_appends_newcomers():
    present = [1, 3, 4, 5]
    previous = [1, 2, 3]
    assert draft_order(present, previous, shuffle=list.reverse) == [3, 1, 5, 4]
    assert present == [1, 3, 4, 5]
    assert previous == [1, 2, 3]


def test_first_race_shuffles_all_present():
    assert draft_order([1, 2, 3], None, shuffle=list.reverse) == [3, 2, 1]


def test_no_previous_result_shuffles_all_present():
    assert draft_order([1, 2], [], shuffle=list.reverse) == [2, 1]


def test_previous_absentees_do_not_change_present_order():
    assert draft_order([1, 3], [1, 2, 3], shuffle=list.reverse) == [3, 1]


def test_default_shuffle_preserves_all_present():
    assert sorted(draft_order([1, 2, 3], None)) == [1, 2, 3]


@pytest.mark.parametrize(
    ("present", "previous"),
    [([1, 1], None), ([1], [2, 2]), ([0], None), ([True], None),
     ([1], [-1]), (["1"], None)],
)
def test_invalid_identifiers_are_rejected(present, previous):
    with pytest.raises(ValueError):
        draft_order(present, previous)


@pytest.mark.parametrize(("copies", "expected"), [(4, False), (5, True), (6, True)])
def test_pool_threshold_counts_copies_not_distinct_cards(copies, expected):
    pool = [CardEntry(name="Turbo", path="cards/turbo.webp", copies=copies)]
    assert has_draft_copies(pool, 2) is expected
    assert pool[0].copies == copies


def test_empty_pool_cannot_supply_draft():
    assert has_draft_copies([], 1) is False


@pytest.mark.parametrize("count", [0, -1, True, 1.5, "2"])
def test_invalid_present_count_is_rejected(count):
    with pytest.raises(ValueError):
        has_draft_copies([], count)
