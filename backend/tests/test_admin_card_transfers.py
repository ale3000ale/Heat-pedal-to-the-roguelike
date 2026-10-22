"""Test del dominio puro; nessun DB reale o applicazione HTTP avviata."""
import copy
import unittest

from app.services.admin_card_transfers import CardTransfer, CardTransferError, plan_transfers
from app.services.cards import CardEntry


class AdminCardTransfersTests(unittest.TestCase):
    def setUp(self):
        self.containers = {name: [] for name in (
            "game_deck", "modification_inventory", "sponsor_inventory",
            "modification_pool", "sponsor_pool",
        )}

    def card(self, copies=1, name="Turbo", path="cards/turbo.webp"):
        return CardEntry(name=name, path=path, copies=copies)

    def total(self, containers):
        return sum(card.copies for cards in containers.values() for card in cards)

    def test_five_directions(self):
        for source, target in (
            ("game_deck", "modification_pool"),
            ("modification_inventory", "modification_pool"),
            ("sponsor_inventory", "sponsor_pool"),
            ("modification_pool", "modification_inventory"),
            ("sponsor_pool", "sponsor_inventory"),
        ):
            with self.subTest(source=source):
                containers = {name: [] for name in self.containers}
                containers[source] = [self.card(2)]
                result = plan_transfers(containers, [CardTransfer(source, "cards/turbo.webp")])
                self.assertEqual(result[source][0].copies, 1)
                self.assertEqual(result[target][0].copies, 1)
                self.assertEqual(self.total(result), self.total(containers))
                self.assertEqual(result[target][0].path, "cards/turbo.webp")
                self.assertEqual(containers[source][0].copies, 2)

    def test_game_removal_does_not_subtract_inventory(self):
        self.containers["game_deck"] = [self.card(2)]
        self.containers["modification_inventory"] = [self.card(3)]
        result = plan_transfers(self.containers, [CardTransfer("game_deck", "cards/turbo.webp")])
        self.assertEqual(result["modification_inventory"][0].copies, 3)
        self.assertEqual(result["game_deck"][0].copies, 1)
        self.assertEqual(result["modification_pool"][0].copies, 1)

    def test_all_five_containers_are_independent(self):
        for name in self.containers:
            self.containers[name] = [self.card(2)]
        result = plan_transfers(self.containers, [CardTransfer("sponsor_pool", "cards/turbo.webp")])
        for name in ("game_deck", "modification_inventory", "modification_pool"):
            self.assertEqual(result[name][0].copies, 2)
        self.assertEqual(result["sponsor_pool"][0].copies, 1)
        self.assertEqual(result["sponsor_inventory"][0].copies, 3)
        self.assertEqual(self.total(result), 10)

    def test_pool_never_adds_to_game(self):
        self.containers["modification_pool"] = [self.card()]
        result = plan_transfers(self.containers, [CardTransfer("modification_pool", "cards/turbo.webp")])
        self.assertEqual(result["game_deck"], [])
        self.assertEqual(result["modification_pool"], [])
        self.assertEqual(result["modification_inventory"][0].copies, 1)

    def test_sponsor_never_adds_to_game(self):
        self.containers["sponsor_pool"] = [self.card()]
        result = plan_transfers(self.containers, [CardTransfer("sponsor_pool", "cards/turbo.webp")])
        self.assertEqual(result["game_deck"], [])
        self.assertEqual(result["sponsor_inventory"][0].copies, 1)

    def test_repeated_clicks_remove_last_row(self):
        self.containers["game_deck"] = [self.card(2)]
        result = plan_transfers(self.containers, [CardTransfer("game_deck", "cards/turbo.webp")] * 2)
        self.assertEqual(result["game_deck"], [])
        self.assertEqual(result["modification_pool"][0].copies, 2)

    def test_failed_later_click_does_not_mutate_inputs(self):
        self.containers["game_deck"] = [self.card()]
        before = copy.deepcopy(self.containers)
        with self.assertRaises(CardTransferError):
            plan_transfers(self.containers, [CardTransfer("game_deck", "cards/turbo.webp")] * 2)
        self.assertEqual(self.containers, before)

    def test_round_trip_keeps_quantities(self):
        self.containers["modification_inventory"] = [self.card(3)]
        result = plan_transfers(self.containers, [
            CardTransfer("modification_inventory", "cards/turbo.webp"),
            CardTransfer("modification_pool", "cards/turbo.webp"),
        ])
        self.assertEqual(result, self.containers)

    def test_empty_plan_returns_independent_models(self):
        self.containers["game_deck"] = [self.card()]
        result = plan_transfers(self.containers, [])
        result["game_deck"][0].copies = 2
        self.assertEqual(self.containers["game_deck"][0].copies, 1)

    def test_unknown_container_rejected(self):
        with self.assertRaises(CardTransferError):
            plan_transfers(self.containers, [CardTransfer("base_pool", "cards/turbo.webp")])

    def test_missing_container_rejected(self):
        del self.containers["sponsor_pool"]
        with self.assertRaises(CardTransferError):
            plan_transfers(self.containers, [])

    def test_extra_container_rejected(self):
        self.containers["base_pool"] = []
        with self.assertRaises(CardTransferError):
            plan_transfers(self.containers, [])

    def test_missing_card_rejected(self):
        with self.assertRaises(CardTransferError):
            plan_transfers(self.containers, [CardTransfer("game_deck", "cards/missing.webp")])

    def test_empty_path_rejected(self):
        with self.assertRaises(CardTransferError):
            plan_transfers(self.containers, [CardTransfer("game_deck", "")])

    def test_ambiguous_source_path_rejected(self):
        self.containers["game_deck"] = [self.card(), self.card(name="Altro")]
        with self.assertRaises(CardTransferError):
            plan_transfers(self.containers, [CardTransfer("game_deck", "cards/turbo.webp")])

    def test_duplicate_names_rejected(self):
        self.containers["game_deck"] = [self.card(), self.card(path="cards/other.webp")]
        with self.assertRaises(CardTransferError):
            plan_transfers(self.containers, [])

    def test_same_name_different_image_rejected(self):
        self.containers["game_deck"] = [self.card()]
        self.containers["modification_pool"] = [self.card(path="cards/other.webp")]
        before = copy.deepcopy(self.containers)
        with self.assertRaises(CardTransferError):
            plan_transfers(self.containers, [CardTransfer("game_deck", "cards/turbo.webp")])
        self.assertEqual(self.containers, before)

    def test_quantity_overflow_rejected_without_mutation(self):
        self.containers["game_deck"] = [self.card()]
        self.containers["modification_pool"] = [self.card(999)]
        before = copy.deepcopy(self.containers)
        with self.assertRaises(CardTransferError):
            plan_transfers(self.containers, [CardTransfer("game_deck", "cards/turbo.webp")])
        self.assertEqual(self.containers, before)

    def test_normalized_name_merges_without_changing_image(self):
        self.containers["game_deck"] = [self.card(name=" turbo ")]
        self.containers["modification_pool"] = [self.card(2)]
        result = plan_transfers(self.containers, [CardTransfer("game_deck", "cards/turbo.webp")])
        self.assertEqual(len(result["modification_pool"]), 1)
        self.assertEqual(result["modification_pool"][0].copies, 3)
        self.assertEqual(result["modification_pool"][0].name, "Turbo")
