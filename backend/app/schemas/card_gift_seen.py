"""Richiesta limitata agli ID delle notifiche mostrate dal client."""
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field

DatabaseId = Annotated[int, Field(gt=0, le=9223372036854775807)]


class GiftSeenSelection(BaseModel):
    """Rifiuta campi extra, coercizioni, ID non positivi e batch oltre 100 ID."""

    model_config = ConfigDict(extra="forbid", strict=True)

    pilot_id: DatabaseId
    gift_ids: list[DatabaseId] = Field(min_length=1, max_length=100)
