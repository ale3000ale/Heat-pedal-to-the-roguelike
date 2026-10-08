import random

import pytest

from app.services.cards import CardEntry
from app.services.shop_draw import (
    PackSoldOutError,
    available_copies,
    draw_cards,
    is_sold_out,
    parse_filter,
)


def card(name, copies):
    return CardEntry(name=name, path=f"cards/{name}.webp", copies=copies)


class StubRng:
    # Restituisce valori prefissati e registra l'intervallo richiesto a ogni estrazione.
    def __init__(self, rolls):
        self.rolls = list(rolls)
        self.totals = []

    def randrange(self, total):
        self.totals.append(total)
        return self.rolls.pop(0)


def test_parse_filter_cleans_names():
    assert parse_filter(" Freni ,  SPORT,, ") == ["freni", "sport"]
    assert parse_filter(None) == []


def test_probability_is_per_copy_and_recalculated_after_each_draw():
    pool = [card("A", 3), card("B", 1), card("C", 6)]
    rng = StubRng([0, 3])
    drawn, new_pool = draw_cards(pool, 2, False, None, rng)
    assert rng.totals == [10, 9]
    assert [(c.name, c.copies) for c in drawn] == [("A", 1), ("B", 1)]
    assert {c.name: c.copies for c in new_pool} == {"A": 2, "C": 6}


def test_the_same_card_can_come_out_more_than_once():
    drawn, new_pool = draw_cards([card("A", 3)], 2, False, None, random.Random(1))
    assert [(c.name, c.copies) for c in drawn] == [("A", 2)]
    assert [(c.name, c.copies) for c in new_pool] == [("A", 1)]


def test_pool_given_is_not_modified():
    pool = [card("A", 2)]
    draw_cards(pool, 2, False, None, random.Random(1))
    assert pool[0].copies == 2


def test_drawing_everything_empties_the_pool():
    drawn, new_pool = draw_cards([card("A", 3), card("B", 1)], 4, False, None, random.Random(7))
    assert sum(c.copies for c in drawn) == 4
    assert new_pool == []


def test_filter_is_case_insensitive_and_by_name_part():
    pool = [card("Freni carbo ceramici", 3), card("Freni sport", 3), card("Carrozzeria", 9)]
    for seed in range(20):
        drawn, new_pool = draw_cards(pool, 4, True, "FRENI", random.Random(seed))
        assert {c.name for c in drawn} <= {"Freni carbo ceramici", "Freni sport"}
        assert {c.name: c.copies for c in new_pool}["Carrozzeria"] == 9


def test_filter_with_several_names():
    pool = [card("Freni sport", 2), card("Turbo", 2), card("Carrozzeria", 5)]
    assert available_copies(pool, True, "freni, turbo") == 4
    assert available_copies(pool, False, "freni") == 9


def test_not_enough_copies_after_the_filter_is_sold_out():
    pool = [card("Freni sport", 2), card("Carrozzeria", 9)]
    with pytest.raises(PackSoldOutError):
        draw_cards(pool, 3, True, "freni", random.Random(1))
    assert is_sold_out(3, 0, True, "freni", pool, []) is True
    assert is_sold_out(2, 0, True, "freni", pool, []) is False


def test_sold_out_checks_both_pools():
    modifiche, sponsor = [card("A", 5)], [card("S", 1)]
    assert is_sold_out(3, 2, False, None, modifiche, sponsor) is True
    assert is_sold_out(3, 1, False, None, modifiche, sponsor) is False
    assert is_sold_out(3, 1, False, None, modifiche, []) is True


def test_zero_count_draws_nothing():
    pool = [card("A", 2)]
    drawn, new_pool = draw_cards(pool, 0, False, None, random.Random(1))
    assert drawn == []
    assert [(c.name, c.copies) for c in new_pool] == [("A", 2)]
