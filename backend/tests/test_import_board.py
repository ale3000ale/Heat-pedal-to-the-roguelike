from io import BytesIO

import pytest
from PIL import Image

from app.scripts.import_board import (
    collect_sources,
    import_images,
    resolve_destination,
)


def write_image(path, size, fmt="JPEG"):
    path.parent.mkdir(parents=True, exist_ok=True)
    buffer = BytesIO()
    Image.new("RGB", size, "blue").save(buffer, fmt)
    path.write_bytes(buffer.getvalue())


def quiet(_message):
    pass


def test_resolve_destination_accepts_board_subfolders(tmp_path):
    root = tmp_path / "board"
    assert resolve_destination("events", root) == (root / "events").resolve()
    assert resolve_destination("maps/special", root) == (root / "maps" / "special").resolve()


def test_resolve_destination_rejects_paths_outside_board(tmp_path):
    root = tmp_path / "board"
    with pytest.raises(ValueError):
        resolve_destination("../cards", root)
    with pytest.raises(ValueError):
        resolve_destination(str(tmp_path / "outside"), root)


def test_collect_sources_finds_images_in_folders(tmp_path):
    write_image(tmp_path / "in" / "a.jpg", (10, 10))
    (tmp_path / "in" / "nota.txt").write_text("x")
    assert collect_sources([tmp_path / "in"]) == [tmp_path / "in" / "a.jpg"]


def test_collect_sources_rejects_empty_folder(tmp_path):
    (tmp_path / "vuota").mkdir()
    with pytest.raises(ValueError):
        collect_sources([tmp_path / "vuota"])


def test_import_writes_webp_in_the_box_and_keeps_the_source(tmp_path):
    source = tmp_path / "src" / "mappa.jpg"
    write_image(source, (2000, 1000))
    destination = tmp_path / "board" / "maps"

    counts = import_images([source], destination, keep_name=True, preview=False, log=quiet)

    assert counts["salvate"] == 1
    assert source.exists()
    target = destination / "mappa.webp"
    with Image.open(target) as image:
        assert image.format == "WEBP"
        assert image.size == (560, 280)


def test_portrait_image_keeps_its_orientation(tmp_path):
    source = tmp_path / "src" / "verticale.jpg"
    write_image(source, (1000, 2000))
    destination = tmp_path / "board" / "events"

    import_images([source], destination, keep_name=True, preview=False, log=quiet)

    with Image.open(destination / "verticale.webp") as image:
        assert image.height == 870
        assert image.width <= 560
        assert abs(image.width / image.height - 0.5) < 0.01


def test_answer_renames_and_slugifies(tmp_path):
    source = tmp_path / "src" / "mappa.jpg"
    write_image(source, (100, 100))
    destination = tmp_path / "board" / "maps"

    import_images(
        [source],
        destination,
        preview=False,
        ask=lambda _prompt: "Gran Premio d'Italia",
        log=quiet,
    )

    assert (destination / "gran-premio-d-italia.webp").exists()


def test_empty_answer_keeps_the_original_name(tmp_path):
    source = tmp_path / "src" / "Mappa Sud.jpg"
    write_image(source, (100, 100))
    destination = tmp_path / "board" / "maps"

    import_images([source], destination, preview=False, ask=lambda _prompt: "", log=quiet)

    assert (destination / "mappa-sud.webp").exists()


def test_preview_receives_each_valid_source(tmp_path):
    source = tmp_path / "src" / "mappa.jpg"
    write_image(source, (100, 100))
    destination = tmp_path / "board" / "maps"
    seen = []

    import_images(
        [source],
        destination,
        keep_name=True,
        preview=True,
        show=seen.append,
        log=quiet,
    )

    assert seen == [source]


def test_remove_source_deletes_the_original_after_saving(tmp_path):
    source = tmp_path / "src" / "mappa.jpg"
    write_image(source, (100, 100))
    destination = tmp_path / "board" / "maps"

    counts = import_images(
        [source],
        destination,
        keep_name=True,
        preview=False,
        remove_source=True,
        log=quiet,
    )

    assert counts["rimosse"] == 1
    assert not source.exists()
    assert (destination / "mappa.webp").exists()


def test_dry_run_writes_nothing(tmp_path):
    source = tmp_path / "src" / "mappa.jpg"
    write_image(source, (100, 100))
    destination = tmp_path / "board" / "maps"

    counts = import_images(
        [source],
        destination,
        keep_name=True,
        preview=False,
        dry_run=True,
        remove_source=True,
        log=quiet,
    )

    assert counts == {"salvate": 1, "non_valide": 0, "errori": 0, "rimosse": 0}
    assert not destination.exists()
    assert source.exists()


def test_invalid_file_is_skipped(tmp_path):
    bad = tmp_path / "src" / "rotta.jpg"
    bad.parent.mkdir(parents=True)
    bad.write_bytes(b"non sono un'immagine")
    destination = tmp_path / "board" / "maps"

    counts = import_images([bad], destination, keep_name=True, preview=False, log=quiet)

    assert counts["non_valide"] == 1
    assert not destination.exists()


def test_duplicate_names_get_a_suffix(tmp_path):
    first = tmp_path / "a" / "mappa.jpg"
    second = tmp_path / "b" / "mappa.jpg"
    write_image(first, (100, 100))
    write_image(second, (100, 100))
    destination = tmp_path / "board" / "maps"

    import_images([first, second], destination, keep_name=True, preview=False, log=quiet)

    assert (destination / "mappa.webp").exists()
    assert (destination / "mappa-2.webp").exists()


def test_webp_in_the_destination_is_resized_in_place(tmp_path):
    destination = tmp_path / "board" / "maps"
    source = destination / "pista.webp"
    write_image(source, (1200, 600), "WEBP")

    counts = import_images([source], destination, keep_name=True, preview=False, log=quiet)

    assert counts["salvate"] == 1
    assert not (destination / "pista-2.webp").exists()
    with Image.open(destination / "pista.webp") as image:
        assert image.size == (560, 280)
