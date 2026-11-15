import io

import pytest
from PIL import Image

from app.config import CARD_IMAGE_SIZE
from app.db.models.deck import Deck, DeckPrototype
from app.services.cards import card_delete, card_upload
from app.services.championship import pools
from app.services.cards.card_delete import (
    CardNotDeletableError,
    CardNotFoundError,
    delete_uploaded_card,
    remove_orphan_uploads,
)
from app.services.cards.card_upload import CardNameTakenError, CardUploadError, upload_card
from app.services.cards.cards import CardEntry, dump_cards
from app.services.championship.pools import BASE_POOL_NAMES, get_base_pool, pool_cards


def image_bytes(fmt: str = "PNG", size: tuple[int, int] = CARD_IMAGE_SIZE) -> bytes:
    # Immagine di prova a tinta unita nel formato e nelle misure richiesti.
    buffer = io.BytesIO()
    Image.new("RGB", size, (200, 30, 30)).save(buffer, format=fmt)
    return buffer.getvalue()


@pytest.fixture()
def media(tmp_path, monkeypatch):
    # Cartella media temporanea al posto di backend/media, in tutti i moduli che la usano.
    for module in (pools, card_upload, card_delete):
        monkeypatch.setattr(module, "MEDIA_DIR", tmp_path)
    return tmp_path


@pytest.fixture()
def db(session_factory, media):
    # Sessione con le due pool di base vuote (modifiche e sponsor).
    with session_factory() as session:
        for kind, name in BASE_POOL_NAMES.items():
            session.add(DeckPrototype(name=name, kind=kind, base_cards=dump_cards([])))
        session.commit()
        yield session


def uploaded_file(media, kind: str, filename: str):
    return media / "cards" / "uploads" / kind / filename


@pytest.mark.parametrize("fmt", ["PNG", "JPEG", "WEBP"])
def test_upload_accepts_allowed_formats(db, media, fmt):
    entry = upload_card(db, "sponsor", "Ruota", 3, image_bytes(fmt))
    assert entry.path == "cards/uploads/sponsor/Ruota_3.webp"
    saved = uploaded_file(media, "sponsor", "Ruota_3.webp")
    with Image.open(saved) as image:
        assert image.format == "WEBP"
        assert image.size == CARD_IMAGE_SIZE


def test_upload_adds_card_to_base_pool(db, media):
    upload_card(db, "modifiche", "Ala", 2, image_bytes())
    cards = pool_cards(get_base_pool(db, "modifiche"))
    assert [(c.name, c.path, c.copies) for c in cards] == [
        ("Ala", "cards/uploads/modifiche/Ala_2.webp", 2)
    ]
    assert pool_cards(get_base_pool(db, "sponsor")) == []


def test_upload_rejects_wrong_size(db, media):
    with pytest.raises(CardUploadError):
        upload_card(db, "sponsor", "Ruota", 1, image_bytes(size=(100, 100)))
    assert not uploaded_file(media, "sponsor", "Ruota_1.webp").exists()


def test_upload_rejects_other_formats(db, media):
    with pytest.raises(CardUploadError):
        upload_card(db, "sponsor", "Ruota", 1, image_bytes("GIF"))


def test_upload_rejects_non_image(db, media):
    with pytest.raises(CardUploadError):
        upload_card(db, "sponsor", "Ruota", 1, b"non sono un'immagine")
    with pytest.raises(CardUploadError):
        upload_card(db, "sponsor", "Ruota", 1, b"")


def test_upload_rejects_big_file(db, media, monkeypatch):
    monkeypatch.setattr(card_upload, "MAX_CARD_UPLOAD_BYTES", 10)
    with pytest.raises(CardUploadError):
        upload_card(db, "sponsor", "Ruota", 1, image_bytes())


@pytest.mark.parametrize("name", ["", "   ", "a/b", "a\\b", ".nascosta", "x" * 65])
def test_upload_rejects_bad_names(db, media, name):
    with pytest.raises(CardUploadError):
        upload_card(db, "sponsor", name, 1, image_bytes())


def test_upload_rejects_bad_kind_and_copies(db, media):
    with pytest.raises(CardUploadError):
        upload_card(db, "altro", "Ruota", 1, image_bytes())
    for copies in (0, 1000):
        with pytest.raises(CardUploadError):
            upload_card(db, "sponsor", "Ruota", copies, image_bytes())


def test_upload_rejects_duplicate_name_ignoring_case(db, media):
    upload_card(db, "sponsor", "Ruota", 1, image_bytes())
    with pytest.raises(CardNameTakenError):
        upload_card(db, "sponsor", "  RUOTA ", 4, image_bytes())
    assert not uploaded_file(media, "sponsor", "RUOTA_4.webp").exists()
    assert len(pool_cards(get_base_pool(db, "sponsor"))) == 1


def test_upload_same_name_in_other_kind_is_allowed(db, media):
    upload_card(db, "sponsor", "Ruota", 1, image_bytes())
    upload_card(db, "modifiche", "Ruota", 1, image_bytes())


def test_upload_removes_file_when_database_fails(db, media, monkeypatch):
    def boom():
        raise RuntimeError("database non disponibile")

    monkeypatch.setattr(db, "commit", boom)
    with pytest.raises(RuntimeError):
        upload_card(db, "sponsor", "Ruota", 1, image_bytes())
    assert not uploaded_file(media, "sponsor", "Ruota_1.webp").exists()


def test_delete_removes_card_and_file(db, media):
    upload_card(db, "sponsor", "Ruota", 3, image_bytes())
    removed = delete_uploaded_card(db, "sponsor", "ruota")
    assert removed == ["cards/uploads/sponsor/Ruota_3.webp"]
    assert pool_cards(get_base_pool(db, "sponsor")) == []
    assert not uploaded_file(media, "sponsor", "Ruota_3.webp").exists()


def test_delete_unknown_card_and_kind(db, media):
    with pytest.raises(CardNotFoundError):
        delete_uploaded_card(db, "sponsor", "Fantasma")
    with pytest.raises(CardNotFoundError):
        delete_uploaded_card(db, "altro", "Ruota")


def test_delete_refuses_base_cards(db, media):
    base = get_base_pool(db, "sponsor")
    entry = CardEntry(name="Di base", path="cards/base/sponsor/Di base_1.webp", copies=1)
    base.base_cards = dump_cards([entry])
    db.commit()
    with pytest.raises(CardNotDeletableError):
        delete_uploaded_card(db, "sponsor", "Di base")
    assert len(pool_cards(get_base_pool(db, "sponsor"))) == 1


def test_delete_keeps_file_while_a_deck_uses_it(db, media):
    upload_card(db, "sponsor", "Ruota", 3, image_bytes())
    path = "cards/uploads/sponsor/Ruota_3.webp"
    pool = get_base_pool(db, "sponsor")
    copy = Deck(
        cards=dump_cards([CardEntry(name="Ruota", path=path, copies=3)]),
        id_prototype=pool.id,
    )
    db.add(copy)
    db.commit()
    assert delete_uploaded_card(db, "sponsor", "Ruota") == []
    assert uploaded_file(media, "sponsor", "Ruota_3.webp").exists()
    db.delete(copy)
    db.commit()
    assert remove_orphan_uploads(db) == [path]
    assert not uploaded_file(media, "sponsor", "Ruota_3.webp").exists()


def test_orphan_cleanup_never_touches_base_files(db, media):
    base_file = media / "cards" / "base" / "sponsor" / "Intoccabile_1.webp"
    base_file.parent.mkdir(parents=True)
    base_file.write_bytes(b"x")
    assert remove_orphan_uploads(db) == []
    assert base_file.exists()


def test_orphan_cleanup_without_uploads_folder(db, media):
    assert remove_orphan_uploads(db) == []


def test_orphan_cleanup_stops_on_unreadable_deck(db, media):
    upload_card(db, "sponsor", "Ruota", 1, image_bytes())
    db.add(Deck(cards="non e' json", id_prototype=get_base_pool(db, "sponsor").id))
    db.commit()
    pool = get_base_pool(db, "sponsor")
    pool.base_cards = dump_cards([])
    db.commit()
    assert remove_orphan_uploads(db) == []
    assert uploaded_file(media, "sponsor", "Ruota_1.webp").exists()
