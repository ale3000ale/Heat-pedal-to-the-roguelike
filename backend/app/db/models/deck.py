from sqlalchemy import Column, Integer, String, ForeignKey, CheckConstraint
from app.db.base import Base


class DeckPrototype(Base):
    __tablename__ = "deck_prototype"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    base_cards = Column(String, nullable=True)

class Deck(Base):
    __tablename__ = "deck"

    id = Column(Integer, primary_key=True, index=True)
    cards = Column(String, nullable=True)
    id_prototype = Column(Integer, ForeignKey("deck_prototype.id"), nullable=True)
