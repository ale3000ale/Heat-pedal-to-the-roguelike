import random

from app.services.cards import CardEntry, card_key


class PackSoldOutError(Exception):
    """Nella pool restano meno copie (dopo il filtro) di quelle da estrarre."""


def parse_filter(filter_text: str | None) -> list[str]:
    # Nomi del filtro: separati da virgola, senza spazi ai bordi, senza distinguere le
    # maiuscole, senza voci vuote.
    return [term.strip().casefold() for term in (filter_text or "").split(",") if term.strip()]


def _eligible(pool: list[CardEntry], filter_enabled: bool, filter_text: str | None):
    # Carte della pool che il filtro lascia estrarre: con il filtro spento tutte, con il
    # filtro acceso quelle il cui nome contiene almeno uno dei nomi indicati.
    if not filter_enabled:
        return list(pool)
    terms = parse_filter(filter_text)
    return [card for card in pool if any(term in card.name.casefold() for term in terms)]


def available_copies(pool: list[CardEntry], filter_enabled: bool, filter_text: str | None) -> int:
    # Copie estraibili: somma delle copie delle carte ammesse dal filtro.
    return sum(card.copies for card in _eligible(pool, filter_enabled, filter_text))


def is_sold_out(
    modifiche_count: int,
    sponsor_count: int,
    filter_enabled: bool,
    filter_text: str | None,
    modifiche_pool: list[CardEntry],
    sponsor_pool: list[CardEntry],
) -> bool:
    # "Terminato": una delle due pool ha meno copie estraibili di quelle richieste.
    return (
        available_copies(modifiche_pool, filter_enabled, filter_text) < modifiche_count
        or available_copies(sponsor_pool, filter_enabled, filter_text) < sponsor_count
    )


def draw_cards(
    pool: list[CardEntry],
    count: int,
    filter_enabled: bool,
    filter_text: str | None,
    rng: random.Random,
) -> tuple[list[CardEntry], list[CardEntry]]:
    # Estrae count carte, una alla volta: ogni copia rimasta ha la stessa probabilità e
    # dopo ogni estrazione le probabilità si ricalcolano. Non modifica la pool ricevuta.
    # Ritorna (carte estratte con le copie sommate, pool aggiornata senza carte a 0 copie).
    # Errori: PackSoldOutError se le copie estraibili sono meno di count.
    if count == 0:
        return [], list(pool)
    if available_copies(pool, filter_enabled, filter_text) < count:
        raise PackSoldOutError
    remaining = {card_key(card.name): card.model_copy() for card in pool}
    eligible = {card_key(card.name) for card in _eligible(pool, filter_enabled, filter_text)}
    drawn: dict[str, int] = {}
    for _ in range(count):
        candidates = [(key, remaining[key].copies) for key in remaining if key in eligible]
        roll = rng.randrange(sum(copies for _, copies in candidates))
        for key, copies in candidates:
            if roll < copies:
                break
            roll -= copies
        remaining[key].copies -= 1
        drawn[key] = drawn.get(key, 0) + 1
    drawn_cards = [
        CardEntry(name=remaining[key].name, path=remaining[key].path, copies=copies)
        for key, copies in drawn.items()
    ]
    return drawn_cards, [card for card in remaining.values() if card.copies > 0]
