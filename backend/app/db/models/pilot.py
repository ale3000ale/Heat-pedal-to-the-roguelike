from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, UniqueConstraint

from app.db.base import Base


class Pilot(Base):
    __tablename__ = "pilot"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    # Nome normalizzato per l'unicità senza distinguere le maiuscole.
    name_key = Column(String, nullable=False)
    gold = Column(Integer, nullable=False, default=0, server_default="0")
    sponsor = Column(Integer, nullable=False, default=0, server_default="0")
    point = Column(Integer, nullable=False, default=0, server_default="0")
    # Facoltativo: un pilota può esistere senza team.
    team_id = Column(Integer, ForeignKey("team.id"), nullable=True)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    inventory_deck_id = Column(Integer, ForeignKey("deck.id"), nullable=False, unique=True)
    game_deck_id = Column(Integer, ForeignKey("deck.id"), nullable=False, unique=True)
    # Data di eliminazione logica; None = pilota visibile.
    deleted_at = Column(DateTime, nullable=True)

    __table_args__ = (UniqueConstraint("name_key", name="uq_pilot_name_key"),)