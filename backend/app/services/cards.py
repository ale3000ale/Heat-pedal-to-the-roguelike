from pathlib import PurePath

from pydantic import BaseModel, Field, TypeAdapter, ValidationError

# Limite di carte (somma delle copie) del mazzo da gioco.
MAX_GAME_DECK_CARDS = 15


class CardError(ValueError):
    """Errore di formato o di regole sulle carte (messaggio leggibile)."""


class CardEntry(BaseModel):
    # Una riga di mazzo: una carta e quante copie identiche ne servono.
    name: str = Field(min_length=1, max_length=64)
    path: str = Field(min_length=1, max_length=255)
    copies: int = Field(ge=1, le=999)


_CARDS = TypeAdapter(list[CardEntry])


def card_key(name: str) -> str:
    # Identità della carta: nome senza spazi ai bordi e senza distinguere le maiuscole.
    return name.strip().casefold()


# Inventario di partenza di ogni pilota, indipendente dalla pool del campionato.
# I percorsi sono provvisori: le immagini verranno aggiunte più avanti.
STARTER_INVENTORY = [
    CardEntry(name=f"Velocità {n}", path=f"images/cards/base/velocita_{n}.webp", copies=3)
    for n in range(1, 5)
]


def parse_cards(raw: str | None) -> list[CardEntry]:
    # Legge il JSON salvato nel database. Testo vuoto o assente = nessuna carta.
    # Rifiuta formati errati e nomi duplicati nello stesso mazzo.
    if not raw:
        return []
    try:
        cards = _CARDS.validate_json(raw)
    except ValidationError as exc:
        raise CardError("Formato delle carte non valido") from exc
    keys = [card_key(card.name) for card in cards]
    if len(set(keys)) != len(keys):
        raise CardError("Carta duplicata nello stesso mazzo")
    return cards


def dump_cards(cards: list[CardEntry]) -> str:
    # Converte l'elenco di carte nel testo JSON da salvare nel database.
    return _CARDS.dump_json(cards).decode()


def validate_game_deck(inventory: list[CardEntry], game: list[CardEntry]) -> None:
    # Controlla il mazzo da gioco: massimo 15 carte in totale e, per ogni carta,
    # non più copie di quelle possedute nell'inventario.
    total = sum(card.copies for card in game)
    if total > MAX_GAME_DECK_CARDS:
        raise CardError(f"Il mazzo da gioco può avere al massimo {MAX_GAME_DECK_CARDS} carte")
    owned = {card_key(card.name): card.copies for card in inventory}
    for card in game:
        if card.copies > owned.get(card_key(card.name), 0):
            raise CardError(f"Carta non disponibile nell'inventario: {card.name}")


def parse_card_filename(filename: str) -> tuple[str, int]:
    # Ricava nome e copie dal nome del file: "ruota da bagnato_3.png" -> ("ruota da bagnato", 3).
    # Serve al modulo di caricamento delle carte.
    name, sep, count = PurePath(filename).stem.rpartition("_")
    if not sep or not name.strip() or not count.isdigit() or int(count) < 1:
        raise CardError("Nome file non valido: usare nome_N (N = numero di copie)")
    return name.strip(), int(count)