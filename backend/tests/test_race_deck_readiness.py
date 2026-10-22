"""Test puri della preparazione mazzi; non certificano avvio o concorrenza DB."""
import unittest

from app.services.cards import CardEntry, dump_cards
from app.services.race_deck_readiness import (
    GameDecksNotReadyError, PilotGameDeck, require_ready_game_decks, unready_game_decks,
)


def deck(copies, pilot_id=1, name="Anna"):
    cards = dump_cards([CardEntry(name="Turbo", path="cards/turbo.webp", copies=copies)]) if copies else "[]"
    return PilotGameDeck(pilot_id, name, cards)


class RaceDeckReadinessTests(unittest.TestCase):
    def test_fifteen_copies_of_one_card_is_ready(self):
        self.assertEqual(unready_game_decks([deck(15)]), ())
        self.assertIsNone(require_ready_game_decks([deck(15)]))

    def test_fifteen_distinct_cards_is_ready(self):
        raw = dump_cards([CardEntry(name=f"Carta {i}", path=f"cards/{i}.webp", copies=1) for i in range(15)])
        self.assertEqual(unready_game_decks([PilotGameDeck(1, "Anna", raw)]), ())

    def test_grouped_copies_are_summed(self):
        raw = dump_cards([CardEntry(name="Prima", path="cards/a.webp", copies=7),
                          CardEntry(name="Seconda", path="cards/b.webp", copies=8)])
        self.assertEqual(unready_game_decks([PilotGameDeck(1, "Anna", raw)]), ())

    def test_zero_under_and_over_are_not_ready(self):
        for copies in (0, 1, 12, 14, 16, 30):
            with self.subTest(copies=copies):
                row, = unready_game_decks([deck(copies)])
                self.assertEqual(row.count, copies)
                self.assertEqual(row.reason, "wrong_count")

    def test_all_unready_pilots_are_reported(self):
        rows = unready_game_decks([deck(14, 1, "Anna"), deck(15, 2, "Beppe"), deck(16, 3, "Carlo")])
        self.assertEqual([(r.pilot_id, r.pilot_name, r.count) for r in rows], [(1, "Anna", 14), (3, "Carlo", 16)])

    def test_none_and_empty_text_follow_existing_empty_deck_parser(self):
        for raw in (None, "", "[]"):
            with self.subTest(raw=raw):
                row, = unready_game_decks([PilotGameDeck(1, "Anna", raw)])
                self.assertEqual(row.count, 0)
                self.assertEqual(row.reason, "wrong_count")

    def test_invalid_json_is_not_counted_as_empty(self):
        row, = unready_game_decks([PilotGameDeck(1, "Anna", "not-json")])
        self.assertIsNone(row.count)
        self.assertEqual(row.reason, "invalid_cards")

    def test_duplicate_names_are_invalid_even_with_fifteen_copies(self):
        raw = '[{"name":"Turbo","path":"cards/a.webp","copies":7},{"name":" turbo ","path":"cards/b.webp","copies":8}]'
        row, = unready_game_decks([PilotGameDeck(1, "Anna", raw)])
        self.assertEqual(row.reason, "invalid_cards")

    def test_invalid_quantity_is_rejected(self):
        raw = '[{"name":"Turbo","path":"cards/a.webp","copies":0}]'
        row, = unready_game_decks([PilotGameDeck(1, "Anna", raw)])
        self.assertIsNone(row.count)
        self.assertEqual(row.reason, "invalid_cards")

    def test_generator_input_is_supported(self):
        rows = unready_game_decks(deck(n, n) for n in (14, 15, 16))
        self.assertEqual([r.count for r in rows], [14, 16])

    def test_empty_entrants_does_not_introduce_a_new_rule(self):
        self.assertEqual(unready_game_decks([]), ())
        self.assertIsNone(require_ready_game_decks([]))

    def test_error_preserves_all_failures_and_counts(self):
        with self.assertRaises(GameDecksNotReadyError) as caught:
            require_ready_game_decks([deck(14), PilotGameDeck(2, "Beppe", "invalid")])
        self.assertEqual(len(caught.exception.unready), 2)
        self.assertIn("Anna: 14/15", str(caught.exception))
        self.assertIn("Beppe: mazzo non valido", str(caught.exception))

    def test_inputs_unchanged_and_result_has_no_card_payload(self):
        original = deck(14)
        raw = original.cards
        row, = unready_game_decks([original])
        self.assertEqual(original.cards, raw)
        self.assertFalse(hasattr(row, "cards"))
        self.assertFalse(hasattr(row, "path"))
