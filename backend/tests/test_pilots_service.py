import pytest

from app.db.models import User
from app.db.models.championship import Championship, ChampionshipPilot
from app.db.models.deck import Deck
from app.security import hash_password
from app.services.cards import STARTER_INVENTORY, parse_cards
from app.services.pilots import (
    PilotInActiveChampionshipError,
    PilotNameTakenError,
    PilotNotFoundError,
    create_pilot,
    delete_pilot,
    get_own_pilot,
    list_pilots,
    rename_pilot,
    set_pilot_team,
)
from app.services.teams import TeamNotFoundError, create_team, delete_team


@pytest.fixture()
def db(session_factory):
    with session_factory() as session:
        yield session


def make_user(db, username):
    user = User(username=username, password=hash_password("password123"), role="player")
    db.add(user)
    db.commit()
    return user


@pytest.fixture()
def mario(db):
    return make_user(db, "mario")


@pytest.fixture()
def luigi(db):
    return make_user(db, "luigi")


def enroll(db, pilot, closed=False):
    # Iscrive il pilota a un nuovo campionato, aperto o chiuso.
    championship = Championship(name=f"Campionato {pilot.id}", is_closed=closed)
    db.add(championship)
    db.flush()
    db.add(ChampionshipPilot(championship_id=championship.id, pilot_id=pilot.id))
    db.commit()


def test_create_pilot_builds_both_decks_and_starts_at_zero(db, mario):
    pilot = create_pilot(db, mario, "  Ayrton   Rossi ")
    assert pilot.name == "Ayrton Rossi"
    assert pilot.team_id is None
    assert (pilot.gold, pilot.sponsor, pilot.point) == (0, 0, 0)
    inventory = db.get(Deck, pilot.inventory_deck_id)
    game = db.get(Deck, pilot.game_deck_id)
    assert parse_cards(inventory.cards) == STARTER_INVENTORY
    assert parse_cards(game.cards) == []
    assert inventory.id != game.id


def test_starter_inventory_has_four_speed_cards_with_three_copies(db, mario):
    pilot = create_pilot(db, mario, "Pilota")
    cards = parse_cards(db.get(Deck, pilot.inventory_deck_id).cards)
    assert [card.name for card in cards] == [f"Velocità {n}" for n in range(1, 5)]
    assert all(card.copies == 3 for card in cards)


def test_create_pilot_with_own_team(db, mario):
    team = create_team(db, mario, "Scuderia")
    assert create_pilot(db, mario, "Pilota", team.id).team_id == team.id


def test_create_pilot_rejects_other_users_team(db, mario, luigi):
    team = create_team(db, luigi, "Team Luigi")
    with pytest.raises(TeamNotFoundError):
        create_pilot(db, mario, "Pilota", team.id)


def test_create_pilot_rejects_deleted_team(db, mario):
    team = create_team(db, mario, "Scuderia")
    delete_team(db, mario, team.id)
    with pytest.raises(TeamNotFoundError):
        create_pilot(db, mario, "Pilota", team.id)


def test_failed_create_leaves_no_orphan_decks(db, mario):
    create_pilot(db, mario, "Pilota")
    decks_before = db.query(Deck).count()
    with pytest.raises(PilotNameTakenError):
        create_pilot(db, mario, "pilota")
    assert db.query(Deck).count() == decks_before


def test_pilot_name_is_unique_across_users_ignoring_case(db, mario, luigi):
    create_pilot(db, mario, "Ayrton")
    with pytest.raises(PilotNameTakenError):
        create_pilot(db, luigi, "AYRTON")
    with pytest.raises(PilotNameTakenError):
        create_pilot(db, luigi, "  ayrton ")


def test_deleted_pilot_keeps_its_name_taken(db, mario):
    pilot = create_pilot(db, mario, "Ayrton")
    delete_pilot(db, mario, pilot.id)
    with pytest.raises(PilotNameTakenError):
        create_pilot(db, mario, "Ayrton")


def test_list_pilots_is_own_visible_and_alphabetical(db, mario, luigi):
    create_pilot(db, mario, "Zeta")
    create_pilot(db, mario, "alfa")
    hidden = create_pilot(db, mario, "Beta")
    create_pilot(db, luigi, "Altro")
    delete_pilot(db, mario, hidden.id)
    assert [pilot.name for pilot in list_pilots(db, mario)] == ["alfa", "Zeta"]


def test_other_users_pilot_looks_non_existent(db, mario, luigi):
    pilot = create_pilot(db, mario, "Ayrton")
    with pytest.raises(PilotNotFoundError):
        get_own_pilot(db, luigi, pilot.id)
    with pytest.raises(PilotNotFoundError):
        rename_pilot(db, luigi, pilot.id, "Rubato")
    with pytest.raises(PilotNotFoundError):
        set_pilot_team(db, luigi, pilot.id, None)
    with pytest.raises(PilotNotFoundError):
        delete_pilot(db, luigi, pilot.id)


def test_unknown_pilot_is_not_found(db, mario):
    with pytest.raises(PilotNotFoundError):
        get_own_pilot(db, mario, 999)


def test_rename_pilot_and_change_only_case(db, mario):
    pilot = create_pilot(db, mario, "ayrton")
    assert rename_pilot(db, mario, pilot.id, "Ayrton").name == "Ayrton"
    assert rename_pilot(db, mario, pilot.id, "Niki").name == "Niki"


def test_rename_to_taken_name_is_rejected(db, mario):
    create_pilot(db, mario, "Ayrton")
    other = create_pilot(db, mario, "Niki")
    with pytest.raises(PilotNameTakenError):
        rename_pilot(db, mario, other.id, "ayrton")


def test_rename_is_allowed_even_when_enrolled(db, mario):
    pilot = create_pilot(db, mario, "Ayrton")
    enroll(db, pilot)
    assert rename_pilot(db, mario, pilot.id, "Niki").name == "Niki"


def test_move_and_remove_team_when_not_enrolled(db, mario):
    first = create_team(db, mario, "Team A")
    second = create_team(db, mario, "Team B")
    pilot = create_pilot(db, mario, "Ayrton", first.id)
    assert set_pilot_team(db, mario, pilot.id, second.id).team_id == second.id
    assert set_pilot_team(db, mario, pilot.id, None).team_id is None
    assert set_pilot_team(db, mario, pilot.id, first.id).team_id == first.id


def test_set_team_rejects_other_users_team(db, mario, luigi):
    foreign = create_team(db, luigi, "Team Luigi")
    pilot = create_pilot(db, mario, "Ayrton")
    with pytest.raises(TeamNotFoundError):
        set_pilot_team(db, mario, pilot.id, foreign.id)
    assert get_own_pilot(db, mario, pilot.id).team_id is None


def test_team_is_locked_while_enrolled_in_active_championship(db, mario):
    first = create_team(db, mario, "Team A")
    second = create_team(db, mario, "Team B")
    pilot = create_pilot(db, mario, "Ayrton", first.id)
    enroll(db, pilot, closed=False)
    with pytest.raises(PilotInActiveChampionshipError):
        set_pilot_team(db, mario, pilot.id, second.id)
    with pytest.raises(PilotInActiveChampionshipError):
        set_pilot_team(db, mario, pilot.id, None)
    assert get_own_pilot(db, mario, pilot.id).team_id == first.id


def test_team_is_free_again_when_championship_is_closed(db, mario):
    team = create_team(db, mario, "Team A")
    pilot = create_pilot(db, mario, "Ayrton")
    enroll(db, pilot, closed=True)
    assert set_pilot_team(db, mario, pilot.id, team.id).team_id == team.id


def test_delete_pilot_hides_it_but_keeps_row_and_decks(db, mario):
    pilot = create_pilot(db, mario, "Ayrton")
    inventory_id, game_id = pilot.inventory_deck_id, pilot.game_deck_id
    delete_pilot(db, mario, pilot.id)
    db.refresh(pilot)
    assert pilot.deleted_at is not None
    assert list_pilots(db, mario) == []
    assert db.get(Deck, inventory_id) is not None
    assert db.get(Deck, game_id) is not None
    with pytest.raises(PilotNotFoundError):
        delete_pilot(db, mario, pilot.id)


def test_delete_blocked_in_active_championship_allowed_when_closed(db, mario):
    active = create_pilot(db, mario, "Attivo")
    enroll(db, active, closed=False)
    with pytest.raises(PilotInActiveChampionshipError):
        delete_pilot(db, mario, active.id)
    assert len(list_pilots(db, mario)) == 1

    closed = create_pilot(db, mario, "Concluso")
    enroll(db, closed, closed=True)
    delete_pilot(db, mario, closed.id)
    assert [pilot.name for pilot in list_pilots(db, mario)] == ["Attivo"]