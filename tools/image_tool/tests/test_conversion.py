import tempfile
import unittest
from io import BytesIO
from pathlib import Path

from PIL import Image

from tools.image_tool.conversion import (
    ImageToolError,
    create_media_folder,
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

    def test_create_media_folder_normalizes_the_name(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "media"
            (root / "board").mkdir(parents=True)
            self.assertEqual(
                create_media_folder(root, "board", "Gran Premio d'Italia"),
                "board/gran-premio-d-italia",
            )
            self.assertTrue((root / "board" / "gran-premio-d-italia").is_dir())
            self.assertEqual(create_media_folder(root, "", "Nuove Mappe"), "nuove-mappe")
            self.assertTrue((root / "nuove-mappe").is_dir())

    def test_create_media_folder_rejects_unsafe_paths_and_names(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "media"
            (root / "board").mkdir(parents=True)
            parents = ("..", "../cards", "board/../cards", "/etc", str(root / "board"), ".nascosta")
            for parent in parents:
                with self.subTest(parent=parent), self.assertRaises(ImageToolError):
                    create_media_folder(root, parent, "nuova")
            names = (
                "",
                "..",
                "../cards",
                "board/mappe",
                "board\\mappe",
                ".nascosta",
                "C:maps",
                "/assoluta",
            )
            for name in names:
                with self.subTest(name=name), self.assertRaises(ImageToolError):
                    create_media_folder(root, "board", name)

    def test_create_media_folder_refuses_an_existing_name(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "media"
            root.mkdir()
            create_media_folder(root, "", "nuova")
            with self.assertRaises(ImageToolError):
                create_media_folder(root, "", "nuova")


if __name__ == "__main__":
    unittest.main()
