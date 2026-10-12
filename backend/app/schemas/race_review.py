from datetime import datetime

from pydantic import BaseModel


class RaceReviewRead(BaseModel):
    # Stato della revisione delle carte di una gara.
    # in_review: vero solo se la revisione è aperta, non scaduta e non confermata.
    # reviewer_user_id: utente che ha aperto la revisione (vuoto se non è attiva).
    # review_expires_at: scadenza della revisione attiva (vuota se non è attiva).
    # review_closed_at: data di conferma; valorizzata = gara chiusa del tutto.
    race_id: int
    in_review: bool
    review_started_at: datetime | None
    reviewer_user_id: int | None = None
    review_expires_at: datetime | None = None
    review_closed_at: datetime | None = None
