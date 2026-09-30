from sqlalchemy import Column, Integer, ForeignKey, DateTime, CheckConstraint, UniqueConstraint
from app.db.base import Base
from sqlalchemy.sql import func

class Race(Base):
    __tablename__ = "race"

    id = Column(Integer, primary_key=True, index=True)
    championship_id = Column(Integer, ForeignKey("championship.id"), nullable=False)
    number = Column(Integer, nullable=False)
    date = Column(DateTime, nullable=True)

    __table_args__ = (
        UniqueConstraint("championship_id", "number"),
    )

class RaceResult(Base):
    __tablename__ = "race_result"

    id = Column(Integer, primary_key=True, index=True)
    race_id = Column(Integer, ForeignKey("race.id"), nullable=False)
    pilot_id = Column(Integer, ForeignKey("pilot.id"), nullable=False)
    position = Column(Integer, nullable=False)
    points = Column(Integer, nullable=False, default=0, server_default="0")

    __table_args__ = (
        UniqueConstraint("race_id", "pilot_id"),
        UniqueConstraint("race_id", "position"),
    )
