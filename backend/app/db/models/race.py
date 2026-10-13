from sqlalchemy import Column, Integer, ForeignKey, DateTime, CheckConstraint, UniqueConstraint
from app.db.base import Base
from sqlalchemy.sql import func

class Race(Base):
    __tablename__ = "race"

    id = Column(Integer, primary_key=True, index=True)
    championship_id = Column(Integer, ForeignKey("championship.id"), nullable=False)
    number = Column(Integer, nullable=False)
    date = Column(DateTime, nullable=True)
    # Valorizzata quando il giudice o l'admin apre la revisione delle carte, che segue la
    # conferma dei risultati. Vuota = revisione non aperta (o scaduta e riaperta da zero).
    review_started_at = Column(DateTime, nullable=True)
    # Utente (giudice o admin) che ha aperto la revisione: è l'unico che può vederla e agire.
    # Vuota quando la revisione non è aperta.
    review_started_by_user_id = Column(
        Integer,
        ForeignKey("user.id", name="fk_race_review_started_by_user_id"),
        nullable=True,
    )
    # Valorizzata quando la revisione è confermata: le carte giocate sono state consumate
    # e la gara è chiusa del tutto. Vuota con risultati presenti = revisione da fare.
    review_closed_at = Column(DateTime, nullable=True)

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
    sponsor_points = Column(Integer, nullable=False, default=0, server_default="0")

    __table_args__ = (
        UniqueConstraint("race_id", "pilot_id"),
        UniqueConstraint("race_id", "position"),
        CheckConstraint("position BETWEEN 1 AND 12", name="ck_race_result_position"),
        CheckConstraint("sponsor_points >= 0", name="ck_race_result_sponsor"),
    )
