"""Transizioni pure: nessun DB, commit, evento o autorizzazione HTTP."""
from collections.abc import Callable, Sequence
from random import SystemRandom

from app.schemas.draft.draft_state import DraftCardSlot, DraftState
from app.services.cards.cards import CardEntry, card_key
from app.services.draft.draft_order import (
    FIRST_RACE_PICKS, FIRST_RACE_ROW, draft_order, has_draft_copies, turn_pilot,
)
from app.services.shop.shop_draw import draw_cards


class DraftTransitionError(ValueError):
    """Comando incompatibile con fase o riferimenti correnti."""


class DraftTurnPermissionError(PermissionError):
    """Comando non appartenente al proprietario del pilota interessato."""


def _copy(state: DraftState, phase: str) -> DraftState:
    """Rivalida e copia lo stato; rifiuta una fase diversa da quella richiesta."""
    result = DraftState.model_validate(state.model_dump())
    if result.phase != phase:
        raise DraftTransitionError("Comando non disponibile nella fase corrente")
    return result


def _finish(state: DraftState) -> DraftState:
    """Valida anche le relazioni dopo la transizione."""
    return DraftState.model_validate(state.model_dump())


def advance_attendance(state: DraftState, pool: Sequence[CardEntry],
                       previous_finish: Sequence[int] | None, *,
                       shuffle: Callable[[list[int]], None] | None = None) -> DraftState:
    """Passa da presenze a ordine, o mazzi se non bastano N+3 copie.

    Parametri: stato, pool validata, arrivo precedente (None alla prima gara),
    shuffle opzionale. Ritorna nuovo stato senza consumare carte. Rifiuta zero
    presenti o riferimento prima gara incoerente. Creatore autorizzato a monte.
    """
    result = _copy(state, "attendance")
    present = [p.pilot_id for p in result.participants if p.present]
    if not present:
        raise DraftTransitionError("Serve almeno un pilota presente")
    if result.first_race != (previous_finish is None):
        raise DraftTransitionError("Riferimento alla gara precedente incoerente")
    if has_draft_copies(pool, len(present), first_race=result.first_race):
        result.order = draft_order(present, previous_finish, shuffle=shuffle)
        result.phase = "order"
    else:
        result.phase = "decks"
    return _finish(result)


def reorder(state: DraftState, pilot_ids: Sequence[int]) -> DraftState:
    """Sostituisce l'ordine con tutti e soli i presenti; permesso creatore a monte."""
    result = _copy(state, "order")
    result.order = list(pilot_ids)
    return _finish(result)


def start_picking(state: DraftState, pool: Sequence[CardEntry], *, rng=None
                  ) -> tuple[DraftState, list[CardEntry]]:
    """Estrae le copie iniziali senza mutare input; ritorna stato e pool residua.

    Alla prima gara il tavolo parte da cinque copie e cresce durante i giri;
    dopo la prima gara restano N+3 copie e una sola scelta per pilota. Riusa
    draw_cards senza filtri, con RNG opzionale. Una pool divenuta insufficiente
    causa errore, non salto silenzioso. Il servizio salva tutto atomicamente.
    """
    result = _copy(state, "order")
    needed = FIRST_RACE_ROW if result.first_race else len(result.order) + 3
    drawn, remaining = draw_cards(list(pool), needed, False, None,
                                  rng or SystemRandom())
    result.cards = []
    result.row = []
    for card in drawn:
        for _ in range(card.copies):
            slot = DraftCardSlot(slot_id=len(result.cards) + 1, name=card.name, path=card.path)
            result.cards.append(slot)
            if result.first_race:
                result.row.append(slot.slot_id)
    result.phase = "picking"
    return _finish(result), remaining


def _turn(state: DraftState, user_id: int) -> int:
    """Identifica il pilota di turno e verifica l'utente autenticato dal server."""
    pilot_id = turn_pilot(state.order, len(state.picks), state.first_race)
    owner = next(p.user_id for p in state.participants if p.pilot_id == pilot_id)
    if type(user_id) is not int or user_id != owner:
        raise DraftTurnPermissionError("Non e il tuo turno")
    return pilot_id


def _available(state: DraftState, slot_id: int) -> DraftCardSlot:
    """Restituisce una copia scelta possibile: tavolo alla prima gara, resto dopo."""
    if type(slot_id) is not int:
        raise DraftTransitionError("Copia non valida")
    if state.first_race:
        allowed = set(state.row)
    else:
        allowed = {card.slot_id for card in state.cards if card.chosen_by is None}
    card = next((item for item in state.cards if item.slot_id == slot_id), None)
    if card is None or slot_id not in allowed:
        raise DraftTransitionError("Copia non disponibile")
    return card


def preview(state: DraftState, user_id: int, slot_id: int | None) -> DraftState:
    """Imposta/toglie anteprima condivisa solo per il proprietario di turno.

    Gli zoom degli altri utenti restano locali. Nessuna copia viene prenotata
    o trasferita; ritorna un nuovo stato o un errore di turno/riferimento.
    """
    result = _copy(state, "picking")
    _turn(result, user_id)
    if slot_id is not None:
        _available(result, slot_id)
    result.preview_slot_id = slot_id
    return _finish(result)


def choose(state: DraftState, user_id: int, slot_id: int
           ) -> tuple[DraftState, int, CardEntry]:
    """Registra la singola scelta delle gare successive.

    Il servizio trasferisce la copia all'inventario nella stessa transazione.
    L'ultima scelta passa a decks, mai a Race. Alla prima gara, dove le scelte
    sono quattro e il tavolo viene rimpiazzato, si usa choose_first_race.
    """
    result = _copy(state, "picking")
    if result.first_race:
        raise DraftTransitionError("Prima gara con tavolo da cinque copie")
    pilot_id = _turn(result, user_id)
    slot = _available(result, slot_id)
    slot.chosen_by = pilot_id
    result.picks.append(slot_id)
    result.preview_slot_id = None
    if len(result.picks) == len(result.order):
        result.phase = "decks"
    return _finish(result), pilot_id, CardEntry(name=slot.name, path=slot.path, copies=1)


def _merge_copies(pool: Sequence[CardEntry], slots: Sequence[DraftCardSlot]) -> list[CardEntry]:
    """Rimette nel tavolo le copie non scelte, sommando per nome come la pool."""
    result = [card.model_copy() for card in pool]
    index = {card_key(card.name): card for card in result}
    for slot in slots:
        key = card_key(slot.name)
        found = index.get(key)
        if found is None:
            found = CardEntry(name=slot.name, path=slot.path, copies=1)
            result.append(found)
            index[key] = found
        else:
            found.copies += 1
    return result


def _deal(state: DraftState, pool: Sequence[CardEntry], count: int, rng) -> list[CardEntry]:
    """Aggiunge al tavolo le copie estratte, mantenendo gli slot progressivi."""
    drawn, remaining = draw_cards(list(pool), count, False, None, rng or SystemRandom())
    next_id = max((card.slot_id for card in state.cards), default=0) + 1
    for card in drawn:
        for _ in range(card.copies):
            slot = DraftCardSlot(slot_id=next_id, name=card.name, path=card.path)
            next_id += 1
            state.cards.append(slot)
            state.row.append(slot.slot_id)
    return remaining


def _return_row(state: DraftState, pool: Sequence[CardEntry]) -> list[CardEntry]:
    """Rimette nel tavolo le copie residue e le toglie dal registro della draft."""
    by_slot = {card.slot_id: card for card in state.cards}
    returned = [by_slot[item] for item in state.row]
    state.cards = [card for card in state.cards if card.chosen_by is not None]
    state.row = []
    return _merge_copies(pool, returned)


def choose_first_race(state: DraftState, user_id: int, slot_id: int,
                      pool: Sequence[CardEntry], *, rng=None
                      ) -> tuple[DraftState, int, CardEntry, list[CardEntry]]:
    """Registra una scelta della prima gara e rimpiazza il tavolo.

    Quattro scelte per pilota, alternate a serpentina. Dopo ogni scelta entra
    una copia; a fine giro le copie residue tornano nella pool e il tavolo
    riparte da cinque. All'ultima scelta il tavolo residuo torna nella pool e
    la fase passa a decks. Ritorna stato, pilota, copia scelta e pool residua;
    non crea mai la gara.
    """
    result = _copy(state, "picking")
    if not result.first_race:
        raise DraftTransitionError("Prima gara non in corso")
    pilot_id = _turn(result, user_id)
    slot = _available(result, slot_id)
    slot.chosen_by = pilot_id
    result.picks.append(slot_id)
    result.preview_slot_id = None
    result.row.remove(slot_id)
    total = FIRST_RACE_PICKS * len(result.order)
    remaining = list(pool)
    made = len(result.picks)
    if made == total:
        remaining = _return_row(result, remaining)
        result.phase = "decks"
    else:
        if made % len(result.order) == 0:
            remaining = _return_row(result, remaining)
            remaining = _deal(result, remaining, FIRST_RACE_ROW, rng)
        else:
            remaining = _deal(result, remaining, 1, rng)
    chosen = CardEntry(name=slot.name, path=slot.path, copies=1)
    return _finish(result), pilot_id, chosen, remaining


def set_ready(state: DraftState, user_id: int, pilot_id: int, ready: bool,
              game_cards: Sequence[CardEntry]) -> DraftState:
    """Conferma/revoca READY del proprio presente, senza modificare il mazzo.

    Il mazzo deve essere letto dal server sotto lock. Esattamente 15 copie
    richieste solo dopo la prima gara; massimo 15 sempre. Il servizio controlla
    all_ready e crea la gara nella stessa transazione. Revocare non impone 15.
    """
    result = _copy(state, "decks")
    if type(pilot_id) is not int or type(user_id) is not int or type(ready) is not bool:
        raise DraftTransitionError("Comando pronto non valido")
    participant = next((p for p in result.participants if p.pilot_id == pilot_id and p.present), None)
    if participant is None:
        raise DraftTransitionError("Pilota non presente")
    if participant.user_id != user_id:
        raise DraftTurnPermissionError("Il pilota non appartiene all'utente")
    if ready:
        count = sum(card.copies for card in game_cards)
        if count > 15 or (not result.first_race and count != 15):
            raise DraftTransitionError("Mazzo non pronto")
        if pilot_id not in result.ready:
            result.ready.append(pilot_id)
    elif pilot_id in result.ready:
        result.ready.remove(pilot_id)
    return _finish(result)


def all_ready(state: DraftState) -> bool:
    """True solo in decks con almeno un presente e tutti confermati."""
    checked = DraftState.model_validate(state.model_dump())
    present = {p.pilot_id for p in checked.participants if p.present}
    return checked.phase == "decks" and bool(present) and set(checked.ready) == present
