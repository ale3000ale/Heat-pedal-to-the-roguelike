"""Regole pure di preparazione della draft; nessuna lettura o scrittura DB."""
from collections.abc import Callable, Sequence
from random import SystemRandom

from app.services.cards import CardEntry


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


def has_draft_copies(pool: Sequence[CardEntry], present_count: int) -> bool:
    """Verifica se le copie disponibili coprono N piloti e tre carte residue.

    Parametri: pool gia validata, numero positivo dei presenti. Ritorna bool;
    non estrae carte e non modifica la pool. Conteggio non valido: ValueError.
    """
    if type(present_count) is not int or present_count < 1:
        raise ValueError("Serve almeno un pilota presente")
    return sum(card.copies for card in pool) >= present_count + 3
