from datetime import datetime, timezone

from app.db.models import User
from app.db.models.card_play import CardPlay
from app.db.models.championship import Championship
from app.db.models.deck import Deck, DeckPrototype
from app.db.models.pilot import Pilot
from app.security import hash_password
from app.services.cards import STARTER_INVENTORY, CardEntry, dump_cards, parse_cards
from .race_fixtures import seed_game_deck_from_inventory_card

PASSWORD = "password123"
CARD = "Turbo Sponsor"


def setup_world(make_client, session_factory):
    with session_factory() as db:
        db.add(
            DeckPrototype(
                name="default",
                base_cards=dump_cards([CardEntry(name="Turbo", path="cards/base/turbo.webp", copies=1)]),
            )
        )
        db.commit()
    admin = make_client()
    with session_factory() as db:
        db.add(User(username="capo", password=hash_password(PASSWORD), role="admin"))
        db.commit()
    assert (
        admin.post("/api/auth/login", json={"username": "capo", "password": PASSWORD}).status_code
        == 200
    )
    player = make_client()
    assert (
        player.post(
            "/api/auth/register", json={"username": "mario", "password": PASSWORD}
        ).status_code
        == 201
    )
    return admin, player


def enrolled_pilot(player, championship_id, name="Ayrton"):
    team_id = player.post("/api/teams", json={"name": f"Team {name}"}).json()["id"]
    pilot_id = player.post("/api/pilots", json={"name": name, "team_id": team_id}).json()["id"]
    r = player.post(f"/api/championships/{championship_id}/pilots", json={"pilot_id": pilot_id})
    assert r.status_code == 201
    return pilot_id


def give_sponsor_cards(session_factory, pilot_id, copies):
    # L'iscrizione svuota l'inventario sponsor: le carte si danno dopo.
    with session_factory() as db:
        pilot = db.get(Pilot, pilot_id)
        cards = [CardEntry(name=CARD, path="cards/sponsor/turbo.webp", copies=copies)]
        db.get(Deck, pilot.sponsor_inventory_deck_id).cards = dump_cards(cards)
        db.commit()


def give_sponsor_pool(session_factory, championship_id, copies):
    with session_factory() as db:
        deck = Deck(cards=dump_cards([CardEntry(name=CARD, path="cards/sponsor/turbo.webp", copies=copies)]))
        db.add(deck)
        db.flush()
        db.get(Championship, championship_id).sponsor_pool_deck_id = deck.id
        db.commit()


def sponsor_inventory(session_factory, pilot_id):
    with session_factory() as db:
        pilot = db.get(Pilot, pilot_id)
        return {c.name: c.copies for c in parse_cards(db.get(Deck, pilot.sponsor_inventory_deck_id).cards)}


def sponsor_pool(session_factory, championship_id):
    with session_factory() as db:
        deck_id = db.get(Championship, championship_id).sponsor_pool_deck_id
        return {c.name: c.copies for c in parse_cards(db.get(Deck, deck_id).cards)}


def play_statuses(session_factory):
    with session_factory() as db:
        return [p.status for p in db.query(CardPlay).order_by(CardPlay.id)]


def start_race(admin, championship_id):
    r = admin.post(f"/api/championships/{championship_id}/races")
    assert r.status_code == 201
    return r.json()["id"]


def finish_race(admin, championship_id, race_id, pilot_id):
    r = admin.put(
        f"/api/championships/{championship_id}/races/{race_id}/results",
        json={"results": [{"pilot_id": pilot_id, "sponsor_points": 0}]},
    )
    assert r.status_code == 200


def close_and_confirm(admin, championship_id, race_id, pilot_id):
    # Il consumo delle carte avviene solo alla conferma della revisione.
    finish_race(admin, championship_id, race_id, pilot_id)
    base = f"/api/championships/{championship_id}/races/{race_id}/review"
    assert admin.post(base).status_code == 200
    assert admin.post(f"{base}/confirm").status_code == 200


def play(player, championship_id, pilot_id):
    return player.post(
        f"/api/championships/{championship_id}/card-plays",
        json={"pilot_id": pilot_id, "card_name": CARD},
    )


def undo(player, championship_id, pilot_id):
    return player.post(
        f"/api/championships/{championship_id}/card-plays/undo", json={"pilot_id": pilot_id}
    )


def scenario(make_client, session_factory, copies=3, pool_copies=1, *, game_deck_copies: int | None = 15):
    """Prepara giocate sponsor con un mazzo da gioco di fixture esplicito.

    copies e pool_copies riguardano solo gli sponsor; game_deck_copies indica
    le copie nel mazzo da gioco e None lo lascia vuoto. Ritorna admin, giocatore,
    campionato, pilota e gara. Errori HTTP o di preparazione falliscono la fixture;
    nessuna intercettazione dell'avvio o modifica all'inventario iniziale reale.
    """
    admin, player = setup_world(make_client, session_factory)
    championship_id = admin.post("/api/championships", json={"name": "Estate"}).json()["id"]
    pilot_id = enrolled_pilot(player, championship_id)
    give_sponsor_cards(session_factory, pilot_id, copies)
    give_sponsor_pool(session_factory, championship_id, pool_copies)
    if game_deck_copies is not None:
        seed_game_deck_from_inventory_card(
            session_factory, pilot_id, path=STARTER_INVENTORY[0].path, copies=game_deck_copies
        )
    race_id = start_race(admin, championship_id)
    return admin, player, championship_id, pilot_id, race_id


def test_playing_uses_available_copies_until_they_run_out(make_client, session_factory):
    _, player, champ, pilot, _ = scenario(make_client, session_factory, copies=2)
    first = play(player, champ, pilot)
    assert first.status_code == 201
    assert first.json()["available"][0]["copies_available"] == 1
    assert play(player, champ, pilot).status_code == 201
    assert play(player, champ, pilot).status_code == 409
    state = player.get(f"/api/championships/{champ}/card-plays", params={"pilot_id": pilot}).json()
    assert state["available"][0]["copies_available"] == 0
    assert len(state["plays"]) == 2


def test_playing_does_not_change_the_inventory_during_the_race(make_client, session_factory):
    _, player, champ, pilot, _ = scenario(make_client, session_factory, copies=2)
    assert play(player, champ, pilot).status_code == 201
    assert sponsor_inventory(session_factory, pilot) == {CARD: 2}


def test_unknown_card_cannot_be_played(make_client, session_factory):
    _, player, champ, pilot, _ = scenario(make_client, session_factory)
    r = player.post(
        f"/api/championships/{champ}/card-plays",
        json={"pilot_id": pilot, "card_name": "Inesistente"},
    )
    assert r.status_code == 409


def test_undo_frees_the_copy_and_keeps_the_log(make_client, session_factory):
    _, player, champ, pilot, _ = scenario(make_client, session_factory, copies=1)
    assert play(player, champ, pilot).status_code == 201
    r = undo(player, champ, pilot)
    assert r.status_code == 200
    assert r.json()["available"][0]["copies_available"] == 1
    assert play_statuses(session_factory) == ["annullata"]


def test_undo_without_plays_is_refused(make_client, session_factory):
    _, player, champ, pilot, _ = scenario(make_client, session_factory)
    assert undo(player, champ, pilot).status_code == 409


def test_five_consecutive_undos_then_the_limit(make_client, session_factory):
    _, player, champ, pilot, _ = scenario(make_client, session_factory, copies=6)
    for _ in range(6):
        assert play(player, champ, pilot).status_code == 201
    remaining = []
    for _ in range(5):
        r = undo(player, champ, pilot)
        assert r.status_code == 200
        remaining.append(r.json()["undo_remaining"])
    assert remaining == [4, 3, 2, 1, 0]
    assert undo(player, champ, pilot).status_code == 409


def test_playing_a_new_card_resets_the_undo_count(make_client, session_factory):
    _, player, champ, pilot, _ = scenario(make_client, session_factory, copies=6)
    for _ in range(6):
        assert play(player, champ, pilot).status_code == 201
    for _ in range(5):
        assert undo(player, champ, pilot).status_code == 200
    r = play(player, champ, pilot)
    assert r.status_code == 201
    assert r.json()["undo_remaining"] == 5
    assert undo(player, champ, pilot).status_code == 200


def test_no_plays_without_a_race_in_progress(make_client, session_factory):
    admin, player, champ, pilot, race = scenario(make_client, session_factory)
    finish_race(admin, champ, race, pilot)
    assert play(player, champ, pilot).status_code == 409


def test_a_player_cannot_play_with_someone_elses_pilot(make_client, session_factory):
    admin, _, champ, pilot, _ = scenario(make_client, session_factory)
    r = admin.post(
        f"/api/championships/{champ}/card-plays",
        json={"pilot_id": pilot, "card_name": CARD},
    )
    assert r.status_code == 404


def test_a_deleted_pilot_cannot_play_or_undo(make_client, session_factory):
    _, player, champ, pilot, _ = scenario(make_client, session_factory, copies=2)
    assert play(player, champ, pilot).status_code == 201
    # L'eliminazione via API è vietata in un campionato attivo: si simula l'eliminazione logica.
    with session_factory() as db:
        db.get(Pilot, pilot).deleted_at = datetime.now(timezone.utc).replace(tzinfo=None)
        db.commit()
    assert play(player, champ, pilot).status_code == 404
    assert undo(player, champ, pilot).status_code == 404


def test_confirming_the_review_consumes_the_played_cards(make_client, session_factory):
    admin, player, champ, pilot, race = scenario(make_client, session_factory, copies=3, pool_copies=1)
    assert play(player, champ, pilot).status_code == 201
    assert play(player, champ, pilot).status_code == 201
    finish_race(admin, champ, race, pilot)
    assert sponsor_inventory(session_factory, pilot) == {CARD: 3}
    close_and_confirm_review = f"/api/championships/{champ}/races/{race}/review"
    assert admin.post(close_and_confirm_review).status_code == 200
    assert sponsor_inventory(session_factory, pilot) == {CARD: 3}
    assert admin.post(f"{close_and_confirm_review}/confirm").status_code == 200
    assert sponsor_inventory(session_factory, pilot) == {CARD: 1}
    assert sponsor_pool(session_factory, champ) == {CARD: 3}
    assert play_statuses(session_factory) == ["consumata", "consumata"]


def test_undone_plays_are_not_consumed(make_client, session_factory):
    admin, player, champ, pilot, race = scenario(make_client, session_factory, copies=3, pool_copies=1)
    assert play(player, champ, pilot).status_code == 201
    assert play(player, champ, pilot).status_code == 201
    assert undo(player, champ, pilot).status_code == 200
    close_and_confirm(admin, champ, race, pilot)
    assert sponsor_inventory(session_factory, pilot) == {CARD: 2}
    assert sponsor_pool(session_factory, champ) == {CARD: 2}
    assert play_statuses(session_factory) == ["consumata", "annullata"]


def test_consuming_the_last_copy_removes_the_card_from_the_inventory(make_client, session_factory):
    admin, player, champ, pilot, race = scenario(make_client, session_factory, copies=1, pool_copies=1)
    assert play(player, champ, pilot).status_code == 201
    close_and_confirm(admin, champ, race, pilot)
    assert sponsor_inventory(session_factory, pilot) == {}
    assert sponsor_pool(session_factory, champ) == {CARD: 2}
