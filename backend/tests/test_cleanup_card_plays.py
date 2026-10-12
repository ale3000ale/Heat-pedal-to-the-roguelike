from datetime import datetime, timezone

from app.db.models.card_play import STATUS_CONSUMED, STATUS_PLAYED, CardPlay
from app.db.models.championship import Championship
from app.db.models.pilot import Pilot
from app.db.models.race import Race
from tests.test_cleanup_api import (
    age,
    hide_pilot,
    hide_team,
    make_admin,
    make_player,
    make_team_with_pilots,
)


def add_race(session_factory) -> int:
    # Gara di un campionato senza iscritti: serve solo come chiave esterna delle giocate.
    with session_factory() as db:
        championship = Championship(name="Prova", name_key="prova")
        db.add(championship)
        db.flush()
        race = Race(
            championship_id=championship.id, number=1, date=datetime.now(timezone.utc)
        )
        db.add(race)
        db.commit()
        return race.id


def add_play(session_factory, race_id: int, pilot_id: int, status: str) -> None:
    with session_factory() as db:
        db.add(
            CardPlay(
                race_id=race_id,
                pilot_id=pilot_id,
                card_name="Sponsor",
                card_path="/images/cards/1_sponsor.webp",
                status=status,
            )
        )
        db.commit()


def remaining_plays(session_factory) -> list[int]:
    with session_factory() as db:
        return [p.pilot_id for p in db.query(CardPlay).order_by(CardPlay.id)]


def test_admin_purge_deletes_the_pilot_card_plays(make_client, session_factory):
    admin = make_admin(make_client, session_factory)
    player = make_player(make_client)
    _, (p1, p2) = make_team_with_pilots(player, "Rossa", ["Anna", "Beppe"])
    race_id = add_race(session_factory)
    add_play(session_factory, race_id, p1, STATUS_PLAYED)
    add_play(session_factory, race_id, p1, STATUS_CONSUMED)
    add_play(session_factory, race_id, p2, STATUS_PLAYED)
    hide_pilot(player, p1)
    assert admin.delete(f"/api/admin/deleted/pilots/{p1}").status_code == 204
    with session_factory() as db:
        assert db.get(Pilot, p1) is None
    assert remaining_plays(session_factory) == [p2]


def test_automatic_purge_deletes_the_pilot_card_plays(make_client, session_factory):
    admin = make_admin(make_client, session_factory)
    player = make_player(make_client)
    team_id, (p1,) = make_team_with_pilots(player, "Vecchia", ["Anna"])
    race_id = add_race(session_factory)
    add_play(session_factory, race_id, p1, STATUS_CONSUMED)
    hide_team(player, team_id)
    age(session_factory, 400, pilot_ids=[p1], team_ids=[team_id])
    r = admin.post("/api/admin/purge-expired")
    assert r.status_code == 200
    assert r.json()["deleted_pilots"] == 1
    with session_factory() as db:
        assert db.get(Pilot, p1) is None
    assert remaining_plays(session_factory) == []
