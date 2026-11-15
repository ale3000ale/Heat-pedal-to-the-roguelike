"""Transazioni draft: lock, versioni, eventi e commit unico; nessuna API."""
from contextlib import contextmanager
from dataclasses import dataclass
from typing import Iterator

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import Deck, DraftPreparation, User
from app.schemas.draft_snapshot import DraftSnapshot
from app.schemas.draft_state import DraftState
from app.services.championships import ChampionshipClosedError, get_championship, list_entrants
from app.services.draft_notifications import signal_draft_changed
from app.services.draft_preparation import DraftPermissionError, DraftPreparationError
from app.services.draft_snapshot import DraftSnapshotConflictError, stage_snapshot_restore
from app.services.races import RaceInProgressError, has_race_in_progress
from app.services.sqlite_write_lock import acquire_sqlite_write_lock


@dataclass
class DraftMutation:
    """Dati interni utilizzabili solo nel contesto; mai serializzare snapshot.

    remove_preparation rimuove la riga sia per annullo sia per conclusione.
    Il ripristino e esplicito in cancel_preparation, mai automatico nel contesto.
    """
    row: DraftPreparation
    state: DraftState
    snapshot: DraftSnapshot
    decks: dict[int, Deck]
    remove_preparation: bool = False


def _authorize(db: Session, row: DraftPreparation, state: DraftState,
               user_id: int, creator_only: bool) -> None:
    """Autorizza creatore gestore o proprietario presente nelle fasi condivise."""
    if type(user_id) is not int or user_id < 1:
        raise DraftPermissionError("Utente non valido")
    role = db.scalar(select(User.role).where(User.id == user_id))
    if role is None:
        raise DraftPermissionError("Utente non disponibile")
    if row.creator_user_id == user_id:
        if role not in ("admin", "judge"):
            raise DraftPermissionError("Il creatore non puo piu gestire gare")
        return
    if creator_only or state.phase not in ("picking", "decks"):
        raise DraftPermissionError("Operazione riservata al creatore")
    if not any(p.present and p.user_id == user_id for p in state.participants):
        raise DraftPermissionError("Nessun proprio pilota presente")


def _load_decks(db: Session, snapshot: DraftSnapshot) -> dict[int, Deck]:
    """Verifica tutti i contenitori e le versioni attese prima delle modifiche."""
    ids = [item.deck_id for item in snapshot.decks]
    statement = select(Deck).where(Deck.id.in_(ids)).execution_options(populate_existing=True)
    decks = {deck.id: deck for deck in db.scalars(statement)}
    if set(decks) != set(ids) or any(
        decks[item.deck_id].version != (item.current_version or item.version)
        for item in snapshot.decks
    ):
        raise DraftSnapshotConflictError("Contenitori modificati fuori dalla preparazione")
    return decks


@contextmanager
def draft_mutation(db: Session, preparation_id: int, user_id: int,
                   expected_version: int, *, creator_only: bool = False
                   ) -> Iterator[DraftMutation]:
    """Rilegge sotto lock, autorizza e salva azione ed eventi atomicamente.

    Parametri: sessione pulita, ID preparazione, utente autenticato, versione
    attesa e vincolo opzionale al creatore. Il corpo modifica stato e soli Deck
    verificati. Rifiuta campionato chiuso, gara non conclusa, iscrizioni cambiate
    o versioni superate. Registra le versioni solo dopo il flush delle proprie
    scritture. Qualunque errore fa rollback completo; nessun retry.
    """
    try:
        acquire_sqlite_write_lock(db)
        if type(preparation_id) is not int or preparation_id < 1:
            raise DraftPreparationError("Preparazione non valida")
        row = db.get(DraftPreparation, preparation_id)
        if row is None:
            raise DraftPreparationError("Preparazione non trovata")
        state = DraftState.model_validate_json(row.state_json)
        snapshot = DraftSnapshot.model_validate_json(row.snapshot_json)
        _authorize(db, row, state, user_id, creator_only)
        if type(expected_version) is not int or expected_version < 1 or row.version != expected_version:
            raise DraftPreparationError("Preparazione modificata: rileggere lo stato")
        if row.phase != state.phase:
            raise DraftPreparationError("Fase persistita incoerente")
        championship = get_championship(db, row.championship_id)
        if championship.is_closed:
            raise ChampionshipClosedError
        if has_race_in_progress(db, row.championship_id):
            raise RaceInProgressError
        current = {p.id: p.user_id for p in list_entrants(db, row.championship_id)}
        if current != {p.pilot_id: p.user_id for p in state.participants}:
            raise DraftPreparationError("Iscrizioni cambiate durante la preparazione")
        work = DraftMutation(row, state, snapshot, _load_decks(db, snapshot))
        yield work
        state = DraftState.model_validate(work.state.model_dump())
        if work.remove_preparation:
            signal_draft_changed(db, row, state)
            db.delete(row)
        else:
            db.flush()
            for item in snapshot.decks:
                item.current_version = work.decks[item.deck_id].version
            row.phase = state.phase
            row.state_json = state.model_dump_json()
            row.snapshot_json = DraftSnapshot.model_validate(snapshot.model_dump()).model_dump_json()
            signal_draft_changed(db, row, state)
        db.commit()
    except Exception:
        db.rollback()
        raise


def cancel_preparation(db: Session, preparation_id: int, user_id: int, expected_version: int) -> None:
    """Ripristina originali, invia chiusura e rimuove la riga con un solo commit.

    Solo creatore gestore. Con propri presenti tutti pronti richiede prima
    non Pronto. Non decrementa versioni. Conflitti rifiutano l'intero annullo.
    Il segnale terminale e emesso dal contesto, non duplicarlo qui.
    """
    with draft_mutation(db, preparation_id, user_id, expected_version, creator_only=True) as work:
        own = {p.pilot_id for p in work.state.participants if p.present and p.user_id == user_id}
        if own and own <= set(work.state.ready):
            raise DraftPreparationError("Premere non Pronto prima di annullare")
        versions = {item.deck_id: item.current_version or item.version for item in work.snapshot.decks}
        stage_snapshot_restore(db, work.snapshot, versions)
        work.remove_preparation = True
