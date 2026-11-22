import tempfile
import unittest
from io import BytesIO
from pathlib import Path

from PIL import Image

from tools.image_tool.conversion import (
    ImageToolError,
    fit_image,
    load_image,
    resolve_destination,
    slugify,
    unique_filename,
)


def image_bytes(size, fmt="JPEG"):
    buffer = BytesIO()
    Image.new("RGB", size, "blue").save(buffer, fmt)
    return buffer.getvalue()


class ConversionTests(unittest.TestCase):
    def test_landscape_keeps_its_orientation(self):
        fitted = fit_image(load_image(image_bytes((2000, 1000))))
        self.assertEqual(fitted.size, (560, 280))

    def test_portrait_keeps_its_orientation(self):
        fitted = fit_image(load_image(image_bytes((1000, 2000))))
        self.assertEqual(fitted.size, (435, 870))

    def test_small_image_is_not_enlarged(self):
        fitted = fit_image(load_image(image_bytes((100, 150))))
        self.assertEqual(fitted.size, (100, 150))

    def test_invalid_file_raises(self):
        with self.assertRaises(ImageToolError):
            load_image(b"non sono un'immagine")

    def test_slugify(self):
        self.assertEqual(slugify("Gran Premio d'Italia"), "gran-premio-d-italia")
        self.assertEqual(slugify("Velocità 1"), "velocita-1")
        self.assertEqual(slugify("  "), "immagine")

    def test_unique_filename_adds_suffix(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "mappa.webp").write_bytes(b"x")
            (root / "mappa-2.webp").write_bytes(b"x")
            self.assertEqual(unique_filename(root, "mappa"), "mappa-3.webp")

    def test_destination_accepts_subfolders(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "board"
            root.mkdir()
            self.assertEqual(
                resolve_destination(root, "events"), (root / "events").resolve()
            )
            self.assertEqual(
                resolve_destination(root, "maps/special"),
                (root / "maps" / "special").resolve(),
            )

    def test_destination_rejects_outside_paths(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "board"
            root.mkdir()
            values = ("../cards", str(Path(directory) / "outside"), "", ".")
            for value in values:
                with self.subTest(value=value), self.assertRaises(ImageToolError):
                    resolve_destination(root, value)


if __name__ == "__main__":
    unittest.main()
