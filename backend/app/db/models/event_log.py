"""Registro persistente condiviso dai worker; non autorizza le letture."""
from sqlalchemy import Column, DateTime, ForeignKey, Index, Integer, String, Text
from sqlalchemy.sql import func

from app.db.base import Base


class EventLog(Base):
    """Evento transazionale; payload JSON validato dal servizio prima della scrittura."""

    __tablename__ = "event_log"

    id = Column(Integer, primary_key=True)
    type = Column(String(64), nullable=False)
    championship_id = Column(Integer, ForeignKey("championship.id", ondelete="CASCADE"), nullable=False)
    pilot_id = Column(Integer, ForeignKey("pilot.id", ondelete="SET NULL"), nullable=True)
    recipient_user_id = Column(Integer, ForeignKey("user.id", ondelete="CASCADE"), nullable=True)
    payload = Column(Text, nullable=False)
    created_at = Column(DateTime, nullable=False, server_default=func.now())

    __table_args__ = (
        Index("ix_event_log_championship_id_id", "championship_id", "id"),
        Index("ix_event_log_recipient_user_id_id", "recipient_user_id", "id"),
        Index("ix_event_log_created_at", "created_at"),
        {"sqlite_autoincrement": True},
    )
