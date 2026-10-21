"""Conferma selettiva delle notifiche: nessuna modifica a carte o eventi SSE."""
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import User
from app.db.models.card_gift import CardGift
from app.db.models.race import Race
from app.schemas.card_gift_seen import GiftSeenSelection
from app.services.championships import get_championship
from app.services.pilots import get_own_pilot
from app.services.shop_purchase import _lock_database


def mark_selected_gifts_seen(
    db: Session, user: User, championship_id: int, selection: GiftSeenSelection
) -> None:
    """Segna viste solo le notifiche richieste del proprio pilota nel campionato.

    Parametri: sessione, utente autenticato, campionato e selezione validata.
    Ritorno: None. Duplicati ignorati; righe assenti/annullate, gia' viste o fuori
    ambito non vengono modificate. Risposta indistinguibile per gli ID fuori ambito.
    Anche admin/giudice devono possedere il pilota. Il campionato puo' essere chiuso:
    si confermano notifiche esistenti senza alterare il gioco o richiedere una gara.
    Errori: ValidationError, ChampionshipNotFoundError, PilotNotFoundError e SQL.
    Un solo commit; rollback su qualsiasi errore, senza conferme parziali.
    Richiede il DB aggiornato alla migrazione degli ID non riutilizzabili.
    """
    try:
        data = GiftSeenSelection.model_validate(selection.model_dump())
        _lock_database(db)
        get_championship(db, championship_id)
        pilot = get_own_pilot(db, user, data.pilot_id)
        statement = (
            select(CardGift)
            .join(Race, Race.id == CardGift.race_id)
            .where(
                CardGift.id.in_(sorted(set(data.gift_ids))),
                CardGift.pilot_id == pilot.id,
                Race.championship_id == championship_id,
                CardGift.seen_at.is_(None),
            )
        )
        now = datetime.now(timezone.utc).replace(tzinfo=None)
        for gift in db.scalars(statement):
            gift.seen_at = now
        db.flush()
        db.commit()
    except Exception:
        db.rollback()
        raise
