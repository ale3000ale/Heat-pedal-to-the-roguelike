"""Eventi pubblici di invalidazione: nessun dettaglio delle carte."""
from typing import Literal

from sqlalchemy.orm import Session

from app.db.models.race import Race
from app.schemas.events import EventCreate
from app.services.event_log import append_event


def record_review_closed(db: Session, race: Race, action: Literal["confirmed", "expired"]) -> None:
    """Accoda due eventi senza commit, nella transazione che chiude la revisione.

    Parametri: sessione, gara chiusa e motivo interno. Nessun valore restituito.
    Errori di validazione/scrittura propagano: il chiamante deve fare rollback
    anche su inventari e pool. I payload non contengono carte, bozza o conteggi.
    """
    append_event(db, EventCreate(
        type="race.review_changed", championship_id=race.championship_id,
        payload={"race_id": race.id, "action": action},
    ))
    append_event(db, EventCreate(
        type="cards.changed", championship_id=race.championship_id,
        payload={"race_id": race.id},
    ))
