"""Poche regressioni mirate sul lock condiviso; esecuzione affidata alla CI."""
import sqlite3
from concurrent.futures import ThreadPoolExecutor
from threading import Barrier

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db.models import User
from app.db.models.deck import Deck
from app.db.models.pilot import Pilot
from app.services.cards import CardEntry, dump_cards, parse_cards
from app.services.pilot_deck import PilotCardNotFoundError, move_card
from app.services.sqlite_write_lock import SQLiteWriteLockError, acquire_sqlite_write_lock
from .test_pilots_api import create_pilot, register

PATH = "cards/starter/velocita-1.webp"


@pytest.fixture()
def own_pilot(client):
    user_id = register(client)
    return user_id, create_pilot(client).json()["id"]


def test_move_supports_an_existing_native_transaction(session_factory, own_pilot):
    with session_factory() as db:
        user = db.get(User, own_pilot[0])
        connection = db.connection()
        if not connection.connection.driver_connection.in_transaction:
            connection.exec_driver_sql("BEGIN")
        pilot = move_card(db, user, own_pilot[1], PATH, True)
        assert parse_cards(db.get(Deck, pilot.game_deck_id).cards)[0].copies == 1


def test_domain_error_rolls_back_and_releases_transaction(session_factory, own_pilot):
    with session_factory() as db:
        user = db.get(User, own_pilot[0])
        with pytest.raises(PilotCardNotFoundError):
            move_card(db, user, own_pilot[1], "cards/missing.webp", True)
        assert not db.in_transaction()


def test_cached_decks_are_refreshed_before_move(session_factory, own_pilot):
    with session_factory() as first:
        user = first.get(User, own_pilot[0])
        pilot = first.get(Pilot, own_pilot[1])
        cached = first.get(Deck, pilot.inventory_deck_id)
        with session_factory() as second:
            second.get(Deck, pilot.inventory_deck_id).cards = dump_cards([
                CardEntry(name="Velocità 1", path=PATH, copies=10),
            ])
            second.commit()
        moved = move_card(first, user, own_pilot[1], PATH, True)
        assert parse_cards(first.get(Deck, moved.inventory_deck_id).cards)[0].copies == 9
        assert parse_cards(cached.cards)[0].copies == 9


def test_pending_changes_are_not_silently_expired(session_factory, own_pilot):
    with session_factory() as db:
        pilot = db.get(Pilot, own_pilot[1])
        deck = db.get(Deck, pilot.game_deck_id)
        deck.cards = "[]"
        with pytest.raises(SQLiteWriteLockError):
            acquire_sqlite_write_lock(db)
        assert deck in db.dirty
        assert deck.cards == "[]"


def test_two_player_moves_preserve_both_copies(session_factory, own_pilot, tmp_path):
    path = tmp_path / "player-moves.sqlite"
    target = sqlite3.connect(path)
    with session_factory() as db:
        db.connection().connection.driver_connection.backup(target)
    target.close()
    engine = create_engine(f"sqlite:///{path}", connect_args={"check_same_thread": False, "timeout": 5})
    factory = sessionmaker(bind=engine, autoflush=False)
    barrier = Barrier(2, timeout=10)
    def attempt():
        with factory() as db:
            user = db.get(User, own_pilot[0])
            barrier.wait()
            move_card(db, user, own_pilot[1], PATH, True)
    try:
        with ThreadPoolExecutor(max_workers=2) as executor:
            futures = [executor.submit(attempt) for _ in range(2)]
            for future in futures:
                future.result(timeout=20)
        with factory() as db:
            pilot = db.get(Pilot, own_pilot[1])
            inventory = parse_cards(db.get(Deck, pilot.inventory_deck_id).cards)
            game = parse_cards(db.get(Deck, pilot.game_deck_id).cards)
            assert next(card.copies for card in inventory if card.path == PATH) == 1
            assert next(card.copies for card in game if card.path == PATH) == 2
    finally:
        engine.dispose()
