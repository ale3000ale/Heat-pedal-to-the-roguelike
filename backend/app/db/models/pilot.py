from sqlalchemy import Column, Integer, String, ForeignKey, CheckConstraint, UniqueConstraint
from app.db.base import Base

class Pilot(Base):
    __tablename__ = "pilot"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    gold = Column(Integer, nullable=False, default=0, server_default="0")
    sponsor = Column(Integer, nullable=False, default=0, server_default="0")
    point = Column(Integer, nullable=False, default=0, server_default="0")
    team_id = Column(Integer, ForeignKey("team.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    inventory_deck_id = Column(Integer, ForeignKey("deck.id"), nullable=False, unique=True)
    game_deck_id = Column(Integer, ForeignKey("deck.id"), nullable=False, unique=True)
