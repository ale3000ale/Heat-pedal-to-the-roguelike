from io import BytesIO

import pytest
from PIL import Image

from app.services.images import MAX_CARD_SIZE
from app.services.pack_images import (
    DEFAULT_FOLDER,
    MAX_UPLOAD_BYTES,
    UPLOAD_FOLDER,
    PackImageError,
    is_available_pack_image,
    list_pack_images,
    save_pack_image,
)


def make_image(size=(100, 100), fmt="PNG"):
    buffer = BytesIO()
    Image.new("RGB", size, "red").save(buffer, fmt)
    return buffer.getvalue()


def test_png_is_converted_to_webp(tmp_path):
    path = save_pack_image("Turbo Pack.png", make_image(), tmp_path)
    assert path == f"{UPLOAD_FOLDER}/turbo-pack.webp"
    with Image.open(tmp_path / path) as saved:
        assert saved.format == "WEBP"


def test_large_image_fits_the_card_box(tmp_path):
    path = save_pack_image("grande.jpg", make_image((2000, 3000), "JPEG"), tmp_path)
    with Image.open(tmp_path / path) as saved:
        assert saved.width <= MAX_CARD_SIZE[0]
        assert saved.height <= MAX_CARD_SIZE[1]


def test_same_name_gets_a_new_file(tmp_path):
    first = save_pack_image("turbo.png", make_image(), tmp_path)
    second = save_pack_image("turbo.png", make_image(), tmp_path)
    assert first != second
    assert (tmp_path / first).exists()
    assert (tmp_path / second).exists()


@pytest.mark.parametrize("filename", ["foto.gif", "foto.bmp", "foto", "foto.txt"])
def test_unsupported_format_is_rejected(tmp_path, filename):
    with pytest.raises(PackImageError):
        save_pack_image(filename, make_image(), tmp_path)


def test_empty_and_too_large_files_are_rejected(tmp_path):
    with pytest.raises(PackImageError):
        save_pack_image("vuoto.png", b"", tmp_path)
    with pytest.raises(PackImageError):
        save_pack_image("enorme.png", b"0" * (MAX_UPLOAD_BYTES + 1), tmp_path)


def test_corrupt_content_is_rejected(tmp_path):
    with pytest.raises(PackImageError):
        save_pack_image("rotta.png", b"non sono un'immagine", tmp_path)
    assert not (tmp_path / UPLOAD_FOLDER).exists() or not list((tmp_path / UPLOAD_FOLDER).iterdir())


def test_list_puts_default_first_and_ignores_other_files(tmp_path):
    (tmp_path / DEFAULT_FOLDER).mkdir()
    (tmp_path / DEFAULT_FOLDER / "base.webp").write_bytes(make_image())
    (tmp_path / DEFAULT_FOLDER / "note.txt").write_text("x")
    uploaded = save_pack_image("zeta.png", make_image(), tmp_path)
    assert list_pack_images(tmp_path) == [f"{DEFAULT_FOLDER}/base.webp", uploaded]


def test_list_is_empty_without_folders(tmp_path):
    assert list_pack_images(tmp_path) == []


def test_only_listed_images_are_available(tmp_path):
    uploaded = save_pack_image("turbo.png", make_image(), tmp_path)
    assert is_available_pack_image(uploaded, tmp_path)
    assert not is_available_pack_image("../turbo.webp", tmp_path)
    assert not is_available_pack_image(f"/{uploaded}", tmp_path)
    assert not is_available_pack_image(f"{UPLOAD_FOLDER}/inesistente.webp", tmp_path)
