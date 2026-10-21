from sqlalchemy import Column, DateTime, ForeignKey, Index, Integer, String
from sqlalchemy.sql import func

from app.db.base import Base


class CardGift(Base):
    # Carta sponsor regalata a un pilota con il tasto S durante una gara. Serve alla
    # notifica "Hai ottenuto una carta sponsor": finché seen_at è vuoto il giocatore non
    # l'ha ancora vista. Il bonus del giudice a fine gara non crea righe qui.
    __tablename__ = "card_gift"

    id = Column(Integer, primary_key=True, index=True)
    race_id = Column(Integer, ForeignKey("race.id"), nullable=False)
    pilot_id = Column(Integer, ForeignKey("pilot.id"), nullable=False)
    # Nome e percorso della carta come stanno nell'inventario sponsor del pilota.
    card_name = Column(String, nullable=False)
    card_path = Column(String, nullable=False)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    seen_at = Column(DateTime, nullable=True)

    # Una conferma ritardata non deve riferirsi a un nuovo regalo con ID riciclato.
    __table_args__ = (
        Index("ix_card_gift_pilot_seen", "pilot_id", "seen_at"),
        {"sqlite_autoincrement": True},
    )
