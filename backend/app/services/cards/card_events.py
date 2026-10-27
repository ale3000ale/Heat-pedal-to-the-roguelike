"""Notifiche private e invalidazioni pubbliche senza dettagli delle carte."""
from typing import Literal

from sqlalchemy.orm import Session

from app.db.models.pilot import Pilot
from app.db.models.race import Race
from app.schemas.core.events import EventCreate
from app.services.core.event_log import append_event


def record_card_action(db: Session, race: Race, pilot: Pilot,
                       action: Literal["card.played", "card.play_undone"], play_id: int) -> None:
    """Accoda due eventi nella transazione del chiamante, senza commit.

    Parametri: sessione, gara, pilota autorizzato, azione interna e id giocata.
    Ritorno: None. Il proprietario riceve l'id giocata; il pubblico soltanto
    race_id e pilot_id per rileggere dati autorizzati. Nessun nome o immagine.
    Errori di validazione/SQL propagano e devono annullare anche l'azione.
    """
    append_event(db, EventCreate(
        type=action, championship_id=race.championship_id, pilot_id=pilot.id,
        recipient_user_id=pilot.user_id,
        payload={"race_id": race.id, "play_id": play_id},
    ))
    append_event(db, EventCreate(
        type="cards.changed", championship_id=race.championship_id, pilot_id=pilot.id,
        payload={"race_id": race.id, "pilot_id": pilot.id},
    ))
