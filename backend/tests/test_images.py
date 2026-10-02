import io

import pytest
from PIL import Image

from app.services.images import (
    MAX_CARD_SIZE,
    CardImageError,
    fit_card_image,
    load_image,
    save_card_image,
    slugify,
    unique_filename,
)


def png_bytes(width, height, mode="RGB"):
    # Immagine di prova in memoria.
    buffer = io.BytesIO()
    Image.new(mode, (width, height), "red").save(buffer, "PNG")
    return buffer.getvalue()


def test_slugify():
    assert slugify("Forza motrice") == "forza-motrice"
    assert slugify("Velocità 1") == "velocita-1"
    assert slugify("  Ruota da   bagnato! ") == "ruota-da-bagnato"
    assert slugify("???") == "carta"


def test_unique_filename_adds_suffix(tmp_path):
    (tmp_path / "freni.webp").write_bytes(b"x")
    assert unique_filename(tmp_path, "turbo") == "turbo.webp"
    assert unique_filename(tmp_path, "freni") == "freni-2.webp"
    (tmp_path / "freni-2.webp").write_bytes(b"x")
    assert unique_filename(tmp_path, "freni") == "freni-3.webp"


def test_large_image_is_reduced_keeping_proportions():
    result = fit_card_image(load_image(png_bytes(2800, 4350)))
    assert result.size[0] <= MAX_CARD_SIZE[0]
    assert result.size[1] <= MAX_CARD_SIZE[1]
    assert abs(result.size[0] / result.size[1] - 2800 / 4350) < 0.01


def test_wide_image_is_not_cropped():
    result = fit_card_image(load_image(png_bytes(1120, 560)))
    assert result.size == (560, 280)


def test_small_image_is_not_enlarged():
    result = fit_card_image(load_image(png_bytes(100, 150)))
    assert result.size == (100, 150)


def test_palette_image_is_converted():
    buffer = io.BytesIO()
    Image.new("P", (50, 50)).save(buffer, "PNG")
    assert fit_card_image(load_image(buffer.getvalue())).mode == "RGBA"


def test_invalid_file_is_rejected():
    with pytest.raises(CardImageError):
        load_image(b"non sono un'immagine")


def test_save_card_image_writes_webp_with_safe_name(tmp_path):
    first = save_card_image(png_bytes(1000, 1500), tmp_path, "Forza motrice")
    second = save_card_image(png_bytes(1000, 1500), tmp_path, "forza  Motrice")
    assert first == "forza-motrice.webp"
    assert second == "forza-motrice-2.webp"
    with Image.open(tmp_path / first) as saved:
        assert saved.format == "WEBP"
        assert saved.size[0] <= MAX_CARD_SIZE[0]
        assert saved.size[1] <= MAX_CARD_SIZE[1]