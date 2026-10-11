import pytest
from pydantic import ValidationError

from app.db.models.shop import PackTemplate, ShopTemplate, ShopTemplatePack
from app.schemas.shop import PackData
from app.services.pack_images import DEFAULT_FOLDER, PackImageError
from app.services.pack_templates import (
    PackTemplateNotFoundError,
    create_pack_template,
    delete_pack_template,
    get_pack_template,
    list_pack_templates,
    update_pack_template,
)


@pytest.fixture
def media(tmp_path, monkeypatch):
    # Cartella media finta con una immagine predefinita e una caricata.
    (tmp_path / DEFAULT_FOLDER).mkdir()
    (tmp_path / DEFAULT_FOLDER / "base.webp").write_bytes(b"x")
    (tmp_path / "illustration").mkdir()
    (tmp_path / "illustration" / "turbo.webp").write_bytes(b"x")
    monkeypatch.setattr("app.services.pack_images.DEFAULT_MEDIA_DIR", tmp_path)
    return tmp_path


def values(**changes):
    data = {"name": "Base", "currency": "gold", "cost": 10}
    data.update(changes)
    return PackData(**data).model_dump()


def test_defaults_and_name_cleaning():
    data = PackData(name="  Pacchetto   Turbo ", currency="gold", cost=5)
    assert data.name == "Pacchetto Turbo"
    assert data.modifiche_count == 3
    assert data.sponsor_count == 0
    assert data.filter_enabled is False


@pytest.mark.parametrize(
    "changes",
    [
        {"cost": 0},
        {"cost": -3},
        {"currency": "euro"},
        {"name": "   "},
        {"modifiche_count": 0, "sponsor_count": 0},
        {"modifiche_count": -1},
        {"filter_enabled": True},
        {"filter_enabled": True, "filter_text": " , ,"},
    ],
)
def test_invalid_pack_data_is_rejected(changes):
    with pytest.raises(ValidationError):
        PackData(**{"name": "Base", "currency": "gold", "cost": 10, **changes})


def test_only_sponsor_cards_is_valid():
    data = PackData(name="Solo sponsor", currency="sponsor", cost=2, modifiche_count=0, sponsor_count=2)
    assert data.modifiche_count == 0


def test_filter_text_is_normalized():
    data = PackData(
        name="Freni", currency="gold", cost=4, filter_enabled=True, filter_text=" Freni ,  sport,, "
    )
    assert data.filter_text == "Freni, sport"


def test_create_uses_the_default_image(session_factory, media):
    with session_factory() as db:
        template = create_pack_template(db, values())
        assert template.image_path == f"{DEFAULT_FOLDER}/base.webp"
        assert get_pack_template(db, template.id).name == "Base"


def test_create_without_default_image_fails(session_factory, tmp_path, monkeypatch):
    monkeypatch.setattr("app.services.pack_images.DEFAULT_MEDIA_DIR", tmp_path)
    with session_factory() as db:
        with pytest.raises(PackImageError):
            create_pack_template(db, values())
        assert list_pack_templates(db) == []


def test_unknown_image_is_rejected(session_factory, media):
    with session_factory() as db:
        with pytest.raises(PackImageError):
            create_pack_template(db, values(image_path="illustration/non-esiste.webp"))
        with pytest.raises(PackImageError):
            create_pack_template(db, values(image_path="../base.webp"))


def test_list_is_alphabetical_ignoring_case(session_factory, media):
    with session_factory() as db:
        for name in ("zeta", "Alfa", "beta"):
            create_pack_template(db, values(name=name))
        assert [t.name for t in list_pack_templates(db)] == ["Alfa", "beta", "zeta"]


def test_update_changes_everything(session_factory, media):
    with session_factory() as db:
        template = create_pack_template(db, values())
        changed = update_pack_template(
            db,
            template.id,
            values(
                name="Nuovo",
                currency="sponsor",
                cost=7,
                image_path="illustration/turbo.webp",
                modifiche_count=1,
                sponsor_count=2,
            ),
        )
        assert changed.name == "Nuovo"
        assert changed.currency == "sponsor"
        assert changed.cost == 7
        assert changed.image_path == "illustration/turbo.webp"
        assert (changed.modifiche_count, changed.sponsor_count) == (1, 2)


def test_missing_template_raises(session_factory, media):
    with session_factory() as db:
        with pytest.raises(PackTemplateNotFoundError):
            get_pack_template(db, 999)
        with pytest.raises(PackTemplateNotFoundError):
            update_pack_template(db, 999, values())
        with pytest.raises(PackTemplateNotFoundError):
            delete_pack_template(db, 999)


def test_delete_removes_links_but_keeps_shop_templates(session_factory, media):
    with session_factory() as db:
        template = create_pack_template(db, values())
        other = create_pack_template(db, values(name="Altro"))
        shop = ShopTemplate(name="Negozio", name_key="negozio")
        db.add(shop)
        db.flush()
        db.add(ShopTemplatePack(shop_template_id=shop.id, pack_template_id=template.id))
        db.add(ShopTemplatePack(shop_template_id=shop.id, pack_template_id=other.id))
        db.commit()
        shop_id, template_id, other_id = shop.id, template.id, other.id

        delete_pack_template(db, template_id)

        assert db.get(PackTemplate, template_id) is None
        assert db.get(ShopTemplate, shop_id) is not None
        assert db.get(ShopTemplatePack, (shop_id, template_id)) is None
        assert db.get(ShopTemplatePack, (shop_id, other_id)) is not None
