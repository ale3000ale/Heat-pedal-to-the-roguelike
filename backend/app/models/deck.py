# backend/app/models/deck.py
# Modelli SQLAlchemy per Deck e Deck_prototype.

from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from app.db import Base


class DeckPrototype(Base):
    __tablename__ = "Deck_prototype"

    id = Column(Integer, primary_key=True, index=True)
    base_cards = Column(String, nullable=True)  # JSON testuale: [{path, value}, ...]
    name = Column(String, unique=True, nullable=False)

    decks = relationship("Deck", back_populates="prototype")


class Deck(Base):
    __tablename__ = "Deck"

    id = Column(Integer, primary_key=True, index=True)
    cards = Column(String, nullable=True)  # JSON testuale: [{path, value}, ...]
    id_prototype = Column(Integer, ForeignKey("Deck_prototype.id"), nullable=False)
    pilot_id = Column(Integer, ForeignKey("Pilot.id"), nullable=True)  # campo aggiunto

    prototype = relationship("DeckPrototype", back_populates="decks")
    pilot = relationship("Pilot", back_populates="decks")
