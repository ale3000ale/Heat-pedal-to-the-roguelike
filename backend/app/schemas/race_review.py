from datetime import datetime

from pydantic import BaseModel


class RaceReviewRead(BaseModel):
    # Stato di revisione di una gara: in_review è vero dalla data di apertura del riepilogo.
    race_id: int
    in_review: bool
    review_started_at: datetime | None
