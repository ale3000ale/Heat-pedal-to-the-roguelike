# backend/app/services/deck_utils.py
# Funzioni di serializzazione/deserializzazione e validazione per il campo Deck.cards (JSON testuale in DB).

import json
from typing import List
from app.schemas.deck import CardItem

VALID_CARD_INDEX_RANGE = range(1, 11)  # N va da 1 a 10, come richiesto


# serialize_cards(cards)
# cards: lista di CardItem (path immagine + value) da salvare nel DB.
# Trasforma la lista di oggetti Pydantic in una stringa JSON pronta per il campo Deck.cards.
# Passaggio critico: questa e' la forma che viene effettivamente scritta su disco nel DB SQLite.
def serialize_cards(cards: List[CardItem]) -> str:
    return json.dumps([c.model_dump() for c in cards])


# deserialize_cards(cards_json)
# cards_json: stringa JSON letta dal campo Deck.cards (o None se il mazzo e' vuoto).
# Ricostruisce la lista di CardItem partendo dal testo salvato nel DB, validandone la struttura.
# Passaggio critico: se il JSON e' corrotto o non valido, ritorna lista vuota invece di far crashare l'API.
def deserialize_cards(cards_json: str | None) -> List[CardItem]:
    if not cards_json:
        return []
    try:
        raw_list = json.loads(cards_json)
    except json.JSONDecodeError:
        return []
    result: List[CardItem] = []
    for raw in raw_list:
        try:
            result.append(CardItem(**raw))
        except Exception:
            continue  # scarta carte malformate senza bloccare l'intero mazzo
    return result


# validate_card_list(cards)
# cards: lista di CardItem da controllare prima del salvataggio di un mazzo.
# Verifica che ogni carta abbia un path con indice N valido (1-10) e un value intero >= 0.
# Solleva ValueError con messaggio chiaro se una carta non rispetta le regole di gioco.
def validate_card_list(cards: List[CardItem]) -> None:
    if not cards:
        raise ValueError("Il mazzo deve contenere almeno una carta")
    for card in cards:
        filename = card.path.split("/")[-1]
        prefix = filename.split("_", 1)[0]
        if not prefix.isdigit() or int(prefix) not in VALID_CARD_INDEX_RANGE:
            raise ValueError(f"Indice carta non valido nel path '{card.path}'")
        if card.value < 0:
            raise ValueError(f"Valore carta non valido per '{card.path}': {card.value}")
