# backend/app/services/deck_service.py
# Logica di business per Deck e Deck_prototype, con ricerca per pilota/campionato.

from typing import Optional
from sqlalchemy.orm import Session
from app.models.deck import Deck, DeckPrototype
from app.models.pilot import Pilot
from app.models.championship import Championship
from app.services.deck_utils import serialize_cards, validate_card_list
from app.schemas.deck import CardItem


# list_all_prototypes(db)
# db: sessione SQLAlchemy attiva.
# Ritorna tutti i prototipi di mazzo con le relative carte base, per la pagina Mazzo "senza login".
def list_all_prototypes(db: Session) -> list[DeckPrototype]:
    return db.query(DeckPrototype).all()


# list_decks_by_user(db, user_id)
# db: sessione; user_id: id dell'utente loggato.
# Ritorna i mazzi concreti dei piloti dell'utente, per la pagina Mazzo "con login".
def list_decks_by_user(db: Session, user_id: int) -> list[Deck]:
    return (
        db.query(Deck)
        .join(Pilot, Deck.pilot_id == Pilot.id)
        .filter(Pilot.user_id == user_id)
        .all()
    )


# search_decks(db, pilot_name, championship_name, user_id)
# db: sessione; pilot_name/championship_name: filtri opzionali per la barra di ricerca;
# user_id: se fornito, limita ai mazzi dei piloti dell'utente.
# Applica i filtri via LIKE case-insensitive incrociando Pilot e Championship.
def search_decks(
    db: Session,
    pilot_name: Optional[str] = None,
    championship_name: Optional[str] = None,
    user_id: Optional[int] = None,
) -> list[Deck]:
    query = db.query(Deck).join(Pilot, Deck.pilot_id == Pilot.id, isouter=True)
    if user_id is not None:
        query = query.filter(Pilot.user_id == user_id)
    if pilot_name:
        query = query.filter(Pilot.name.ilike(f"%{pilot_name}%"))
    if championship_name:
        query = query.join(Championship, Pilot.championship_id == Championship.id).filter(
            Championship.name.ilike(f"%{championship_name}%")
        )
    return query.all()


# create_deck(db, id_prototype, pilot_id, cards)
# db: sessione; id_prototype: prototipo di riferimento; pilot_id: pilota proprietario (opzionale);
# cards: lista di CardItem da validare e salvare.
# Valida le carte e serializza in JSON prima del salvataggio nel DB.
# Passaggio critico: la validazione blocca il salvataggio se path o value non sono coerenti col gioco.
def create_deck(db: Session, id_prototype: int, pilot_id: Optional[int], cards: list[CardItem]) -> Deck:
    validate_card_list(cards)
    deck = Deck(
        id_prototype=id_prototype,
        pilot_id=pilot_id,
        cards=serialize_cards(cards),
    )
    db.add(deck)
    db.commit()
    db.refresh(deck)
    return deck
