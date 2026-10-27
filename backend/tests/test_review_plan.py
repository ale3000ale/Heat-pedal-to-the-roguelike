import unittest
from copy import deepcopy

from app.services.race.review_plan import PoolStock, ReviewHolding, build_review_plan


class ReviewPlanTests(unittest.TestCase):
    def test_omitted_play_is_checked(self):
        plan = build_review_plan([ReviewHolding(1, "Alettone", 3, active=3)], [PoolStock("Alettone", 5, 7)], {})
        self.assertEqual(plan.pool_after["alettone"], 8)
        self.assertEqual(len(plan.issues), 1)

    def test_returns_and_withdrawals_are_netted(self):
        rows = [ReviewHolding(1, "Alettone", 1, consumed=1), ReviewHolding(2, "Alettone", 1, active=1)]
        plan = build_review_plan(rows, [PoolStock("Alettone", 0, 2)], {(1, "alettone"): 1})
        self.assertEqual(plan.pool_after["alettone"], 0)
        self.assertFalse(plan.issues)

    def test_gifts_are_in_total(self):
        plan = build_review_plan([ReviewHolding(1, "Freno", 2, active=2)], [PoolStock("Freno", 0, 2)], {})
        self.assertEqual(plan.targets[(1, "freno")], 0)
        self.assertEqual(plan.pool_after["freno"], 2)
        self.assertFalse(plan.issues)

    def test_correction_above_total_is_rejected(self):
        plan = build_review_plan([ReviewHolding(1, "Freno", 2)], [PoolStock("Freno", 0, 2)], {(1, "freno"): 3})
        self.assertEqual(len(plan.issues), 1)

    def test_unknown_card_is_rejected(self):
        self.assertTrue(build_review_plan([], [], {(1, "casco"): 0}).issues)

    def test_insufficient_pool_is_rejected(self):
        plan = build_review_plan([ReviewHolding(1, "Freno", 1, consumed=1)], [PoolStock("Freno", 0, 1)], {(1, "freno"): 1})
        self.assertEqual(plan.pool_after["freno"], -1)
        self.assertTrue(plan.issues)

    def test_inputs_are_not_modified(self):
        rows = [ReviewHolding(1, "Casco", 1)]
        stocks = [PoolStock("Casco", 0, 1)]
        counts = {(1, "casco"): 0}
        before = deepcopy((rows, stocks, counts))
        build_review_plan(rows, stocks, counts)
        self.assertEqual((rows, stocks, counts), before)

    def test_corrupt_active_count_is_not_clamped(self):
        plan = build_review_plan([ReviewHolding(1, "Casco", 1, active=2)], [PoolStock("Casco", 0, 2)], {})
        self.assertTrue(plan.issues)

    def test_duplicate_inventory_is_rejected(self):
        with self.assertRaises(ValueError):
            build_review_plan([ReviewHolding(1, "Casco", 1), ReviewHolding(1, " CASCO ", 1)], [], {})

    def test_missing_zero_stock_is_rejected(self):
        self.assertTrue(build_review_plan([ReviewHolding(1, "Casco", 1, active=1)], [], {}).issues)
