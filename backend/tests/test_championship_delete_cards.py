from datetime import datetime, timezone

from app.db.models.card_gift import CardGift
from app.db.models.card_play import STATUS_PLAYED, CardPlay
from app.db.models.championship import Championship
from app.db.models.pilot import Pilot
from app.db.models.race import Race
from app.services.championships import (
    ChampionshipOpenError,
    delete_championship,
)
from tests.test_cleanup_api import make_player, make_team_with_pilots

import pytest


def add_championship_with_cards(session_factory, pilot_id: int, closed: bool) -> int:
    # Campionato con una gara, una giocata e un regalo di carta sponsor.
    with session_factory() as db:
        championship = Championship(name="Da cancellare", name_key="da cancellare")
        championship.is_closed = closed
        db.add(championship)
        db.flush()
        race = Race(
            championship_id=championship.id, number=1, date=datetime.now(timezone.utc)
        )
        db.add(race)
        db.flush()
        db.add(
            CardPlay(
                race_id=race.id,
                pilot_id=pilot_id,
                card_name="Sponsor",
                card_path="/images/cards/1_sponsor.webp",
                status=STATUS_PLAYED,
            )
        )
        db.add(
            CardGift(
                race_id=race.id,
                pilot_id=pilot_id,
                card_name="Sponsor",
                card_path="/images/cards/1_sponsor.webp",
            )
        )
        db.commit()
        return championship.id


def count_rows(session_factory, model) -> int:
    with session_factory() as db:
        return db.query(model).count()


def test_delete_closed_championship_removes_plays_and_gifts(make_client, session_factory):
    player = make_player(make_client)
    _, (pilot_id,) = make_team_with_pilots(player, "Rossa", ["Anna"])
    championship_id = add_championship_with_cards(session_factory, pilot_id, closed=True)
    assert count_rows(session_factory, CardPlay) == 1
    assert count_rows(session_factory, CardGift) == 1
    with session_factory() as db:
        delete_championship(db, championship_id)
    assert count_rows(session_factory, Championship) == 0
    assert count_rows(session_factory, Race) == 0
    assert count_rows(session_factory, CardPlay) == 0
    assert count_rows(session_factory, CardGift) == 0
    with session_factory() as db:
        assert db.get(Pilot, pilot_id) is not None


def test_delete_open_championship_keeps_plays_and_gifts(make_client, session_factory):
    player = make_player(make_client)
    _, (pilot_id,) = make_team_with_pilots(player, "Blu", ["Beppe"])
    championship_id = add_championship_with_cards(session_factory, pilot_id, closed=False)
    with session_factory() as db:
        with pytest.raises(ChampionshipOpenError):
            delete_championship(db, championship_id)
    assert count_rows(session_factory, CardPlay) == 1
    assert count_rows(session_factory, CardGift) == 1
