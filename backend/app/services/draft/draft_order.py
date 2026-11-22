"""Regole pure di preparazione della draft; nessuna lettura o scrittura DB."""
from collections.abc import Callable, Sequence
from random import SystemRandom

from app.services.cards.cards import CardEntry


def draft_order(
    present: Sequence[int],
    previous_finish: Sequence[int] | None,
    *,
    shuffle: Callable[[list[int]], None] | None = None,
) -> list[int]:
    """Restituisce i presenti in ordine inverso, con nuovi presenti casuali in coda.

    Parametri: identificativi presenti, arrivo precedente dal primo all'ultimo
    (None per prima gara), funzione di mescolamento opzionale per i test.
    Ritorna una nuova lista; non modifica gli input. Duplicati, booleani e
    identificativi non interi positivi causano ValueError.
    """
    current = list(present)
    previous = list(previous_finish) if previous_finish is not None else []
    for values in (current, previous):
        if any(type(value) is not int or value < 1 for value in values):
            raise ValueError("Identificativo pilota non valido")
        if len(set(values)) != len(values):
            raise ValueError("Pilota ripetuto")
    present_ids = set(current)
    previous_ids = set(previous)
    ordered = [pilot_id for pilot_id in reversed(previous) if pilot_id in present_ids]
    newcomers = [pilot_id for pilot_id in current if pilot_id not in previous_ids]
    (shuffle or SystemRandom().shuffle)(newcomers)
    return ordered + newcomers


FIRST_RACE_PICKS = 4
FIRST_RACE_ROW = 5


def picks_per_pilot(first_race: bool) -> int:
    """Scelte spettanti a ogni presente: quattro alla prima gara, una dopo."""
    if type(first_race) is not bool:
        raise ValueError("Riferimento prima gara non valido")
    return FIRST_RACE_PICKS if first_race else 1


def required_draft_copies(present_count: int, first_race: bool) -> int:
    """Copie necessarie nella pool: quattro scelte a testa piu il tavolo da cinque.

    Parametri: numero positivo dei presenti e riferimento prima gara. Ritorna la
    soglia minima; non legge la pool. Conteggio non valido: ValueError.
    """
    if type(present_count) is not int or present_count < 1:
        raise ValueError("Serve almeno un pilota presente")
    if not first_race:
        return present_count + 3
    return present_count * FIRST_RACE_PICKS + FIRST_RACE_ROW


def has_draft_copies(pool: Sequence[CardEntry], present_count: int, *,
                     first_race: bool = False) -> bool:
    """Verifica se le copie disponibili coprono le scelte della procedura.

    Parametri: pool gia validata, numero positivo dei presenti, riferimento
    prima gara. Ritorna bool; non estrae carte e non modifica la pool.
    Conteggio non valido: ValueError.
    """
    return sum(card.copies for card in pool) >= required_draft_copies(present_count, first_race)


def turn_pilot(order: Sequence[int], made: int, first_race: bool) -> int:
    """Pilota di turno secondo l'ordine confermato.

    Alla prima gara i giri si alternano: il primo segue l'ordine, il secondo lo
    inverte, e cosi via. Dopo la prima gara resta una sola scelta per pilota.
    Parametri: ordine dei presenti, scelte gia registrate, riferimento prima
    gara. Ritorna l'identificativo del pilota. Indici non validi: ValueError.
    """
    total = len(order)
    if total < 1:
        raise ValueError("Serve almeno un pilota presente")
    if type(made) is not int or made < 0 or made >= total * picks_per_pilot(first_race):
        raise ValueError("Turno non disponibile")
    if not first_race:
        return order[made]
    round_index, position = divmod(made, total)
    if round_index % 2 == 1:
        position = total - 1 - position
    return order[position]
