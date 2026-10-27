from datetime import datetime

from pydantic import BaseModel, ConfigDict


class CardGiftRequest(BaseModel):
    # Pilota del giocatore che preme il tasto S o che conferma di aver visto le notifiche.
    pilot_id: int


class CardGiftRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    race_id: int
    card_name: str
    card_path: str
    created_at: datetime
