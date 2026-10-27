"""Apertura e presenze interne: nessun router espone ancora queste operazioni."""
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import DraftPreparation, Race, User
from app.schemas.draft.draft_snapshot import DraftSnapshot
from app.schemas.draft.draft_state import DraftParticipant, DraftState
from app.services.championship.championships import ChampionshipClosedError, get_championship, list_entrants
from app.services.draft.draft_snapshot import capture_snapshot
from app.services.draft.draft_notifications import signal_draft_changed
from app.services.race.races import RaceInProgressError, has_race_in_progress
from app.services.core.sqlite_write_lock import acquire_sqlite_write_lock


class DraftPreparationError(ValueError):
    """Preparazione mancante, superata o non modificabile nella fase corrente."""


class DraftPermissionError(PermissionError):
    """Utente non autorizzato a gestire la preparazione."""


def _manager(db: Session, user_id: int) -> None:
    """Rilegge il ruolo dal database sotto il lock del chiamante."""
    if type(user_id) is not int or db.scalar(select(User.role).where(User.id == user_id)) not in ("admin", "judge"):
        raise DraftPermissionError("Solo admin e giudice possono preparare una gara")


def open_preparation(db: Session, championship_id: int, user_id: int) -> DraftPreparation:
    """Crea presenze e snapshot in una transazione, senza creare Race.

    Parametri: sessione pulita, campionato, ID autenticato lato server. Ritorna
    il contenitore interno persistito, non una risposta pubblica. Verifica ruolo,
    campionato aperto, nessuna gara non conclusa e nessuna preparazione esistente.
    Il chiamante deve elaborare prima le eventuali revisioni scadute.
    Su ogni errore esegue rollback; errori SQL e lock propagano senza retry.
    L'integrazione dei blocchi alle altre scritture resta necessaria prima dell'API.
    """
    try:
        acquire_sqlite_write_lock(db)
        _manager(db, user_id)
        championship = get_championship(db, championship_id)
        if championship.is_closed:
            raise ChampionshipClosedError
        if has_race_in_progress(db, championship_id):
            raise RaceInProgressError
        if db.scalar(select(DraftPreparation.id).where(DraftPreparation.championship_id == championship_id)) is not None:
            raise DraftPreparationError("Esiste gia una preparazione per questo campionato")
        entrants = list_entrants(db, championship_id)
        ids = []
        if championship.pool_deck_id is not None:
            ids.append(championship.pool_deck_id)
        for pilot in entrants:
            ids.extend((pilot.inventory_deck_id, pilot.game_deck_id))
        snapshot = capture_snapshot(db, ids)
        first_race = db.scalar(select(Race.id).where(Race.championship_id == championship_id).limit(1)) is None
        state = DraftState(format_version=1, phase="attendance", first_race=first_race,
            participants=[DraftParticipant(pilot_id=p.id, user_id=p.user_id, name=p.name, present=True) for p in entrants],
            order=[], cards=[], picks=[], preview_slot_id=None, ready=[])
        preparation = DraftPreparation(championship_id=championship_id, creator_user_id=user_id,
            phase=state.phase, state_json=state.model_dump_json(), snapshot_json=snapshot.model_dump_json())
        db.add(preparation)
        db.flush()
        signal_draft_changed(db, preparation, state)
        db.commit()
        db.refresh(preparation)
        return preparation
    except Exception:
        db.rollback()
        raise


def set_attendance(db: Session, preparation_id: int, user_id: int,
                   expected_version: int, pilot_id: int, present: bool) -> DraftPreparation:
    """Include o esclude un pilota noto nella sola fase presenze.

    Parametri: ID preparazione, utente autenticato, versione positiva attesa,
    pilota e presenza booleana. Ritorna riga interna dopo commit. Solo il creatore
    ancora admin/giudice puo agire. Errori di dominio, validazione e SQL causano
    rollback; nessun retry automatico, nessun aggiornamento di mazzi o pool.
    """
    try:
        acquire_sqlite_write_lock(db)
        _manager(db, user_id)
        row = db.get(DraftPreparation, preparation_id)
        if row is None:
            raise DraftPreparationError("Preparazione non trovata")
        if row.creator_user_id != user_id:
            raise DraftPermissionError("Solo il creatore puo cambiare le presenze")
        if type(expected_version) is not int or expected_version < 1 or row.version != expected_version:
            raise DraftPreparationError("Preparazione modificata: rileggere lo stato")
        championship = get_championship(db, row.championship_id)
        if championship.is_closed:
            raise ChampionshipClosedError
        if has_race_in_progress(db, row.championship_id):
            raise RaceInProgressError
        state = DraftState.model_validate_json(row.state_json)
        DraftSnapshot.model_validate_json(row.snapshot_json)
        if row.phase != state.phase or state.phase != "attendance":
            raise DraftPreparationError("La selezione presenze e terminata")
        if type(pilot_id) is not int or type(present) is not bool:
            raise DraftPreparationError("Pilota o presenza non validi")
        pilot = next((item for item in state.participants if item.pilot_id == pilot_id), None)
        if pilot is None:
            raise DraftPreparationError("Pilota non presente nella preparazione")
        pilot.present = present
        state = DraftState.model_validate(state.model_dump())
        row.state_json = state.model_dump_json()
        signal_draft_changed(db, row, state)
        db.commit()
        db.refresh(row)
        return row
    except Exception:
        db.rollback()
        raise
