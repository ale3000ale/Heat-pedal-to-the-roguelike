"""Controlli draft senza lock o commit autonomi: transazione del chiamante."""
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models.championship import ChampionshipPilot
from app.db.models.draft import DraftPreparation


class DraftLockedError(ValueError):
    """Una preparazione attiva impedisce scritture esterne al suo flusso."""


def has_draft(db: Session, championship_id: int) -> bool:
    """Legge l'esistenza della preparazione senza modificare dati o sessione.

    Parametri: sessione e campionato. Ritorna bool. La lettura da sola non
    autorizza scritture successive: il chiamante deve mantenere il lock.
    Errori SQL propagano, senza trasformarli in assenza della preparazione.
    """
    statement = select(DraftPreparation.id).where(
        DraftPreparation.championship_id == championship_id
    ).limit(1)
    return db.scalar(statement) is not None


def pilot_has_draft(db: Session, pilot_id: int) -> bool:
    """Legge il blocco del mazzo ordinario per un iscritto, anche assente.

    Lo snapshot iniziale comprende tutti gli iscritti. I presenti modificano
    il mazzo tramite i comandi dedicati nella fase mazzi, prima di READY.
    Nessun lock, commit o rollback autonomo; errori SQL propagano.
    """
    statement = (
        select(DraftPreparation.id)
        .join(ChampionshipPilot, ChampionshipPilot.championship_id == DraftPreparation.championship_id)
        .where(ChampionshipPilot.pilot_id == pilot_id)
        .limit(1)
    )
    return db.scalar(statement) is not None


def require_no_draft(db: Session, championship_id: int) -> None:
    """Rifiuta una scrittura esterna al flusso draft, dopo il lock del servizio.

    Ritorna None se libero; DraftLockedError se occupato. Il servizio mantiene
    gestione dei propri errori e rollback. Non usare nei comandi della draft.
    """
    if has_draft(db, championship_id):
        raise DraftLockedError("Preparazione gara attiva: operazione temporaneamente bloccata")


def require_no_pilot_draft(db: Session, pilot_id: int) -> None:
    """Rifiuta lo spostamento ordinario dopo il lock e la verifica del proprietario.

    Ritorna None se libero; DraftLockedError se il pilota e coinvolto. Nessuna
    modifica: rollback e traduzione HTTP appartengono al chiamante.
    """
    if pilot_has_draft(db, pilot_id):
        raise DraftLockedError("Usare la preparazione gara per modificare il mazzo")
