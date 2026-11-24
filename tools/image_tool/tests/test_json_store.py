import json
import tempfile
import unittest
from pathlib import Path

from tools.image_tool.json_store import (
    StoreError,
    file_path,
    find_duplicate,
    load_items,
    model_for,
    next_id,
    repair_items,
    save_items,
    validate_image_path,
    validate_item,
)


class JsonStoreTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        root = Path(self.temp.name)
        self.media = root / "media"
        (self.media / "board" / "maps").mkdir(parents=True)
        (self.media / "board" / "events").mkdir()
        (self.media / "board" / "maps" / "ITALIA.webp").write_bytes(b"mappa")
        (self.media / "board" / "maps" / "FRANCE.webp").write_bytes(b"francia")
        (self.media / "board" / "events" / "EVENTO.webp").write_bytes(b"evento")
        (self.media / "board" / "maps" / "note.txt").write_text("testo", encoding="utf-8")
        self.json_dir = root / "json"

    def map_payload(self, **overrides):
        payload = {
            "nome": "Italia",
            "image": "board/maps/ITALIA.webp",
            "giri": 3,
            "curve": 12,
            "caselle": 42,
            "stress": 2,
            "heat": 3,
            "sezioni": [1, 2],
        }
        payload.update(overrides)
        return payload

    def valid_item(self):
        return validate_item("maps", self.map_payload(), self.media, [])

    def test_next_id_is_incremental(self):
        self.assertEqual(next_id([]), 1)
        self.assertEqual(next_id([{"id": 1}, {"id": 3}]), 4)

    def test_validate_item_assigns_or_preserves_the_id(self):
        first = validate_item("maps", self.map_payload(), self.media, [])
        second = validate_item(
            "maps",
            self.map_payload(nome="Francia", image="board/maps/FRANCE.webp"),
            self.media,
            [first],
        )
        self.assertEqual(first["id"], 1)
        self.assertEqual(second["id"], 2)
        preserved = validate_item(
            "maps",
            self.map_payload(),
            self.media,
            [first],
            exclude_index=0,
            item_id=first["id"],
        )
        self.assertEqual(preserved["id"], 1)

    def test_payload_id_is_ignored(self):
        item = validate_item("maps", self.map_payload(id=999), self.media, [])
        self.assertEqual(item["id"], 1)

    def test_load_normalizes_missing_and_duplicate_ids(self):
        self.json_dir.mkdir(parents=True)
        raw = [
            {"nome": "Italia", "image": "board/maps/ITALIA.webp", "giri": 1, "curve": 2, "caselle": 3},
            {"nome": "Francia", "image": "board/maps/FRANCE.webp", "giri": 1, "curve": 2, "caselle": 3},
        ]
        path = file_path(self.json_dir, "maps")
        path.write_text(json.dumps(raw), encoding="utf-8")
        items = load_items(self.json_dir, "maps", self.media)
        self.assertEqual([item["id"] for item in items], [1, 2])

        raw[0]["id"] = 5
        raw[1]["id"] = 5
        path.write_text(json.dumps(raw), encoding="utf-8")
        items = load_items(self.json_dir, "maps", self.media)
        self.assertEqual([item["id"] for item in items], [5, 6])

    def test_missing_file_is_empty(self):
        self.assertEqual(load_items(self.json_dir, "events", self.media), [])
        self.assertEqual(load_items(self.json_dir, "maps", self.media), [])
        self.assertFalse(file_path(self.json_dir, "maps").exists())

    def test_load_repairs_missing_empty_and_invalid_fields(self):
        self.json_dir.mkdir(parents=True)
        raw = [
            {
                "id": None,
                "nome": "  ",
                "image": "board/maps/missing.webp",
                "giri": -1,
                "curve": "12",
                "caselle": 42,
                "extra": "da eliminare",
            }
        ]
        path = file_path(self.json_dir, "maps")
        path.write_text(json.dumps(raw), encoding="utf-8")
        items, changed = repair_items(self.json_dir, "maps", self.media)
        self.assertTrue(changed)
        self.assertEqual(
            items[0],
            {
                "id": 1,
                "nome": None,
                "image": None,
                "giri": None,
                "curve": None,
                "caselle": 42,
                "stress": None,
                "heat": None,
                "sezioni": None,
            },
        )
        self.assertEqual(json.loads(path.read_text(encoding="utf-8")), items)

        again, changed_again = repair_items(self.json_dir, "maps", self.media)
        self.assertFalse(changed_again)
        self.assertEqual(again, items)

    def test_load_repairs_only_invalid_sections(self):
        self.json_dir.mkdir(parents=True)
        first = self.map_payload(sezioni=[0, 3])
        second = self.map_payload(
            nome="Francia", image="board/maps/FRANCE.webp", sezioni=[1, "2"]
        )
        path = file_path(self.json_dir, "maps")
        path.write_text(json.dumps([first, second]), encoding="utf-8")
        items = load_items(self.json_dir, "maps", self.media)
        self.assertEqual(items[0]["sezioni"], [0, 3])
        self.assertIsNone(items[1]["sezioni"])

    def test_load_keeps_duplicate_values_for_the_ui_to_flag(self):
        self.json_dir.mkdir(parents=True)
        first = self.map_payload()
        second = self.map_payload(
            nome="ITALIA", image="board/maps/FRANCE.webp"
        )
        path = file_path(self.json_dir, "maps")
        path.write_text(json.dumps([first, second]), encoding="utf-8")
        items = load_items(self.json_dir, "maps", self.media)
        self.assertEqual([item["nome"] for item in items], ["Italia", "ITALIA"])

    def test_validate_item_requires_valid_sections(self):
        for value in (None, [-1], ["1"], 1.5):
            with self.subTest(value=value), self.assertRaises(StoreError):
                validate_item(
                    "maps", self.map_payload(sezioni=value), self.media, []
                )
        empty = validate_item("maps", self.map_payload(sezioni=[]), self.media, [])
        self.assertEqual(empty["sezioni"], [])

    def test_unknown_kind_is_rejected(self):
        with self.assertRaises(StoreError) as raised:
            model_for("piloti")
        self.assertEqual(raised.exception.status_code, 404)

    def test_save_and_load_roundtrip(self):
        item = self.valid_item()
        save_items(self.json_dir, "maps", [item])
        path = file_path(self.json_dir, "maps")
        self.assertTrue(path.is_file())
        self.assertEqual(list(self.json_dir.glob(".tmp-*")), [])
        raw = path.read_text(encoding="utf-8")
        self.assertIn("Italia", raw)
        self.assertEqual(load_items(self.json_dir, "maps", self.media), [item])

    def test_required_text_fields_cannot_be_blank(self):
        base = {
            "nome": "Evento",
            "image": "board/events/EVENTO.webp",
            "effetto": "+1 sponsor",
            "sponsor": 1,
            "fotografi": "1",
        }
        for field in ("nome", "effetto", "fotografi"):
            payload = dict(base)
            payload[field] = "  "
            with self.subTest(field=field), self.assertRaises(StoreError):
                validate_item("events", payload, self.media, [])

    def test_wrong_number_types_and_negative_values_are_rejected(self):
        cases = (
            ("giri", -1),
            ("giri", "3"),
            ("curve", 2.5),
            ("caselle", "42"),
            ("stress", -1),
            ("stress", "2"),
            ("heat", -1),
            ("heat", 2.5),
        )
        for field, value in cases:
            with self.subTest(field=field, value=value), self.assertRaises(StoreError):
                validate_item("maps", self.map_payload(**{field: value}), self.media, [])

    def test_stress_and_heat_are_preserved_and_required(self):
        item = self.valid_item()
        self.assertEqual((item["stress"], item["heat"]), (2, 3))
        for field in ("stress", "heat"):
            with self.subTest(field=field):
                payload = self.map_payload()
                del payload[field]
                with self.assertRaises(StoreError):
                    validate_item("maps", payload, self.media, [])

    def test_extra_fields_are_rejected(self):
        payload = self.map_payload(ignored=True)
        with self.assertRaises(StoreError):
            validate_item("maps", payload, self.media, [])

    def test_image_path_must_be_a_supported_file_inside_media(self):
        valid = validate_image_path("board\\maps\\ITALIA.webp", self.media)
        self.assertEqual(valid, "board/maps/ITALIA.webp")
        invalid = (
            "",
            "../ITALIA.webp",
            str(self.media / "board" / "maps" / "ITALIA.webp"),
            "board/maps/missing.webp",
            "board/maps/note.txt",
        )
        for value in invalid:
            with self.subTest(value=value), self.assertRaises(StoreError):
                validate_image_path(value, self.media)

    def test_find_duplicate_is_case_insensitive(self):
        item = self.valid_item()
        items = [item]
        self.assertEqual(
            find_duplicate(items, self.map_payload(nome="ITALIA", image="x")), "nome"
        )
        self.assertEqual(
            find_duplicate(
                items, self.map_payload(nome="Altro", image="BOARD/MAPS/italia.webp")
            ),
            "image",
        )
        self.assertIsNone(find_duplicate(items, item, exclude_index=0))

    def test_duplicate_on_save_raises_the_expected_message(self):
        item = self.valid_item()
        with self.assertRaises(StoreError) as raised:
            validate_item("maps", self.map_payload(), self.media, [item])
        self.assertEqual(str(raised.exception), "errore elemento già esistente")
        self.assertEqual(raised.exception.status_code, 409)

    def test_edit_can_keep_its_own_name_image_and_id(self):
        item = self.valid_item()
        updated = validate_item(
            "maps",
            self.map_payload(giri=4),
            self.media,
            [item],
            exclude_index=0,
            item_id=item["id"],
        )
        self.assertEqual(updated["giri"], 4)
        self.assertEqual(updated["id"], item["id"])

    def test_corrupt_or_non_list_json_is_reported(self):
        path = file_path(self.json_dir, "maps")
        self.json_dir.mkdir(parents=True)
        path.write_text("{", encoding="utf-8")
        with self.assertRaises(StoreError):
            load_items(self.json_dir, "maps", self.media)
        path.write_text('{"nome": "Italia"}', encoding="utf-8")
        with self.assertRaises(StoreError):
            load_items(self.json_dir, "maps", self.media)


if __name__ == "__main__":
    unittest.main()
