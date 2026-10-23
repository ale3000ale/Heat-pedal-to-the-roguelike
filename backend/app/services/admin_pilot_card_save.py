"""Salvataggio admin atomico; non crea carte, pool, notifiche regalo o migrazioni."""
from typing import get_args
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import Session
from sqlalchemy.orm.exc import StaleDataError

from app.db.models.deck import Deck
from app.db.models.user import User
from app.schemas.admin_pilot_cards import AdminPilotCardsRead, AdminPilotCardsSave
from app.schemas.events import EventCreate
from app.services.admin_card_transfers import CardTransfer, Container, plan_transfers
from app.services.admin_pilot_cards import CardAdminForbiddenError, read_admin_pilot_cards
from app.services.cards import dump_cards
from app.services.event_log import append_event
from app.services.sqlite_write_lock import SQLiteWriteLockError, acquire_sqlite_write_lock


class CardAdminConflictError(ValueError):
    """Stato, versioni o disponibilita' cambiati: la bozza non viene sovrascritta."""


def _lock_cards(db: Session) -> None:
    """Usa il lock condiviso; traduce gli errori di contratto senza fare commit."""
    try:
        acquire_sqlite_write_lock(db)
    except SQLiteWriteLockError as exc:
        raise CardAdminConflictError(str(exc)) from exc


def _check_versions(snapshot: AdminPilotCardsRead, data: AdminPilotCardsSave) -> None:
    """Confronta id e versione di tutti i contenitori, comprese pool assenti."""
    for name in get_args(Container):
        current = getattr(snapshot.containers, name)
        expected = getattr(data.versions, name)
        if not current.available:
            if expected is not None:
                raise CardAdminConflictError("Disponibilita' dei contenitori cambiata")
        elif expected is None or (expected.id, expected.version) != (current.id, current.version):
            raise CardAdminConflictError("Carte modificate da un'altra richiesta: ricaricare i dati")


def _prepare(snapshot: AdminPilotCardsRead, data: AdminPilotCardsSave):
    """Valida pool e prepara un piano senza mutare DB o snapshot; errori propagano."""
    for transfer in data.transfers:
        pool = "modification_pool" if transfer.source in (
            "game_deck", "modification_inventory", "modification_pool",
        ) else "sponsor_pool"
        if not getattr(snapshot.containers, pool).available:
            raise CardAdminConflictError("La pool necessaria non esiste nel campionato")
    return plan_transfers(
        {name: getattr(snapshot.containers, name).cards for name in get_args(Container)},
        [CardTransfer(transfer.source, transfer.path) for transfer in data.transfers],
    )


def save_admin_pilot_cards(
    db: Session, user: User, championship_id: int, pilot_id: int, data: AdminPilotCardsSave,
) -> AdminPilotCardsRead:
    """Applica un'unica conferma admin, con un solo commit e rollback completo.

    Parametri: sessione, utente autenticato, campionato/pilota e bozza validata.
    Ritorno: nuovo snapshot con versioni aggiornate. Ricontrolla ruolo, iscrizione,
    chiusura, gara/revisione e versioni dopo il lock. Nessun retry automatico.
    Errori: quelli della lettura, CardTransferError o CardAdminConflictError;
    errori SQL/eventi inattesi propagano dopo rollback. I segnali sono nella
    medesima transazione e non contengono carte; una bozza senza differenze non
    incrementa versioni e non genera eventi. Non richiede 15 carte al salvataggio.
    """
    actor_id = user.id
    try:
        _lock_cards(db)
        actor = db.get(User, actor_id)
        if actor is None:
            raise CardAdminForbiddenError
        snapshot = read_admin_pilot_cards(db, actor, championship_id, pilot_id)
        if snapshot.read_only:
            raise CardAdminConflictError(snapshot.blocked_reason)
        _check_versions(snapshot, data)
        planned = _prepare(snapshot, data)
        changed = False
        for name, cards in planned.items():
            current = getattr(snapshot.containers, name)
            if cards != current.cards:
                db.get(Deck, current.id).cards = dump_cards(cards)
                changed = True
        if changed:
            append_event(db, EventCreate(type="cards.changed", championship_id=championship_id))
            append_event(db, EventCreate(
                type="cards.changed", championship_id=championship_id, pilot_id=pilot_id,
                recipient_user_id=snapshot.pilot.user_id,
            ))
        db.flush()
        result = read_admin_pilot_cards(db, actor, championship_id, pilot_id)
        db.commit()
        return result
    except StaleDataError as exc:
        db.rollback()
        raise CardAdminConflictError("Versioni cambiate durante il salvataggio") from exc
    except OperationalError as exc:
        db.rollback()
        code = getattr(exc.orig, "sqlite_errorcode", 0)
        if code & 255 in (5, 6):
            raise CardAdminConflictError("Database occupato o snapshot superato: riprovare manualmente") from exc
        raise
    except Exception:
        db.rollback()
        raise
