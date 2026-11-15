"""Eventi pubblici di invalidazione: nessun dettaglio delle carte."""
from typing import Literal

from sqlalchemy.orm import Session

from app.db.models.race import Race
from app.schemas.core.events import EventCreate
from app.services.core.event_log import append_event

ReviewAction = Literal["opened", "abandoned", "reopened", "started", "cancelled"]


def record_review_changed(db: Session, race: Race, action: ReviewAction) -> None:
    """Accoda un evento di stato della revisione senza commit.

    Parametri: sessione, gara modificata e azione interna. Nessun valore restituito.
    Errori di validazione o scrittura propagano: il chiamante fa rollback anche
    dello stato della gara. Il payload contiene solo race_id e azione.
    """
    append_event(db, EventCreate(
        type="race.review_changed", championship_id=race.championship_id,
        payload={"race_id": race.id, "action": action},
    ))


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
