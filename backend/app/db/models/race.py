from sqlalchemy import CheckConstraint, Column, DateTime, ForeignKey, Integer, Text, UniqueConstraint
from app.db.base import Base


class Race(Base):
    __tablename__ = "race"

    id = Column(Integer, primary_key=True, index=True)
    championship_id = Column(Integer, ForeignKey("championship.id"), nullable=False)
    number = Column(Integer, nullable=False)
    date = Column(DateTime, nullable=True)
    # Apertura e titolare della revisione; le date sono memorizzate in UTC.
    review_started_at = Column(DateTime, nullable=True)
    review_started_by_user_id = Column(
        Integer,
        ForeignKey("user.id", name="fk_race_review_started_by_user_id"),
        nullable=True,
    )
    # Conferma definitiva della revisione; nulla finché non viene chiusa.
    review_closed_at = Column(DateTime, nullable=True)
    # Testo JSON della bozza; validazione e utilizzo arrivano nel servizio dedicato.
    review_draft = Column(Text, nullable=True)

    __table_args__ = (UniqueConstraint("championship_id", "number"),)


class RaceResult(Base):
    __tablename__ = "race_result"

    id = Column(Integer, primary_key=True, index=True)
    race_id = Column(Integer, ForeignKey("race.id"), nullable=False)
    pilot_id = Column(Integer, ForeignKey("pilot.id"), nullable=False)
    position = Column(Integer, nullable=False)
    points = Column(Integer, nullable=False, default=0, server_default="0")
    sponsor_points = Column(Integer, nullable=False, default=0, server_default="0")

    __table_args__ = (
        UniqueConstraint("race_id", "pilot_id"),
        UniqueConstraint("race_id", "position"),
        CheckConstraint("position BETWEEN 1 AND 12", name="ck_race_result_position"),
        CheckConstraint("sponsor_points >= 0", name="ck_race_result_sponsor"),
    )
