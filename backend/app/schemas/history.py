from datetime import datetime

from pydantic import BaseModel

from app.schemas.purchase import DrawnCardRead


class PurchaseItemRead(BaseModel):
    # Un acquisto dello storico, con i valori copiati al momento dell'acquisto.
    id: int
    pack_name: str
    currency: str
    cost: int
    purchased_at: datetime
    cards_modifiche: list[DrawnCardRead]
    cards_sponsor: list[DrawnCardRead]


class PilotHistoryRead(BaseModel):
    pilot_id: int | None
    pilot_name: str
    purchases: list[PurchaseItemRead]


class HistoryRead(BaseModel):
    pilots: list[PilotHistoryRead]
