from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, UniqueConstraint
from app.db.base import Base
from sqlalchemy.sql import func, expression


class Championship(Base):
    __tablename__ = "championship"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    # Nome normalizzato per l'unicità senza distinguere le maiuscole.
    name_key = Column(String, nullable=False)
    date = Column(DateTime, nullable=False, server_default=func.now())
    is_closed = Column(Boolean, nullable=False, default=False)
    pool_deck_id = Column(Integer, ForeignKey("deck.id"), nullable=True)
    __table_args__ = (UniqueConstraint("name_key", name="uq_championship_name_key"),)

class ChampionshipPilot(Base):
    __tablename__ = "championship_pilot"

    id = Column(Integer, primary_key=True, index=True)
    championship_id = Column(Integer, ForeignKey("championship.id"), nullable=False)
    pilot_id = Column(Integer, ForeignKey("pilot.id"), nullable=False)

    __table_args__ = (
        UniqueConstraint("championship_id", "pilot_id"),
    )
  