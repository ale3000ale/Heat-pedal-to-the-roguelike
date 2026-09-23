# backend/app/models/championship.py
# Modello SQLAlchemy per la tabella Championship e ChampionshipParticipant.

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship

from app.db import Base


class Championship(Base):
    __tablename__ = "Championship"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    pilots = Column(String, nullable=True)  # campo legacy, non usato nella logica applicativa
    deck = Column(Integer, ForeignKey("Deck.id"), nullable=True)
    date = Column(DateTime, nullable=False)

    participants = relationship("ChampionshipParticipant", back_populates="championship")
    shop_items = relationship("ShopItem", back_populates="championship")


class ChampionshipParticipant(Base):
    """Storico punti/ranking di un pilota in un dato campionato (tabella aggiunta)."""

    __tablename__ = "ChampionshipParticipant"
    __table_args__ = (UniqueConstraint("championship_id", "pilot_id"),)

    id = Column(Integer, primary_key=True, index=True)
    championship_id = Column(Integer, ForeignKey("Championship.id"), nullable=False)
    pilot_id = Column(Integer, ForeignKey("Pilot.id"), nullable=False)
    points = Column(Integer, nullable=False, default=0)
    ranking = Column(Integer, nullable=True)

    championship = relationship("Championship", back_populates="participants")
    pilot = relationship("Pilot", back_populates="championship_entries")
