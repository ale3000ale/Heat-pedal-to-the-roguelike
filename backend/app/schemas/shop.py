# backend/app/schemas/shop.py
# Schemi Pydantic per ShopItem e Purchase.

from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class ShopItemOut(BaseModel):
    id: int
    championship_id: int
    name: str
    description: Optional[str] = None
    price_gold: int
    price_points: int
    requirements: Optional[str] = None
    image_path: Optional[str] = None

    class Config:
        from_attributes = True


class ShopItemCreate(BaseModel):
    championship_id: int
    name: str
    description: Optional[str] = None
    price_gold: int = 0
    price_points: int = 0
    requirements: Optional[str] = None
    image_path: Optional[str] = None


class PurchaseCreate(BaseModel):
    pilot_id: int
    championship_id: int
    item_id: int


class PurchaseOut(BaseModel):
    id: int
    pilot_id: int
    championship_id: int
    item_id: int
    purchased_at: datetime

    class Config:
        from_attributes = True


class WalletOut(BaseModel):
    """Recap di gold e punti di un pilota in un dato campionato."""
    pilot_id: int
    pilot_name: str
    championship_id: int
    gold: int
    points: int
