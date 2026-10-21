"""Eventi delle assegnazioni: privati al proprietario, pubblici senza carte."""
from typing import Literal

from sqlalchemy.orm import Session

from app.db.models.card_gift import CardGift
from app.db.models.pilot import Pilot
from app.db.models.race import Race
from app.schemas.events import EventCreate
from app.services.event_log import append_event


def record_gift_action(db: Session, race: Race, pilot: Pilot, gift: CardGift,
                       action: Literal["card.gifted", "card.gift_undone"]) -> None:
    """Accoda eventi nella transazione del regalo o annullo; nessun commit.

    Parametri: sessione, gara, pilota, assegnazione con id e azione interna.
    Ritorno: None. Il privato contiene race_id/gift_id; il pubblico race_id/pilot_id.
    Nessun nome o immagine della carta. Il client rilegge le notifiche non viste,
    senza mostrare un regalo gia' annullato dal solo replay dell'evento.
    Errori propagano al chiamante, che deve annullare l'intera transazione.
    """
    append_event(db, EventCreate(
        type=action, championship_id=race.championship_id, pilot_id=pilot.id,
        recipient_user_id=pilot.user_id,
        payload={"race_id": race.id, "gift_id": gift.id},
    ))
    append_event(db, EventCreate(
        type="cards.changed", championship_id=race.championship_id, pilot_id=pilot.id,
        payload={"race_id": race.id, "pilot_id": pilot.id},
    ))
