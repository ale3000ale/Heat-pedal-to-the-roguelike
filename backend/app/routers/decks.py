# backend/app/routers/decks.py
# Endpoint per la pagina Mazzo: prototipi, mazzi utente, ricerca, dettaglio carte.

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db import get_db
from app.core.deps import get_current_user_required
from app.models.user import User
from app.models.deck import Deck
from app.schemas.deck import DeckOut, DeckPrototypeOut, DeckCreate
from app.services import deck_service
from app.services.deck_utils import deserialize_cards

router = APIRouter(prefix="/decks", tags=["decks"])


# _to_deck_out(deck)
# deck: istanza Deck dal DB.
# Deserializza il JSON delle carte e arricchisce la response con nomi pilota/campionato.
def _to_deck_out(deck: Deck) -> DeckOut:
    cards = deserialize_cards(deck.cards)
    pilot_name = deck.pilot.name if deck.pilot else None
    champ_name = (
        deck.pilot.championship_entries[0].championship.name
        if deck.pilot and deck.pilot.championship_entries
        else None
    )
    return DeckOut(
        id=deck.id, id_prototype=deck.id_prototype, pilot_id=deck.pilot_id,
        pilot_name=pilot_name, championship_name=champ_name, cards=cards,
    )


# list_prototypes(db)
# db: sessione SQLAlchemy attiva.
# Ritorna tutte le carte del gioco (via prototipi), per la pagina Mazzo "senza login".
@router.get("/prototypes", response_model=list[DeckPrototypeOut])
def list_prototypes(db: Session = Depends(get_db)):
    prototypes = deck_service.list_all_prototypes(db)
    return [
        DeckPrototypeOut(id=p.id, name=p.name, cards=deserialize_cards(p.base_cards))
        for p in prototypes
    ]


# list_my_decks(search_pilot, search_championship, db, current_user)
# search_pilot/search_championship: filtri opzionali; db: sessione; current_user: utente autenticato.
# Ritorna i mazzi dei piloti dell'utente, eventualmente filtrati dalla barra di ricerca.
@router.get("", response_model=list[DeckOut])
def list_my_decks(
    search_pilot: Optional[str] = None,
    search_championship: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_required),
):
    decks = deck_service.search_decks(db, search_pilot, search_championship, current_user.id)
    return [_to_deck_out(d) for d in decks]


# get_deck(deck_id, db)
# deck_id: id del mazzo da visualizzare; db: sessione SQLAlchemy.
# Ritorna il dettaglio di un mazzo con le sue carte (letto dal JSON in Deck.cards).
@router.get("/{deck_id}", response_model=DeckOut)
def get_deck(deck_id: int, db: Session = Depends(get_db)):
    deck = db.query(Deck).filter(Deck.id == deck_id).first()
    if deck is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Mazzo non trovato")
    return _to_deck_out(deck)


# create_deck(payload, db, current_user)
# payload: prototipo, pilota e lista carte del nuovo mazzo; db: sessione; current_user: utente autenticato.
# Valida e salva un nuovo mazzo concreto associato a un pilota dell'utente.
@router.post("", response_model=DeckOut, status_code=status.HTTP_201_CREATED)
def create_deck(
    payload: DeckCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_required),
):
    deck = deck_service.create_deck(db, payload.id_prototype, payload.pilot_id, payload.cards)
    return _to_deck_out(deck)
