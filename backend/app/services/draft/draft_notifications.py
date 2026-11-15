"""Segnali draft accodati nella transazione dell'azione; nessun commit."""
from sqlalchemy.orm import Session

from app.db.models.draft import DraftPreparation
from app.schemas.draft.draft_state import DraftState
from app.schemas.core.events import EventCreate
from app.services.core.event_log import append_event


def signal_draft_changed(db: Session, row: DraftPreparation, state: DraftState) -> None:
    """Accoda un segnale distinto per destinatario, senza carte o snapshot.

    Parametri: sessione del chiamante, riga con ID disponibile, stato validato.
    In attendance/order riceve solo il creatore; in picking/decks anche i
    proprietari presenti, una volta per account. Usare prima di cancellare la
    preparazione per segnalare la chiusura. Errori propagano per rollback totale.
    """
    checked = DraftState.model_validate(state.model_dump())
    recipients = {row.creator_user_id}
    if checked.phase in ("picking", "decks"):
        recipients.update(p.user_id for p in checked.participants if p.present)
    for user_id in sorted(recipients):
        append_event(db, EventCreate(
            type="draft.changed", championship_id=row.championship_id,
            recipient_user_id=user_id, payload={"preparation_id": row.id},
        ))
