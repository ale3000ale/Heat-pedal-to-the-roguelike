from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, UniqueConstraint
from app.db.base import Base
from sqlalchemy.sql import func

class Championship(Base):
    __tablename__ = "championship"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    date = Column(DateTime, nullable=False, server_default=func.now())
    is_closed = Column(Boolean, nullable=False, default=False, server_default="false")
    pool_deck_id = Column(Integer, ForeignKey("deck.id"), nullable=True)

class ChampionshipPilot(Base):
    __tablename__ = "championship_pilot"

    id = Column(Integer, primary_key=True, index=True)
    championship_id = Column(Integer, ForeignKey("championship.id"), nullable=False)
    pilot_id = Column(Integer, ForeignKey("pilot.id"), nullable=False)

    __table_args__ = (
        UniqueConstraint("championship_id", "pilot_id"),
    )
