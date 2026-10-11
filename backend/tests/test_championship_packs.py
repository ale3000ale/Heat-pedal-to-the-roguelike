import pytest

from app.db.models.championship import Championship
from app.db.models.shop import Pack, PackPurchase
from app.services.championships import (
    ChampionshipClosedError,
    ChampionshipNotFoundError,
    delete_championship,
)
from app.services.pack_images import DEFAULT_FOLDER, PackImageError
from app.services.pack_templates import create_pack_template, update_pack_template
from app.services.packs import (
    PackNotFoundError,
    create_pack,
    delete_pack,
    list_packs,
    update_pack,
)
from app.services.shop_copy import add_packs_from_templates, pack_templates_of
from app.services.shop_templates import (
    ShopTemplateEmptyError,
    ShopTemplateNotFoundError,
    create_shop_template,
    update_shop_template,
)


@pytest.fixture
def media(tmp_path, monkeypatch):
    (tmp_path / DEFAULT_FOLDER).mkdir()
    (tmp_path / DEFAULT_FOLDER / "base.webp").write_bytes(b"x")
    monkeypatch.setattr("app.services.pack_images.DEFAULT_MEDIA_DIR", tmp_path)
    return tmp_path


def values(**changes):
    data = {
        "name": "Base",
        "image_path": None,
        "currency": "gold",
        "cost": 5,
        "modifiche_count": 3,
        "sponsor_count": 0,
        "filter_enabled": False,
        "filter_text": None,
    }
    data.update(changes)
    return data


def make_championship(db, name="Camp", closed=False):
    championship = Championship(name=name, name_key=name.lower(), is_closed=closed)
    db.add(championship)
    db.commit()
    return championship.id


def test_shop_template_packs_are_copied_independently(session_factory, media):
    with session_factory() as db:
        template = create_pack_template(db, values(name="Turbo", cost=9, sponsor_count=1))
        shop = create_shop_template(db, "Negozio", [template.id])
        championship_id = make_championship(db)
        add_packs_from_templates(db, championship_id, pack_templates_of(db, shop.id))
        db.commit()

        packs = list_packs(db, championship_id)
        assert [(p.name, p.cost, p.sponsor_count) for p in packs] == [("Turbo", 9, 1)]

        update_pack_template(db, template.id, values(name="Cambiato", cost=1))
        assert list_packs(db, championship_id)[0].name == "Turbo"
        assert list_packs(db, championship_id)[0].cost == 9


def test_empty_or_missing_shop_template_is_not_usable(session_factory, media):
    with session_factory() as db:
        template = create_pack_template(db, values())
        shop = create_shop_template(db, "Negozio", [template.id])
        update_shop_template(db, shop.id, "Negozio", [])
        with pytest.raises(ShopTemplateEmptyError):
            pack_templates_of(db, shop.id)
        with pytest.raises(ShopTemplateNotFoundError):
            pack_templates_of(db, 999)


def test_new_championship_has_an_empty_shop(session_factory, media):
    with session_factory() as db:
        assert list_packs(db, make_championship(db)) == []


def test_create_pack_uses_default_image_and_lists_alphabetically(session_factory, media):
    with session_factory() as db:
        championship_id = make_championship(db)
        for name in ("zeta", "Alfa"):
            create_pack(db, championship_id, values(name=name))
        packs = list_packs(db, championship_id)
        assert [p.name for p in packs] == ["Alfa", "zeta"]
        assert packs[0].image_path == f"{DEFAULT_FOLDER}/base.webp"


def test_pack_rules_on_missing_or_closed_championship(session_factory, media):
    with session_factory() as db:
        closed_id = make_championship(db, "Chiuso", closed=True)
        with pytest.raises(ChampionshipNotFoundError):
            create_pack(db, 999, values())
        with pytest.raises(ChampionshipNotFoundError):
            list_packs(db, 999)
        with pytest.raises(ChampionshipClosedError):
            create_pack(db, closed_id, values())
        assert list_packs(db, closed_id) == []


def test_unknown_image_is_rejected(session_factory, media):
    with session_factory() as db:
        championship_id = make_championship(db)
        with pytest.raises(PackImageError):
            create_pack(db, championship_id, values(image_path="illustration/no.webp"))
        assert list_packs(db, championship_id) == []


def test_update_pack_and_wrong_championship(session_factory, media):
    with session_factory() as db:
        first = make_championship(db, "Uno")
        second = make_championship(db, "Due")
        pack = create_pack(db, first, values())
        changed = update_pack(db, first, pack.id, values(name="Nuovo", cost=20))
        assert (changed.name, changed.cost) == ("Nuovo", 20)
        with pytest.raises(PackNotFoundError):
            update_pack(db, second, pack.id, values())
        with pytest.raises(PackNotFoundError):
            delete_pack(db, second, pack.id)
        with pytest.raises(PackNotFoundError):
            update_pack(db, first, 999, values())


def test_delete_pack_keeps_the_purchase_history(session_factory, media):
    with session_factory() as db:
        championship_id = make_championship(db)
        pack = create_pack(db, championship_id, values())
        db.add(
            PackPurchase(
                championship_id=championship_id,
                pack_id=pack.id,
                pilot_name="Pilota",
                pack_name="Base",
                currency="gold",
                cost=5,
            )
        )
        db.commit()
        delete_pack(db, championship_id, pack.id)
        purchase = db.query(PackPurchase).one()
        assert purchase.pack_id is None
        assert purchase.pack_name == "Base"
        assert db.query(Pack).count() == 0


def test_deleting_a_championship_removes_packs_and_purchases(session_factory, media):
    with session_factory() as db:
        target = make_championship(db, "Da cancellare")
        other = make_championship(db, "Resta")
        pack = create_pack(db, target, values())
        create_pack(db, other, values(name="Altro"))
        for championship_id in (target, other):
            db.add(
                PackPurchase(
                    championship_id=championship_id,
                    pack_id=pack.id if championship_id == target else None,
                    pilot_name="Pilota",
                    pack_name="Base",
                    currency="gold",
                    cost=5,
                )
            )
        db.get(Championship, target).is_closed = True
        db.commit()

        delete_championship(db, target)

        assert db.get(Championship, target) is None
        assert [p.championship_id for p in db.query(Pack)] == [other]
        assert [p.championship_id for p in db.query(PackPurchase)] == [other]
