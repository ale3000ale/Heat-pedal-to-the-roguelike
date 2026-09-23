# backend/app/models/shop.py
# Modelli SQLAlchemy per ShopItem e Purchase (tabelle aggiunte per la pagina Negozio).

from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db import Base


class ShopItem(Base):
    __tablename__ = "ShopItem"

    id = Column(Integer, primary_key=True, index=True)
    championship_id = Column(Integer, ForeignKey("Championship.id"), nullable=False)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    price_gold = Column(Integer, nullable=False, default=0)
    price_points = Column(Integer, nullable=False, default=0)
    requirements = Column(String, nullable=True)
    image_path = Column(String, nullable=True)

    championship = relationship("Championship", back_populates="shop_items")


class Purchase(Base):
    __tablename__ = "Purchase"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("User.id"), nullable=False)
    pilot_id = Column(Integer, ForeignKey("Pilot.id"), nullable=False)
    championship_id = Column(Integer, ForeignKey("Championship.id"), nullable=False)
    item_id = Column(Integer, ForeignKey("ShopItem.id"), nullable=False)
    purchased_at = Column(DateTime, server_default=func.now())
