import pytest
from pydantic import ValidationError

from app.db.models.shop import PackTemplate, ShopTemplate, ShopTemplatePack
from app.schemas.shop import ShopTemplateData
from app.services.pack_images import DEFAULT_FOLDER
from app.services.pack_templates import (
    PackTemplateNotFoundError,
    create_pack_template,
    delete_pack_template,
)
from app.services.shop_templates import (
    DuplicatePackTemplateError,
    ShopTemplateEmptyError,
    ShopTemplateNameTakenError,
    ShopTemplateNotFoundError,
    create_shop_template,
    delete_shop_template,
    get_shop_template,
    list_shop_templates,
    update_shop_template,
)


@pytest.fixture
def media(tmp_path, monkeypatch):
    (tmp_path / DEFAULT_FOLDER).mkdir()
    (tmp_path / DEFAULT_FOLDER / "base.webp").write_bytes(b"x")
    monkeypatch.setattr("app.services.pack_images.DEFAULT_MEDIA_DIR", tmp_path)
    return tmp_path


def make_pack(db, name):
    values = {"name": name, "currency": "gold", "cost": 5, "modifiche_count": 3,
              "sponsor_count": 0, "filter_enabled": False, "filter_text": None}
    return create_pack_template(db, values).id


def test_name_is_cleaned_by_the_schema():
    assert ShopTemplateData(name="  Negozio   Base ").name == "Negozio Base"
    with pytest.raises(ValidationError):
        ShopTemplateData(name="a")


def test_create_links_the_pack_templates(session_factory, media):
    with session_factory() as db:
        first, second = make_pack(db, "Uno"), make_pack(db, "Due")
        info = create_shop_template(db, "Negozio", [second, first])
        assert info.name == "Negozio"
        assert info.pack_template_ids == sorted([first, second])
        assert info.is_empty is False
        assert get_shop_template(db, info.id).pack_template_ids == info.pack_template_ids


def test_create_without_pack_templates_fails(session_factory, media):
    with session_factory() as db:
        with pytest.raises(ShopTemplateEmptyError):
            create_shop_template(db, "Vuoto", [])
        assert list_shop_templates(db) == []


def test_duplicate_and_unknown_pack_templates_are_rejected(session_factory, media):
    with session_factory() as db:
        pack = make_pack(db, "Uno")
        with pytest.raises(DuplicatePackTemplateError):
            create_shop_template(db, "Doppio", [pack, pack])
        with pytest.raises(PackTemplateNotFoundError):
            create_shop_template(db, "Strano", [pack, 999])
        assert db.query(ShopTemplate).count() == 0
        assert db.query(ShopTemplatePack).count() == 0


def test_name_is_unique_ignoring_case(session_factory, media):
    with session_factory() as db:
        pack = make_pack(db, "Uno")
        create_shop_template(db, "Negozio", [pack])
        with pytest.raises(ShopTemplateNameTakenError):
            create_shop_template(db, "  NEGOZIO ", [pack])


def test_update_renames_and_replaces_packs(session_factory, media):
    with session_factory() as db:
        first, second = make_pack(db, "Uno"), make_pack(db, "Due")
        info = create_shop_template(db, "Negozio", [first])
        changed = update_shop_template(db, info.id, "NEGOZIO", [second])
        assert changed.name == "NEGOZIO"
        assert changed.pack_template_ids == [second]


def test_update_cannot_take_another_name(session_factory, media):
    with session_factory() as db:
        pack = make_pack(db, "Uno")
        create_shop_template(db, "Primo", [pack])
        other = create_shop_template(db, "Secondo", [pack])
        with pytest.raises(ShopTemplateNameTakenError):
            update_shop_template(db, other.id, "primo", [pack])


def test_update_missing_or_invalid(session_factory, media):
    with session_factory() as db:
        pack = make_pack(db, "Uno")
        info = create_shop_template(db, "Negozio", [pack])
        with pytest.raises(ShopTemplateNotFoundError):
            update_shop_template(db, 999, "Altro", [pack])
        with pytest.raises(DuplicatePackTemplateError):
            update_shop_template(db, info.id, "Negozio", [pack, pack])
        with pytest.raises(PackTemplateNotFoundError):
            update_shop_template(db, info.id, "Negozio", [999])
        assert get_shop_template(db, info.id).pack_template_ids == [pack]


def test_deleting_every_pack_template_leaves_an_empty_shop_template(session_factory, media):
    with session_factory() as db:
        pack = make_pack(db, "Uno")
        info = create_shop_template(db, "Negozio", [pack])
        delete_pack_template(db, pack)
        empty = get_shop_template(db, info.id)
        assert empty.is_empty is True
        assert empty.pack_template_ids == []
        new_pack = make_pack(db, "Nuovo")
        again = update_shop_template(db, info.id, "Negozio", [new_pack])
        assert again.is_empty is False


def test_delete_keeps_the_pack_templates(session_factory, media):
    with session_factory() as db:
        pack = make_pack(db, "Uno")
        info = create_shop_template(db, "Negozio", [pack])
        delete_shop_template(db, info.id)
        assert db.get(ShopTemplate, info.id) is None
        assert db.query(ShopTemplatePack).count() == 0
        assert db.get(PackTemplate, pack) is not None
        with pytest.raises(ShopTemplateNotFoundError):
            delete_shop_template(db, info.id)


def test_list_is_alphabetical_ignoring_case(session_factory, media):
    with session_factory() as db:
        pack = make_pack(db, "Uno")
        for name in ("zeta", "Alfa", "beta"):
            create_shop_template(db, name, [pack])
        assert [t.name for t in list_shop_templates(db)] == ["Alfa", "beta", "zeta"]
