"""Invalidazioni delle correzioni di inventario, senza notifiche regalo."""
from sqlalchemy.orm import Session

from app.db.models.pilot import Pilot
from app.db.models.race import Race
from app.schemas.core.events import EventCreate
from app.services.core.event_log import append_event


def record_inventory_correction(db: Session, race: Race, pilot: Pilot) -> None:
    """Accoda cards.changed nella transazione autorizzata del revisore.

    Parametri: sessione, gara e pilota gia' verificati dal servizio chiamante.
    Ritorno: None. Il pubblico riceve solo race_id/pilot_id e rilegge le API
    autorizzate. Nessun dettaglio carta, evento privato o notifica CardGift.
    Non esegue commit; errori di validazione/SQL propagano al chiamante,
    che deve fare rollback anche del trasferimento tra inventario e pool.
    """
    append_event(db, EventCreate(
        type="cards.changed",
        championship_id=race.championship_id,
        pilot_id=pilot.id,
        payload={"race_id": race.id, "pilot_id": pilot.id},
    ))
