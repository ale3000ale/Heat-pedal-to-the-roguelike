"""Test predisposti dei veri servizi dopo il consolidamento; non eseguiti localmente."""
import pytest
from sqlalchemy import func, select

from app.db.models import Championship, EventLog, PackPurchase, Pilot, Race, User
from app.services.admin_pilot_card_save import CardAdminConflictError, save_admin_pilot_cards
from app.services.admin_pilot_cards import read_admin_pilot_cards
from app.services.championships import close_championship, enroll_pilot
from app.services.draft_guards import DraftLockedError
from app.services.draft_preparation import open_preparation
from app.services.pilot_deck import has_race_in_progress, move_card
from app.services.races import create_race
from app.services.shop_purchase import purchase_pack
from tests.test_draft_preparation import seed


def test_external_writes_cannot_bypass_preparation(session_factory):
    cid, judge, _, player, pid = seed(session_factory)
    with session_factory() as db:
        open_preparation(db, cid, judge)
        actor = db.get(User, player)
        operations = [
            lambda: close_championship(db, cid),
            lambda: enroll_pilot(db, actor, cid, pid),
            lambda: move_card(db, actor, pid, "cards/missing.webp", True),
            lambda: create_race(db, cid),
            lambda: purchase_pack(db, actor, cid, 999999, pid),
        ]
        for operation in operations:
            with pytest.raises(DraftLockedError):
                operation()
        assert not db.get(Championship, cid).is_closed
        assert has_race_in_progress(db, db.get(Pilot, pid))
        assert db.scalar(select(func.count()).select_from(Race)) == 0
        assert db.scalar(select(func.count()).select_from(PackPurchase)) == 0
        assert db.scalar(select(func.count()).select_from(EventLog).where(EventLog.type == "race.started")) == 0


def test_admin_uses_existing_conflict_contract(session_factory):
    cid, judge, _, _, pid = seed(session_factory)
    with session_factory() as db:
        db.get(User, judge).role = "admin"
        db.commit()
        open_preparation(db, cid, judge)
        admin = db.get(User, judge)
        snapshot = read_admin_pilot_cards(db, admin, cid, pid)
        assert snapshot.read_only and snapshot.blocked_reason == "Preparazione gara attiva"
        with pytest.raises(CardAdminConflictError):
            save_admin_pilot_cards(db, admin, cid, pid, None)


def test_other_championship_remains_operational(session_factory):
    cid, judge, _, _, _ = seed(session_factory)
    with session_factory() as db:
        other = Championship(name="Altro", name_key="altro")
        db.add(other)
        db.commit()
        other_id = other.id
        open_preparation(db, cid, judge)
        assert close_championship(db, other_id).is_closed
        assert not db.get(Championship, cid).is_closed
