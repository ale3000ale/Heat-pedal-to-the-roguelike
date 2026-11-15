from pydantic import BaseModel, Field

from app.services.championship.gold import MAX_CARD_POLL_SECONDS, MIN_CARD_POLL_SECONDS


class CardPollSettings(BaseModel):
    # Secondi tra due controlli delle notifiche delle carte sponsor (da 1 a 10).
    seconds: int = Field(ge=MIN_CARD_POLL_SECONDS, le=MAX_CARD_POLL_SECONDS)
