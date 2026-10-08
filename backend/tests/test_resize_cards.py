from io import BytesIO

from PIL import Image

from app.scripts.resize_cards import process_folder
from app.services.images import MAX_CARD_SIZE


def write_image(path, size, fmt):
    path.parent.mkdir(parents=True, exist_ok=True)
    buffer = BytesIO()
    Image.new("RGB", size, "blue").save(buffer, fmt)
    path.write_bytes(buffer.getvalue())


def quiet(_message):
    pass


def test_big_png_becomes_webp_in_the_box_and_original_stays(tmp_path):
    write_image(tmp_path / "carta.png", (2000, 3000), "PNG")
    counts = process_folder(tmp_path, log=quiet)
    assert counts["sistemata"] == 1
    assert (tmp_path / "carta.png").exists()
    with Image.open(tmp_path / "carta.webp") as converted:
        assert converted.format == "WEBP"
        assert converted.width <= MAX_CARD_SIZE[0]
        assert converted.height <= MAX_CARD_SIZE[1]
    assert not list(tmp_path.glob("*.tmp"))


def test_small_jpg_is_converted_without_resizing(tmp_path):
    write_image(tmp_path / "piccola.jpg", (100, 150), "JPEG")
    process_folder(tmp_path, log=quiet)
    with Image.open(tmp_path / "piccola.webp") as converted:
        assert converted.size == (100, 150)


def test_second_run_changes_nothing(tmp_path):
    write_image(tmp_path / "carta.png", (2000, 3000), "PNG")
    process_folder(tmp_path, log=quiet)
    converted = (tmp_path / "carta.webp").read_bytes()
    counts = process_folder(tmp_path, log=quiet)
    assert counts == {"ok": 1, "sistemata": 0, "gia_convertita": 1, "non_valida": 0}
    assert (tmp_path / "carta.webp").read_bytes() == converted


def test_webp_inside_the_box_is_not_touched(tmp_path):
    write_image(tmp_path / "ok.webp", (300, 400), "WEBP")
    before = (tmp_path / "ok.webp").read_bytes()
    counts = process_folder(tmp_path, log=quiet)
    assert counts["ok"] == 1
    assert (tmp_path / "ok.webp").read_bytes() == before


def test_big_webp_is_resized_in_place(tmp_path):
    write_image(tmp_path / "grande.webp", (1500, 2000), "WEBP")
    counts = process_folder(tmp_path, log=quiet)
    assert counts["sistemata"] == 1
    with Image.open(tmp_path / "grande.webp") as resized:
        assert resized.width <= MAX_CARD_SIZE[0]
        assert resized.height <= MAX_CARD_SIZE[1]


def test_dry_run_writes_nothing(tmp_path):
    write_image(tmp_path / "carta.png", (2000, 3000), "PNG")
    counts = process_folder(tmp_path, dry_run=True, log=quiet)
    assert counts["sistemata"] == 1
    assert not (tmp_path / "carta.webp").exists()


def test_invalid_file_is_skipped_and_others_are_processed(tmp_path):
    (tmp_path / "rotta.png").write_bytes(b"non sono un'immagine")
    write_image(tmp_path / "buona.png", (100, 100), "PNG")
    counts = process_folder(tmp_path, log=quiet)
    assert counts["non_valida"] == 1
    assert counts["sistemata"] == 1
    assert (tmp_path / "buona.webp").exists()


def test_subfolders_and_other_files_are_handled(tmp_path):
    write_image(tmp_path / "illustration" / "turbo.png", (900, 1200), "PNG")
    (tmp_path / "nota.txt").write_text("x")
    counts = process_folder(tmp_path, log=quiet)
    assert counts["sistemata"] == 1
    assert (tmp_path / "illustration" / "turbo.webp").exists()


def test_missing_folder_gives_zero_counts(tmp_path):
    counts = process_folder(tmp_path / "inesistente", log=quiet)
    assert counts == {"ok": 0, "sistemata": 0, "gia_convertita": 0, "non_valida": 0}
