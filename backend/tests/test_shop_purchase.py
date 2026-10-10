import random
from datetime import datetime

import pytest

from app.db.models import User
from app.db.models.championship import Championship, ChampionshipPilot
from app.db.models.deck import Deck
from app.db.models.pilot import Pilot
from app.db.models.race import Race
from app.db.models.shop import Pack, PackPurchase
from app.services.cards import CardEntry, dump_cards, parse_cards
from app.services.championships import ChampionshipClosedError
from app.services.packs import PackNotFoundError
from app.services.pilots import PilotNotFoundError
from app.services.shop_draw import PackSoldOutError
from app.services.shop_purchase import (
    InsufficientFundsError,
    InventoryLimitError,
    ShopLockedError,
    merge_inventory,
    purchase_pack,
)
from app.services.shop_view import (
    PilotNotEnrolledError,
    ShopAccessDeniedError,
    open_shop,
)


def card(name, copies):
    return CardEntry(name=name, path=f"cards/{name}.webp", copies=copies)


def new_deck(db, cards):
    deck = Deck(cards=dump_cards(cards))
    db.add(deck)
    db.flush()
    return deck


def cards_of(db, deck_id):
    return {c.name: c.copies for c in parse_cards(db.get(Deck, deck_id).cards)}


class Scene:
    pass


def make_scene(db, gold=50, sponsor=0, pool=None, sponsor_pool=None, inventory=None):
    scene = Scene()
    scene.user = User(username="giocatore", password="x", role="player")
    scene.admin = User(username="capo", password="x", role="admin")
    db.add_all([scene.user, scene.admin])
    db.flush()
    pool_deck = new_deck(db, pool if pool is not None else [card("Freni", 5)])
    sponsor_deck = new_deck(db, sponsor_pool if sponsor_pool is not None else [card("Logo", 4)])
    scene.pilot = Pilot(
        name="Pilota",
        name_key="pilota",
        gold=gold,
        sponsor=sponsor,
        user_id=scene.user.id,
        inventory_deck_id=new_deck(db, inventory or []).id,
        sponsor_inventory_deck_id=new_deck(db, []).id,
        game_deck_id=new_deck(db, []).id,
    )
    db.add(scene.pilot)
    scene.championship = Championship(
        name="Camp",
        name_key="camp",
        pool_deck_id=pool_deck.id,
        sponsor_pool_deck_id=sponsor_deck.id,
    )
    db.add(scene.championship)
    db.flush()
    db.add(ChampionshipPilot(championship_id=scene.championship.id, pilot_id=scene.pilot.id))
    scene.pool_deck_id = pool_deck.id
    scene.sponsor_deck_id = sponsor_deck.id
    db.commit()
    return scene


def add_pack(db, scene, **changes):
    values = {
        "name": "Base",
        "image_path": "x.webp",
        "currency": "gold",
        "cost": 10,
        "modifiche_count": 3,
        "sponsor_count": 0,
        "filter_enabled": False,
        "filter_text": None,
    }
    values.update(changes)
    pack = Pack(championship_id=scene.championship.id, **values)
    db.add(pack)
    db.commit()
    return pack


def buy(db, scene, pack, user=None):
    return purchase_pack(
        db, user or scene.user, scene.championship.id, pack.id, scene.pilot.id, random.Random(1)
    )


def test_purchase_updates_everything_together(session_factory):
    with session_factory() as db:
        scene = make_scene(db, inventory=[card("Freni", 2)])
        pack = add_pack(db, scene)
        result = buy(db, scene, pack)
        assert [(c.name, c.copies) for c in result.cards_modifiche] == [("Freni", 3)]
        assert result.cards_sponsor == []
        assert result.pilot.gold == 40
        assert cards_of(db, scene.pool_deck_id) == {"Freni": 2}
        assert cards_of(db, scene.pilot.inventory_deck_id) == {"Freni": 5}
        purchase = db.query(PackPurchase).one()
        assert (purchase.pilot_name, purchase.pack_name, purchase.cost) == ("Pilota", "Base", 10)
        assert parse_cards(purchase.cards_modifiche)[0].copies == 3
        assert purchase.cards_sponsor is None


def test_sponsor_pack_uses_sponsor_balance_and_pool(session_factory):
    with session_factory() as db:
        scene = make_scene(db, gold=0, sponsor=7)
        pack = add_pack(
            db, scene, currency="sponsor", cost=5, modifiche_count=1, sponsor_count=2
        )
        result = buy(db, scene, pack)
        assert result.pilot.sponsor == 2
        assert result.pilot.gold == 0
        assert sum(c.copies for c in result.cards_modifiche) == 1
        assert [(c.name, c.copies) for c in result.cards_sponsor] == [("Logo", 2)]
        assert cards_of(db, scene.sponsor_deck_id) == {"Logo": 2}
        assert cards_of(db, scene.pilot.sponsor_inventory_deck_id) == {"Logo": 2}
        assert cards_of(db, scene.pilot.inventory_deck_id) == {"Freni": 1}


def test_insufficient_funds_changes_nothing(session_factory):
    with session_factory() as db:
        scene = make_scene(db, gold=9)
        pack = add_pack(db, scene)
        with pytest.raises(InsufficientFundsError):
            buy(db, scene, pack)
        assert db.get(Pilot, scene.pilot.id).gold == 9
        assert cards_of(db, scene.pool_deck_id) == {"Freni": 5}
        assert db.query(PackPurchase).count() == 0


def test_sold_out_pack_changes_nothing(session_factory):
    with session_factory() as db:
        scene = make_scene(db, pool=[card("Freni", 2)])
        pack = add_pack(db, scene)
        with pytest.raises(PackSoldOutError):
            buy(db, scene, pack)
        assert db.get(Pilot, scene.pilot.id).gold == 50
        assert cards_of(db, scene.pool_deck_id) == {"Freni": 2}


def test_sold_out_on_the_sponsor_pool_blocks_the_whole_purchase(session_factory):
    with session_factory() as db:
        scene = make_scene(db, sponsor_pool=[card("Logo", 1)])
        pack = add_pack(db, scene, modifiche_count=1, sponsor_count=2)
        with pytest.raises(PackSoldOutError):
            buy(db, scene, pack)
        assert cards_of(db, scene.pool_deck_id) == {"Freni": 5}
        assert cards_of(db, scene.pilot.inventory_deck_id) == {}


def test_race_in_progress_locks_the_shop(session_factory):
    with session_factory() as db:
        scene = make_scene(db)
        pack = add_pack(db, scene)
        db.add(Race(championship_id=scene.championship.id, number=1, date=datetime.now()))
        db.commit()
        with pytest.raises(ShopLockedError):
            buy(db, scene, pack)
        assert open_shop(db, scene.user, scene.championship.id, scene.pilot.id).locked is True


def test_closed_championship_blocks_purchases(session_factory):
    with session_factory() as db:
        scene = make_scene(db)
        pack = add_pack(db, scene)
        scene.championship.is_closed = True
        db.commit()
        with pytest.raises(ChampionshipClosedError):
            buy(db, scene, pack)


def test_pilot_must_be_own_and_enrolled(session_factory):
    with session_factory() as db:
        scene = make_scene(db)
        pack = add_pack(db, scene)
        with pytest.raises(PilotNotFoundError):
            buy(db, scene, pack, user=scene.admin)
        db.query(ChampionshipPilot).delete()
        db.commit()
        with pytest.raises(PilotNotEnrolledError):
            buy(db, scene, pack)


def test_unknown_pack_is_not_found(session_factory):
    with session_factory() as db:
        scene = make_scene(db)
        with pytest.raises(PackNotFoundError):
            purchase_pack(db, scene.user, scene.championship.id, 999, scene.pilot.id)


def test_inventory_limit_changes_nothing(session_factory):
    with session_factory() as db:
        scene = make_scene(db, inventory=[card("Freni", 99)])
        pack = add_pack(db, scene)
        with pytest.raises(InventoryLimitError):
            buy(db, scene, pack)
        assert db.get(Pilot, scene.pilot.id).gold == 50
        assert cards_of(db, scene.pool_deck_id) == {"Freni": 5}
        assert cards_of(db, scene.pilot.inventory_deck_id) == {"Freni": 99}


def test_merge_inventory_adds_copies_and_ignores_case():
    merged = merge_inventory([card("Freni", 2)], [card("FRENI", 3), card("Turbo", 1)])
    assert {c.name: c.copies for c in merged} == {"Freni": 5, "Turbo": 1}
    with pytest.raises(InventoryLimitError):
        merge_inventory([card("Freni", 100)], [card("Freni", 1)])


def test_shop_view_marks_sold_out_packs(session_factory):
    with session_factory() as db:
        scene = make_scene(db, pool=[card("Freni", 2)])
        add_pack(db, scene, name="Grande", modifiche_count=3)
        add_pack(db, scene, name="Piccolo", modifiche_count=2)
        view = open_shop(db, scene.user, scene.championship.id, scene.pilot.id)
        assert [(p.name, sold) for p, sold in view.packs] == [("Grande", True), ("Piccolo", False)]
        assert view.read_only is False
        assert view.locked is False


def test_shop_access_rules(session_factory):
    with session_factory() as db:
        scene = make_scene(db)
        with pytest.raises(ShopAccessDeniedError):
            open_shop(db, scene.user, scene.championship.id)
        admin_view = open_shop(db, scene.admin, scene.championship.id)
        assert admin_view.pilot is None
        assert admin_view.read_only is True
        scene.championship.is_closed = True
        db.commit()
        with pytest.raises(ShopAccessDeniedError):
            open_shop(db, scene.user, scene.championship.id, scene.pilot.id)
        closed_view = open_shop(db, scene.admin, scene.championship.id)
        assert closed_view.read_only is True
        assert closed_view.locked is False
