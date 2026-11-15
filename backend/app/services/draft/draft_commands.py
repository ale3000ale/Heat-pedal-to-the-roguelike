"""Comandi draft interni: ogni azione usa una transazione e segnali privati."""
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import Championship, DraftPreparation, Pilot, Race, RaceResult
from app.services.cards.cards import CardEntry, dump_cards, parse_cards
from app.services.draft.draft_preparation import DraftPermissionError, DraftPreparationError
from app.services.draft.draft_transaction import DraftMutation, draft_mutation
from app.services.draft.draft_transitions import advance_attendance, choose, preview, reorder, start_picking
from app.services.pilots.pilot_deck import GameDeckFullError, _put_one, _take_one
from app.services.race.races import MAX_RACE_PILOTS


def _pool(db: Session, work: DraftMutation):
    """Legge la pool verificata; distingue assenza da riferimento cambiato."""
    championship = db.get(Championship, work.row.championship_id)
    if championship is None:
        raise DraftPreparationError("Campionato non disponibile")
    key = championship.pool_deck_id
    if key is None:
        return None
    if key not in work.decks:
        raise DraftPreparationError("Riferimento alla pool cambiato")
    return work.decks[key]


def _pilot(db: Session, work: DraftMutation, pilot_id: int) -> Pilot:
    """Verifica presente, proprietario e riferimenti a inventario/mazzo tracciati."""
    if type(pilot_id) is not int:
        raise DraftPreparationError("Pilota non valido")
    participant = next((p for p in work.state.participants if p.pilot_id == pilot_id and p.present), None)
    pilot = db.get(Pilot, pilot_id)
    if participant is None or pilot is None or pilot.deleted_at is not None:
        raise DraftPreparationError("Pilota non disponibile nella preparazione")
    if pilot.user_id != participant.user_id:
        raise DraftPreparationError("Proprietario del pilota cambiato")
    if (pilot.inventory_deck_id == pilot.game_deck_id
        or pilot.inventory_deck_id not in work.decks or pilot.game_deck_id not in work.decks):
        raise DraftPreparationError("Riferimenti ai mazzi cambiati")
    return pilot


def confirm_attendance(db: Session, preparation_id: int, user_id: int,
                       expected_version: int, *, shuffle=None) -> DraftPreparation:
    """Conferma presenze: ordine o direttamente mazzi con pool insufficiente.

    Solo creatore. Richiede 1-12 presenti e verifica proprietari/riferimenti,
    non il requisito delle 15 copie prima della modifica dei mazzi. Quel
    requisito resta in READY e nel ricontrollo finale prima della gara.
    Legge l'arrivo precedente. Snapshot, stato ed eventi sono coordinati da
    draft_mutation; errori fanno rollback, senza retry o completamenti automatici.
    """
    with draft_mutation(db, preparation_id, user_id, expected_version, creator_only=True) as work:
        if work.state.phase != "attendance":
            raise DraftPreparationError("Presenze gia confermate")
        present = [_pilot(db, work, p.pilot_id) for p in work.state.participants if p.present]
        if not 1 <= len(present) <= MAX_RACE_PILOTS:
            raise DraftPreparationError(f"Servono da 1 a {MAX_RACE_PILOTS} piloti presenti")
        previous = db.scalar(select(Race.id).where(Race.championship_id == work.row.championship_id)
                             .order_by(Race.number.desc()).limit(1))
        finish = None if previous is None else list(db.scalars(
            select(RaceResult.pilot_id).where(RaceResult.race_id == previous).order_by(RaceResult.position)))
        pool = _pool(db, work)
        work.state = advance_attendance(work.state, parse_cards(pool.cards) if pool is not None else [],
                                        finish, shuffle=shuffle)
    return db.get(DraftPreparation, preparation_id)


def change_order(db: Session, preparation_id: int, user_id: int,
                 expected_version: int, pilot_ids: list[int]) -> DraftPreparation:
    """Salva l'ordine del creatore: tutti e soli i presenti, senza duplicati."""
    with draft_mutation(db, preparation_id, user_id, expected_version, creator_only=True) as work:
        work.state = reorder(work.state, pilot_ids)
    return db.get(DraftPreparation, preparation_id)


def begin_picking(db: Session, preparation_id: int, user_id: int,
                  expected_version: int, *, rng=None) -> DraftPreparation:
    """Riserva N+3 copie e avvia i turni; stato e pool nello stesso commit.

    Solo creatore. Pool cambiata o insufficiente causa errore, mai un salto
    silenzioso. Le copie riservate escono dalla pool e restano negli slot.
    """
    with draft_mutation(db, preparation_id, user_id, expected_version, creator_only=True) as work:
        pool = _pool(db, work)
        if pool is None:
            raise DraftPreparationError("Pool modifiche non disponibile")
        work.state, remaining = start_picking(work.state, parse_cards(pool.cards), rng=rng)
        pool.cards = dump_cards(remaining)
    return db.get(DraftPreparation, preparation_id)


def share_preview(db: Session, preparation_id: int, user_id: int,
                  expected_version: int, slot_id: int | None) -> DraftPreparation:
    """Condivide l'anteprima del proprietario di turno; gli altri zoom restano locali."""
    with draft_mutation(db, preparation_id, user_id, expected_version) as work:
        work.state = preview(work.state, user_id, slot_id)
    return db.get(DraftPreparation, preparation_id)


def choose_card(db: Session, preparation_id: int, user_id: int,
                expected_version: int, slot_id: int) -> DraftPreparation:
    """Salva scelta e inventario insieme; all'ultima scelta torna la pool residua.

    Non sottrae nuovamente dalla pool la copia gia riservata all'estrazione.
    Le tre copie non scelte tornano alla pool una sola volta. Ultima scelta
    passa a decks, non crea Race. Ogni errore fa rollback dell'intera scelta.
    """
    with draft_mutation(db, preparation_id, user_id, expected_version) as work:
        next_state, pilot_id, card = choose(work.state, user_id, slot_id)
        pilot = _pilot(db, work, pilot_id)
        inventory = work.decks[pilot.inventory_deck_id]
        cards = parse_cards(inventory.cards)
        _put_one(cards, card)
        inventory.cards = dump_cards(cards)
        if next_state.phase == "decks":
            pool = _pool(db, work)
            if pool is None:
                raise DraftPreparationError("Pool modifiche non disponibile")
            remaining = parse_cards(pool.cards)
            for slot in next_state.cards:
                if slot.chosen_by is None:
                    _put_one(remaining, CardEntry(name=slot.name, path=slot.path, copies=1))
            pool.cards = dump_cards(remaining)
        work.state = next_state
    return db.get(DraftPreparation, preparation_id)


def move_draft_card(db: Session, preparation_id: int, user_id: int, expected_version: int,
                    pilot_id: int, path: str, to_game: bool) -> DraftPreparation:
    """Sposta una copia del proprio presente non pronto, soltanto in decks.

    Riusa i trasferimenti reali inventario/mazzo e mantiene massimo 15 anche
    alla prima gara. Aggiorna le versioni tracciate nella stessa transazione.
    Non chiama l'ingresso ordinario move_card, che durante la draft e bloccato.
    """
    with draft_mutation(db, preparation_id, user_id, expected_version) as work:
        if work.state.phase != "decks" or pilot_id in work.state.ready:
            raise DraftPreparationError("Mazzo non modificabile nella fase corrente")
        if type(to_game) is not bool or type(path) is not str or not path:
            raise DraftPreparationError("Spostamento non valido")
        pilot = _pilot(db, work, pilot_id)
        if pilot.user_id != user_id:
            raise DraftPermissionError("Il pilota non appartiene all'utente")
        inventory, game = work.decks[pilot.inventory_deck_id], work.decks[pilot.game_deck_id]
        inventory_cards, game_cards = parse_cards(inventory.cards), parse_cards(game.cards)
        if to_game and sum(card.copies for card in game_cards) >= 15:
            raise GameDeckFullError
        source, target = (inventory_cards, game_cards) if to_game else (game_cards, inventory_cards)
        _put_one(target, _take_one(source, path))
        inventory.cards, game.cards = dump_cards(inventory_cards), dump_cards(game_cards)
    return db.get(DraftPreparation, preparation_id)
