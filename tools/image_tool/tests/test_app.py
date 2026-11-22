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
        self.board = Path(self.temp.name) / "board"
        (self.board / "events").mkdir(parents=True)
        (self.board / "maps").mkdir()
        self.staging = Path(self.temp.name) / "staging"
        self.app = create_app(self.board, self.staging)
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

    def save(self, item, destination="maps", name=""):
        return self.client.post(
            "/api/save",
            json={"destination": destination, "items": [{"id": item["id"], "name": name}]},
        )

    def test_page_and_destinations(self):
        page = self.client.get("/")
        self.assertEqual(page.status_code, 200)
        self.assertIn("Immagini di mappe ed eventi", page.text)
        data = self.client.get("/api/destinations").json()
        self.assertIn("events", data["destinations"])
        self.assertIn("maps", data["destinations"])
        self.assertEqual(data["default"], "events")

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
        target = self.board / "maps" / "mappa.webp"
        self.assertTrue(target.is_file())
        with Image.open(target) as image:
            self.assertEqual(image.format, "WEBP")
            self.assertEqual(image.size, (560, 280))

    def test_suggested_name_keeps_the_uploaded_name(self):
        item = self.upload_one(name="Mappa Sud.jpg")
        self.assertEqual(item["suggested"], "Mappa Sud")
        response = self.save(item)
        self.assertEqual(response.status_code, 200, response.text)
        self.assertTrue((self.board / "maps" / "mappa-sud.webp").is_file())

    def test_save_renames_and_slugifies(self):
        item = self.upload_one()
        response = self.save(item, name="Gran Premio d'Italia")
        self.assertEqual(response.status_code, 200, response.text)
        self.assertTrue((self.board / "maps" / "gran-premio-d-italia.webp").is_file())

    def test_existing_files_are_not_overwritten(self):
        target = self.board / "maps" / "mappa.webp"
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
            json={"destination": "maps", "items": [{"id": "0" * 32, "name": "mappa"}]},
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["saved"], [])
        self.assertEqual(len(data["errors"]), 1)

    def test_new_destination_folder_is_created(self):
        item = self.upload_one()
        response = self.save(item, destination="nuove/mappe", name="pista")
        self.assertEqual(response.status_code, 200, response.text)
        self.assertTrue((self.board / "nuove" / "mappe" / "pista.webp").is_file())

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
                "destination": "maps",
                "items": [{"id": item["id"], "name": "mappa"} for item in items],
            },
        )
        self.assertEqual(save.status_code, 200, save.text)
        self.assertEqual(
            [entry["file"] for entry in save.json()["saved"]],
            ["mappa.webp", "mappa-2.webp"],
        )


if __name__ == "__main__":
    unittest.main()
