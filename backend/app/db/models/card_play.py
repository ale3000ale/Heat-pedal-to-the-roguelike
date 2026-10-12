from sqlalchemy import CheckConstraint, Column, DateTime, ForeignKey, Index, Integer, String
from sqlalchemy.sql import func

from app.db.base import Base

STATUS_PLAYED = "giocata"
STATUS_UNDONE = "annullata"
STATUS_CONSUMED = "consumata"


class CardPlay(Base):
    # Registro delle carte sponsor giocate da un pilota durante una gara. Le righe non
    # si cancellano: una giocata annullata o consumata resta nello storico.
    __tablename__ = "card_play"

    id = Column(Integer, primary_key=True, index=True)
    race_id = Column(Integer, ForeignKey("race.id"), nullable=False)
    pilot_id = Column(Integer, ForeignKey("pilot.id"), nullable=False)
    # Nome e percorso della carta come stanno nell'inventario sponsor del pilota.
    card_name = Column(String, nullable=False)
    card_path = Column(String, nullable=False)
    status = Column(String, nullable=False, default=STATUS_PLAYED, server_default=STATUS_PLAYED)
    played_at = Column(DateTime, nullable=False, server_default=func.now())

    __table_args__ = (
        CheckConstraint(
            "status IN ('giocata', 'annullata', 'consumata')", name="ck_card_play_status"
        ),
        Index("ix_card_play_race_pilot", "race_id", "pilot_id"),
    )
