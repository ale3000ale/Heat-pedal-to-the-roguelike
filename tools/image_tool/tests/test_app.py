import json
import tempfile
import unittest
from io import BytesIO
from pathlib import Path

from fastapi.testclient import TestClient
from PIL import Image

from tools.image_tool.app import create_app


def image_bytes(size=(2000, 1000), fmt="JPEG"):
    buffer = BytesIO()
    Image.new("RGB", size, "blue").save(buffer, fmt)
    return buffer.getvalue()


class AppTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        root = Path(self.temp.name)
        self.media = root / "media"
        (self.media / "board" / "events").mkdir(parents=True)
        (self.media / "board" / "maps").mkdir()
        (self.media / "cards").mkdir()
        (self.media / "board" / "maps" / "ITALIA.webp").write_bytes(b"mappa")
        (self.media / "board" / "maps" / "FRANCE.webp").write_bytes(b"francia")
        (self.media / "board" / "maps" / "DEUTSCHLAND.webp").write_bytes(b"germania")
        (self.media / "board" / "events" / "EVENTO.webp").write_bytes(b"evento")
        self.json_dir = root / "json"
        self.staging = root / "staging"
        self.state = root / "state.json"
        self.app = create_app(self.media, self.json_dir, self.staging, self.state)
        self.client = TestClient(self.app)
        self.client.__enter__()
        self.addCleanup(self.client.__exit__, None, None, None)

    def upload(self, name="mappa.jpg", size=(2000, 1000)):
        return self.client.post(
            "/api/upload",
            files=[("files", (name, image_bytes(size), "image/jpeg"))],
        )

    def upload_one(self, name="mappa.jpg", size=(2000, 1000)):
        response = self.upload(name, size)
        self.assertEqual(response.status_code, 200, response.text)
        data = response.json()
        self.assertEqual(data["errors"], [])
        self.assertEqual(len(data["items"]), 1)
        return data["items"][0]

    def save(self, item, destination="board/maps", name=""):
        return self.client.post(
            "/api/save",
            json={"destination": destination, "items": [{"id": item["id"], "name": name}]},
        )

    def map_payload(self, **overrides):
        payload = {
            "nome": "Italia",
            "image": "board/maps/ITALIA.webp",
            "giri": 3,
            "curve": 12,
            "caselle": 42,
            "sezioni": [1, 2],
        }
        payload.update(overrides)
        return payload

    def test_page_and_destinations(self):
        page = self.client.get("/")
        self.assertEqual(page.status_code, 200)
        self.assertIn("Strumento di sviluppo", page.text)
        self.assertIn("Media", page.text)
        self.assertIn("Mappe", page.text)
        self.assertIn("Eventi", page.text)
        data = self.client.get("/api/destinations").json()
        self.assertIn("board/events", data["destinations"])
        self.assertIn("board/maps", data["destinations"])
        self.assertEqual(data["default"], "board/events")

    def test_media_root_is_served_and_browsed(self):
        data = self.client.get("/api/media/browse").json()
        self.assertEqual(data["path"], "")
        self.assertIsNone(data["parent"])
        self.assertEqual(
            [entry["path"] for entry in data["directories"]], ["board", "cards"]
        )
        self.assertEqual(data["images"], [])
        response = self.client.get("/media/board/maps/ITALIA.webp")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, b"mappa")

    def test_media_browse_shows_only_the_current_folder(self):
        board = self.client.get("/api/media/browse", params={"path": "board"}).json()
        self.assertEqual(board["path"], "board")
        self.assertEqual(board["parent"], "")
        self.assertEqual(
            [entry["path"] for entry in board["directories"]],
            ["board/events", "board/maps"],
        )
        self.assertEqual(board["images"], [])

        maps = self.client.get("/api/media/browse", params={"path": "board/maps"}).json()
        self.assertEqual(maps["path"], "board/maps")
        self.assertEqual(maps["parent"], "board")
        self.assertEqual(maps["directories"], [])
        self.assertEqual(
            [entry["path"] for entry in maps["images"]],
            [
                "board/maps/DEUTSCHLAND.webp",
                "board/maps/FRANCE.webp",
                "board/maps/ITALIA.webp",
            ],
        )

        back = self.client.get("/api/media/browse", params={"path": board["parent"]}).json()
        self.assertEqual(back["path"], "")

    def test_media_browse_rejects_paths_outside_media(self):
        values = (
            "..",
            "../",
            "board/../cards",
            "/etc",
            str(self.media / "board"),
            "board/maps/ITALIA.webp",
            "board/mancante",
            ".nascosta",
        )
        for value in values:
            with self.subTest(value=value):
                response = self.client.get("/api/media/browse", params={"path": value})
                self.assertIn(response.status_code, (400, 404), response.text)

    def test_media_browse_ignores_hidden_entries(self):
        (self.media / ".segreto.webp").write_bytes(b"segreto")
        (self.media / ".nascosta").mkdir()
        data = self.client.get("/api/media/browse").json()
        self.assertNotIn(".segreto.webp", [entry["name"] for entry in data["images"]])
        self.assertNotIn(".nascosta", [entry["name"] for entry in data["directories"]])

    def test_media_browser_script_and_preview_are_wired(self):
        page = self.client.get("/")
        for marker in (
            'id="edit-preview"',
            'id="media-up"',
            'id="media-crumb"',
            'id="media-folders"',
            'id="media-grid"',
        ):
            with self.subTest(marker=marker):
                self.assertIn(marker, page.text)
        script = (
            Path(__file__).resolve().parents[1] / "static" / "app.js"
        ).read_text(encoding="utf-8")
        self.assertIn("/api/media/browse", script)
        self.assertNotIn("/api/media/images", script)
        self.assertIn("/api/media/last-folder", script)
        self.assertIn("showPreview(item.image || '')", script)

    def test_json_editor_marks_errors_and_sections_without_steppers(self):
        script = (
            Path(__file__).resolve().parents[1] / "static" / "app.js"
        ).read_text(encoding="utf-8")
        css = (
            Path(__file__).resolve().parents[1] / "static" / "style.css"
        ).read_text(encoding="utf-8")
        for marker in (
            'className = \'card-alert\'',
            'type: \'sections\'',
            'Numero sezioni',
            'className = \'field\'',
            'classList.add(\'invalid\')',
            'data-role="count"',
            "dataset.role = 'items'",
        ):
            with self.subTest(marker=marker):
                self.assertIn(marker, script)
        self.assertNotIn('number-stepper', script)
        self.assertNotIn("'+1'", script)
        self.assertNotIn("'−1'", script)
        for marker in ('.card-alert', '.field.invalid', 'input[type="number"]'):
            with self.subTest(marker=marker):
                self.assertIn(marker, css)
        self.assertNotIn('.number-stepper', css)

    def test_last_folder_is_saved_separately_for_each_json(self):
        maps = self.client.post(
            "/api/media/last-folder", json={"kind": "maps", "path": "board/maps"}
        )
        self.assertEqual(maps.status_code, 200, maps.text)
        self.assertEqual(maps.json()["path"], "board/maps")
        self.assertEqual(
            self.client.get("/api/media/last-folder", params={"kind": "maps"}).json()["path"],
            "board/maps",
        )
        self.assertEqual(
            self.client.get("/api/media/last-folder", params={"kind": "events"}).json()[
                "path"
            ],
            "",
        )
        expected = {"maps": "board/maps"}
        self.assertEqual(
            json.loads(self.state.read_text(encoding="utf-8")), expected
        )

        events = self.client.post(
            "/api/media/last-folder", json={"kind": "events", "path": "board/events"}
        )
        self.assertEqual(events.status_code, 200, events.text)
        self.assertEqual(
            json.loads(self.state.read_text(encoding="utf-8")),
            {"maps": "board/maps", "events": "board/events"},
        )

    def test_last_folder_survives_an_app_restart(self):
        self.client.post(
            "/api/media/last-folder", json={"kind": "maps", "path": "board/maps"}
        )
        self.client.post(
            "/api/media/last-folder", json={"kind": "events", "path": "board/events"}
        )
        restarted = create_app(self.media, self.json_dir, self.staging, self.state)
        with TestClient(restarted) as client:
            self.assertEqual(
                client.get("/api/media/last-folder", params={"kind": "maps"}).json()[
                    "path"
                ],
                "board/maps",
            )
            self.assertEqual(
                client.get("/api/media/last-folder", params={"kind": "events"}).json()[
                    "path"
                ],
                "board/events",
            )

    def test_missing_last_folder_falls_back_to_root(self):
        response = self.client.post(
            "/api/media/last-folder", json={"kind": "maps", "path": "board/maps"}
        )
        self.assertEqual(response.status_code, 200, response.text)
        (self.media / "board" / "maps").rename(self.media / "board" / "mappe")
        self.assertEqual(
            self.client.get("/api/media/last-folder", params={"kind": "maps"}).json()[
                "path"
            ],
            "",
        )

    def test_last_folder_rejects_invalid_input(self):
        for kind in ("unknown", ""):
            with self.subTest(kind=kind):
                response = self.client.get(
                    "/api/media/last-folder", params={"kind": kind}
                )
                self.assertEqual(response.status_code, 400)
        for path in ("../", "/tmp", "board/maps/ITALIA.webp", "board/mancante"):
            with self.subTest(path=path):
                response = self.client.post(
                    "/api/media/last-folder", json={"kind": "maps", "path": path}
                )
                self.assertIn(response.status_code, (400, 404), response.text)
        response = self.client.post(
            "/api/media/last-folder", json={"kind": "unknown", "path": "board/maps"}
        )
        self.assertEqual(response.status_code, 400)
        self.assertFalse(self.state.exists())

    def test_upload_converts_and_previews_webp(self):
        item = self.upload_one()
        self.assertEqual((item["width"], item["height"]), (560, 280))
        self.assertEqual(item["suggested"], "mappa")
        preview = self.client.get(item["preview_url"])
        self.assertEqual(preview.status_code, 200)
        self.assertEqual(preview.headers["content-type"], "image/webp")
        self.assertEqual(preview.content[:4], b"RIFF")
        self.assertEqual(preview.content[8:12], b"WEBP")

    def test_save_uses_the_original_name_on_empty_answer(self):
        item = self.upload_one()
        response = self.save(item)
        self.assertEqual(response.status_code, 200, response.text)
        data = response.json()
        self.assertEqual(data["errors"], [])
        self.assertEqual(data["saved"][0]["file"], "mappa.webp")
        target = self.media / "board" / "maps" / "mappa.webp"
        self.assertTrue(target.is_file())
        with Image.open(target) as image:
            self.assertEqual(image.format, "WEBP")
            self.assertEqual(image.size, (560, 280))

    def test_suggested_name_keeps_the_uploaded_name(self):
        item = self.upload_one(name="Mappa Sud.jpg")
        self.assertEqual(item["suggested"], "Mappa Sud")
        response = self.save(item)
        self.assertEqual(response.status_code, 200, response.text)
        self.assertTrue((self.media / "board" / "maps" / "mappa-sud.webp").is_file())

    def test_save_renames_and_slugifies(self):
        item = self.upload_one()
        response = self.save(item, name="Gran Premio d'Italia")
        self.assertEqual(response.status_code, 200, response.text)
        self.assertTrue((self.media / "board" / "maps" / "gran-premio-d-italia.webp").is_file())

    def test_existing_files_are_not_overwritten(self):
        target = self.media / "board" / "maps" / "mappa.webp"
        target.write_bytes(b"esistente")
        item = self.upload_one()
        response = self.save(item, name="mappa")
        self.assertEqual(response.status_code, 200, response.text)
        self.assertEqual(response.json()["saved"][0]["file"], "mappa-2.webp")
        self.assertEqual(target.read_bytes(), b"esistente")

    def test_invalid_destination_is_rejected(self):
        item = self.upload_one()
        response = self.save(item, destination="../cards")
        self.assertEqual(response.status_code, 400)

    def test_invalid_file_is_reported(self):
        response = self.client.post(
            "/api/upload",
            files=[("files", ("rotto.jpg", b"non sono un'immagine", "image/jpeg"))],
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["items"], [])
        self.assertEqual(data["errors"][0]["filename"], "rotto.jpg")

    def test_discard_removes_the_staged_preview(self):
        item = self.upload_one()
        response = self.client.delete(f"/api/staged/{item['id']}")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.client.get(item["preview_url"]).status_code, 404)

    def test_unknown_id_is_reported_on_save(self):
        response = self.client.post(
            "/api/save",
            json={
                "destination": "board/maps",
                "items": [{"id": "0" * 32, "name": "mappa"}],
            },
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["saved"], [])
        self.assertEqual(len(data["errors"]), 1)

    def test_new_destination_folder_is_created(self):
        item = self.upload_one()
        response = self.save(item, destination="nuove/mappe", name="pista")
        self.assertEqual(response.status_code, 200, response.text)
        self.assertTrue((self.media / "nuove" / "mappe" / "pista.webp").is_file())

    def test_multiple_uploads_get_unique_names(self):
        response = self.client.post(
            "/api/upload",
            files=[
                ("files", ("mappa.jpg", image_bytes(), "image/jpeg")),
                ("files", ("mappa.jpg", image_bytes((1000, 1000)), "image/jpeg")),
            ],
        )
        self.assertEqual(response.status_code, 200, response.text)
        items = response.json()["items"]
        self.assertEqual(len(items), 2)
        save = self.client.post(
            "/api/save",
            json={
                "destination": "board/maps",
                "items": [{"id": item["id"], "name": "mappa"} for item in items],
            },
        )
        self.assertEqual(save.status_code, 200, save.text)
        self.assertEqual(
            [entry["file"] for entry in save.json()["saved"]],
            ["mappa.webp", "mappa-2.webp"],
        )

    def test_missing_json_is_created_on_read(self):
        response = self.client.get("/api/data/maps")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["items"], [])
        self.assertTrue(data["created"])
        path = self.json_dir / "maps.json"
        self.assertTrue(path.is_file())
        self.assertEqual(json.loads(path.read_text(encoding="utf-8")), [])

        again = self.client.get("/api/data/maps")
        self.assertEqual(again.status_code, 200)
        self.assertFalse(again.json()["created"])
        self.assertEqual(self.client.get("/api/data/unknown").status_code, 404)

    def test_opening_a_json_repairs_missing_and_invalid_fields(self):
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
        (self.json_dir / "maps.json").write_text(json.dumps(raw), encoding="utf-8")
        response = self.client.get("/api/data/maps")
        self.assertEqual(response.status_code, 200, response.text)
        data = response.json()
        self.assertTrue(data["repaired"])
        self.assertEqual(
            data["items"][0],
            {
                "id": 1,
                "nome": None,
                "image": None,
                "giri": None,
                "curve": None,
                "caselle": 42,
                "sezioni": None,
            },
        )
        stored = json.loads((self.json_dir / "maps.json").read_text(encoding="utf-8"))
        self.assertEqual(stored, data["items"])
        second = self.client.get("/api/data/maps")
        self.assertFalse(second.json()["repaired"])

    def test_opening_a_json_keeps_duplicates_for_the_ui_to_flag(self):
        raw = [
            self.map_payload(),
            self.map_payload(nome="ITALIA", image="board/maps/FRANCE.webp"),
        ]
        (self.json_dir / "maps.json").write_text(json.dumps(raw), encoding="utf-8")
        response = self.client.get("/api/data/maps")
        self.assertEqual(response.status_code, 200, response.text)
        data = response.json()
        self.assertEqual([item["nome"] for item in data["items"]], ["Italia", "ITALIA"])
        self.assertEqual([item["id"] for item in data["items"]], [1, 2])

    def test_create_and_update_data_persist_on_disk(self):
        response = self.client.post("/api/data/maps", json=self.map_payload())
        self.assertEqual(response.status_code, 200, response.text)
        self.assertEqual(len(response.json()["items"]), 1)
        self.assertEqual(response.json()["items"][0]["id"], 1)

        update = self.client.put(
            "/api/data/maps/0",
            json=self.map_payload(
                nome="Italia 2026", image="board/maps/FRANCE.webp", giri=4
            ),
        )
        self.assertEqual(update.status_code, 200, update.text)
        stored = json.loads((self.json_dir / "maps.json").read_text(encoding="utf-8"))
        self.assertEqual(len(stored), 1)
        self.assertEqual(stored[0]["id"], 1)
        self.assertEqual(stored[0]["nome"], "Italia 2026")
        self.assertEqual(stored[0]["image"], "board/maps/FRANCE.webp")
        self.assertEqual(stored[0]["giri"], 4)

    def test_ids_are_generated_incrementally_and_preserved(self):
        first = self.client.post("/api/data/maps", json=self.map_payload())
        second = self.client.post(
            "/api/data/maps",
            json=self.map_payload(nome="Francia", image="board/maps/FRANCE.webp"),
        )
        self.assertEqual(first.status_code, 200, first.text)
        self.assertEqual(second.status_code, 200, second.text)
        self.assertEqual([item["id"] for item in second.json()["items"]], [1, 2])

        update = self.client.put(
            "/api/data/maps/0",
            json=self.map_payload(
                nome="Italia 2026", image="board/maps/ITALIA.webp", giri=5
            ),
        )
        self.assertEqual(update.status_code, 200, update.text)
        self.assertEqual(update.json()["items"][0]["id"], 1)

        third = self.client.post(
            "/api/data/maps",
            json=self.map_payload(
                nome="Germania", image="board/maps/DEUTSCHLAND.webp"
            ),
        )
        self.assertEqual(third.status_code, 200, third.text)
        self.assertEqual([item["id"] for item in third.json()["items"]], [1, 2, 3])

    def test_client_supplied_id_is_ignored(self):
        response = self.client.post(
            "/api/data/maps", json=self.map_payload(id=999)
        )
        self.assertEqual(response.status_code, 200, response.text)
        self.assertEqual(response.json()["items"][0]["id"], 1)

    def test_events_endpoint_accepts_its_own_schema(self):
        payload = {
            "nome": "Affluenza record",
            "image": "board/events/EVENTO.webp",
            "effetto": "+1 sponsore",
            "sponsor": 2,
            "fotografi": "1",
        }
        response = self.client.post("/api/data/events", json=payload)
        self.assertEqual(response.status_code, 200, response.text)
        self.assertEqual(response.json()["items"][0]["id"], 1)
        self.assertEqual(response.json()["items"][0]["sponsor"], 2)

    def test_duplicate_name_or_image_is_rejected(self):
        self.assertEqual(
            self.client.post("/api/data/maps", json=self.map_payload()).status_code, 200
        )
        same_name = self.client.post(
            "/api/data/maps",
            json=self.map_payload(nome="ITALIA", image="board/maps/FRANCE.webp"),
        )
        self.assertEqual(same_name.status_code, 409)
        self.assertIn("errore elemento già esistente", same_name.text)

        same_image = self.client.post(
            "/api/data/maps",
            json=self.map_payload(nome="Francia", image="board/maps/italia.webp"),
        )
        self.assertEqual(same_image.status_code, 409)

    def test_bad_image_path_is_rejected(self):
        values = (
            "../ITALIA.webp",
            str(self.media / "board" / "maps" / "ITALIA.webp"),
            "board/maps/missing.webp",
            "board/maps/note.txt",
        )
        for value in values:
            with self.subTest(value=value):
                response = self.client.post(
                    "/api/data/maps", json=self.map_payload(image=value)
                )
                self.assertEqual(response.status_code, 400, response.text)

    def test_wrong_number_types_are_rejected(self):
        for value in (-1, "3", 1.5):
            with self.subTest(value=value):
                response = self.client.post(
                    "/api/data/maps", json=self.map_payload(giri=value)
                )
                self.assertEqual(response.status_code, 400, response.text)

    def test_corrupt_json_is_reported(self):
        (self.json_dir / "maps.json").write_text("{", encoding="utf-8")
        response = self.client.get("/api/data/maps")
        self.assertEqual(response.status_code, 500)
        self.assertIn("File JSON non valido", response.text)


if __name__ == "__main__":
    unittest.main()
