"""READY e creazione finale nella transazione della preparazione."""
from dataclasses import dataclass
from datetime import datetime, timezone

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.db.models.race import Race
from app.schemas.events import EventCreate
from app.services.cards import parse_cards
from app.services.draft_commands import _pilot
from app.services.draft_preparation import DraftPreparationError
from app.services.draft_transaction import draft_mutation
from app.services.draft_transitions import all_ready, set_ready
from app.services.event_log import append_event
from app.services.races import MAX_RACE_PILOTS


@dataclass(frozen=True)
class DraftCompletion:
    """Esito interno: preparazione ancora attiva oppure gara appena creata."""
    preparation_id: int | None
    race_id: int | None


def _stage_race(db: Session, championship_id: int) -> Race:
    """Prepara numero, data e race.started senza commit autonomo.

    Il chiamante mantiene il lock e ha gia verificato campionato e assenza di
    gare non concluse. Non richiamare create_race: il suo commit e il vecchio
    controllo di tutti gli iscritti non appartengono alla finalizzazione draft.
    """
    last = db.scalar(select(func.max(Race.number)).where(Race.championship_id == championship_id))
    race = Race(championship_id=championship_id, number=(last or 0) + 1,
                date=datetime.now(timezone.utc))
    db.add(race)
    db.flush()
    append_event(db, EventCreate(type="race.started", championship_id=championship_id,
                                payload={"race_id": race.id}))
    return race


def ready_pilot(db: Session, preparation_id: int, user_id: int,
                expected_version: int, pilot_id: int, ready: bool) -> DraftCompletion:
    """Conferma/revoca il proprio READY; l'ultimo confermato crea la gara.

    Parametri: sessione, preparazione, ID autenticato, versione attesa, pilota e
    bool. Controlla il mazzo reale. Prima della gara ricontrolla tutti i presenti
    sotto lo stesso lock: esattamente 15 dopo la prima gara, massimo 15 alla
    prima. Mai controllare gli assenti. Gara, READY ed eventi condividono commit
    o rollback. Nessun retry e nessun completamento automatico del mazzo.
    """
    race_id = None
    with draft_mutation(db, preparation_id, user_id, expected_version) as work:
        pilot = _pilot(db, work, pilot_id)
        work.state = set_ready(work.state, user_id, pilot_id, ready,
                              parse_cards(work.decks[pilot.game_deck_id].cards))
        if all_ready(work.state):
            present = [p for p in work.state.participants if p.present]
            if not 1 <= len(present) <= MAX_RACE_PILOTS:
                raise DraftPreparationError("Numero di presenti non valido")
            for participant in present:
                current = _pilot(db, work, participant.pilot_id)
                work.state = set_ready(work.state, participant.user_id, participant.pilot_id, True,
                    parse_cards(work.decks[current.game_deck_id].cards))
            race_id = _stage_race(db, work.row.championship_id).id
            work.remove_preparation = True
    return DraftCompletion(None if race_id is not None else preparation_id, race_id)


def already_disputed(db: Session, preparation_id: int, user_id: int,
                     expected_version: int) -> DraftCompletion:
    """Crea una gara normale dal modal iniziale, senza draft, READY o vincolo 15.

    Solo il creatore ancora gestore, in attendance prima di ogni estrazione o
    modifica mazzo. Conserva campionato aperto, lock e unica gara non conclusa.
    Non inserisce risultati e non termina la gara. Il contesto segnala chiusura.
    """
    with draft_mutation(db, preparation_id, user_id, expected_version, creator_only=True) as work:
        if work.state.phase != "attendance":
            raise DraftPreparationError("Percorso disponibile soltanto dal modal iniziale")
        race_id = _stage_race(db, work.row.championship_id).id
        work.remove_preparation = True
    return DraftCompletion(None, race_id)
