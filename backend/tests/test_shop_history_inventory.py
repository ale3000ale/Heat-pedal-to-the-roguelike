from datetime import datetime

import pytest

from app.db.models import User
from app.db.models.championship import Championship, ChampionshipPilot
from app.db.models.deck import Deck
from app.db.models.pilot import Pilot
from app.db.models.shop import PackPurchase
from app.services.cards import STARTER_INVENTORY, CardEntry, dump_cards
from app.services.pilots import PilotNotFoundError
from app.services.shop_history import group_by_pilot, list_all_history, list_own_history
from app.services.shop_inventory import inventory_summary, visible_cards
from app.services.shop_view import PilotNotEnrolledError, ShopAccessDeniedError


def card(name, copies):
    return CardEntry(name=name, path=f"cards/{name}.webp", copies=copies)


def new_deck(db, cards=()):
    deck = Deck(cards=dump_cards(list(cards)))
    db.add(deck)
    db.flush()
    return deck


def new_pilot(db, user, name, inventory=(), sponsor_inventory=()):
    pilot = Pilot(
        name=name,
        name_key=name.casefold(),
        user_id=user.id,
        inventory_deck_id=new_deck(db, inventory).id,
        sponsor_inventory_deck_id=new_deck(db, sponsor_inventory).id,
        game_deck_id=new_deck(db).id,
    )
    db.add(pilot)
    db.flush()
    return pilot


class Scene:
    pass


def make_scene(db):
    scene = Scene()
    scene.user = User(username="giocatore", password="x", role="player")
    scene.other = User(username="altro", password="x", role="player")
    scene.admin = User(username="capo", password="x", role="admin")
    db.add_all([scene.user, scene.other, scene.admin])
    db.flush()
    scene.anna = new_pilot(
        db,
        scene.user,
        "Anna",
        inventory=[card("Turbo", 2), card("Freni", 1), *STARTER_INVENTORY],
        sponsor_inventory=[card("Logo", 3)],
    )
    scene.zeno = new_pilot(db, scene.user, "Zeno")
    scene.bruno = new_pilot(db, scene.other, "Bruno")
    scene.championship = Championship(
        name="Camp",
        name_key="camp",
        pool_deck_id=new_deck(db).id,
        sponsor_pool_deck_id=new_deck(db).id,
    )
    db.add(scene.championship)
    db.flush()
    for pilot in (scene.anna, scene.zeno, scene.bruno):
        db.add(ChampionshipPilot(championship_id=scene.championship.id, pilot_id=pilot.id))
    db.commit()
    return scene


def add_purchase(db, scene, pilot, minute, pack_name="Base", pilot_name=None):
    purchase = PackPurchase(
        championship_id=scene.championship.id,
        pilot_id=pilot.id if pilot is not None else None,
        pilot_name=pilot_name or pilot.name,
        pack_name=pack_name,
        currency="gold",
        cost=10,
        purchased_at=datetime(2026, 10, 8, 12, minute),
    )
    db.add(purchase)
    db.commit()
    return purchase


def test_own_history_has_only_own_pilots_newest_first(session_factory):
    with session_factory() as db:
        scene = make_scene(db)
        old = add_purchase(db, scene, scene.anna, 1, "Vecchio")
        new = add_purchase(db, scene, scene.anna, 5, "Nuovo")
        mine = add_purchase(db, scene, scene.zeno, 3)
        add_purchase(db, scene, scene.bruno, 4)
        purchases = list_own_history(db, scene.user, scene.championship.id)
        assert [p.id for p in purchases] == [new.id, mine.id, old.id]


def test_history_is_grouped_by_pilot_in_alphabetical_order(session_factory):
    with session_factory() as db:
        scene = make_scene(db)
        add_purchase(db, scene, scene.zeno, 1)
        add_purchase(db, scene, scene.anna, 2, "A")
        add_purchase(db, scene, scene.anna, 3, "B")
        groups = group_by_pilot(list_own_history(db, scene.user, scene.championship.id))
        assert [(g.pilot_name, [p.pack_name for p in g.purchases]) for g in groups] == [
            ("Anna", ["B", "A"]),
            ("Zeno", ["Base"]),
        ]


def test_deleted_pilot_purchases_are_grouped_by_saved_name(session_factory):
    with session_factory() as db:
        scene = make_scene(db)
        add_purchase(db, scene, None, 1, pilot_name="Fantasma")
        add_purchase(db, scene, None, 2, pilot_name="Fantasma")
        groups = group_by_pilot(list_all_history(db, scene.championship.id))
        assert [(g.pilot_id, g.pilot_name, len(g.purchases)) for g in groups] == [
            (None, "Fantasma", 2)
        ]


def test_all_history_includes_every_pilot(session_factory):
    with session_factory() as db:
        scene = make_scene(db)
        add_purchase(db, scene, scene.anna, 1)
        add_purchase(db, scene, scene.bruno, 2)
        assert len(list_all_history(db, scene.championship.id)) == 2
        assert list_own_history(db, scene.admin, scene.championship.id) == []


def test_closed_championship_history_is_for_the_admin_only(session_factory):
    with session_factory() as db:
        scene = make_scene(db)
        add_purchase(db, scene, scene.anna, 1)
        scene.championship.is_closed = True
        db.commit()
        with pytest.raises(ShopAccessDeniedError):
            list_own_history(db, scene.user, scene.championship.id)
        assert list_own_history(db, scene.admin, scene.championship.id) == []


def test_visible_cards_hides_starters_and_sorts():
    cards = [card("turbo", 1), *STARTER_INVENTORY, card("Antenna", 2)]
    assert [c.name for c in visible_cards(cards)] == ["Antenna", "turbo"]


def test_inventory_summary_returns_both_inventories_without_starters(session_factory):
    with session_factory() as db:
        scene = make_scene(db)
        pilot, modifiche, sponsor = inventory_summary(
            db, scene.user, scene.championship.id, scene.anna.id
        )
        assert pilot.id == scene.anna.id
        assert [(c.name, c.copies) for c in modifiche] == [("Freni", 1), ("Turbo", 2)]
        assert [(c.name, c.copies) for c in sponsor] == [("Logo", 3)]


def test_inventory_summary_rules(session_factory):
    with session_factory() as db:
        scene = make_scene(db)
        with pytest.raises(PilotNotFoundError):
            inventory_summary(db, scene.user, scene.championship.id, scene.bruno.id)
        db.query(ChampionshipPilot).filter_by(pilot_id=scene.zeno.id).delete()
        db.commit()
        with pytest.raises(PilotNotEnrolledError):
            inventory_summary(db, scene.user, scene.championship.id, scene.zeno.id)
        scene.championship.is_closed = True
        db.commit()
        with pytest.raises(ShopAccessDeniedError):
            inventory_summary(db, scene.user, scene.championship.id, scene.anna.id)
