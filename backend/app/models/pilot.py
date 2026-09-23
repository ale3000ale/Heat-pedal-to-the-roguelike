# backend/app/models/pilot.py
# Modello SQLAlchemy per la tabella Pilot.

from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from app.db import Base


class Pilot(Base):
    __tablename__ = "Pilot"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    gold = Column(Integer, nullable=False, default=0)
    sponsor = Column(Integer, nullable=False, default=0)
    point = Column(Integer, nullable=False, default=0)
    championship_id = Column(Integer, ForeignKey("Championship.id"), nullable=True)
    team = Column(Integer, ForeignKey("Team.id"), nullable=True)
    user_id = Column(Integer, ForeignKey("User.id"), nullable=False)

    user = relationship("User", back_populates="pilots")
    team_rel = relationship("Team", back_populates="pilots")
    championship_entries = relationship("ChampionshipParticipant", back_populates="pilot")
    decks = relationship("Deck", back_populates="pilot")
