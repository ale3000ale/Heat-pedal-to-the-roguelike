"""Estrazione casuale di mappa ed evento per la prossima gara."""
import json
import secrets
from pathlib import Path

from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import Session

from app.config import MEDIA_DIR
from app.db.models.championship import Championship
from app.schemas.core.events import EventCreate
from app.services.championship.championships import ChampionshipClosedError, get_championship
from app.services.core.event_log import append_event
from app.services.core.sqlite_write_lock import SQLiteWriteLockError, acquire_sqlite_write_lock
from app.services.draft.draft_guards import require_no_draft
from app.services.race.races import RaceInProgressError, has_race_in_progress

MAP_DIR = "board/maps"
EVENT_DIR = "board/events"
IMAGE_SUFFIX = ".webp"
MAPS_FILENAME = "maps.json"
JSON_DIR_NAMES = ("json", "JSON")
_choose = secrets.choice


class RaceSetupFilesError(Exception):
    """Mappa o evento non disponibili sul disco."""


class RaceSetupAlreadyExistsError(Exception):
    """Il setup della prossima gara è già stato preparato."""


class RaceSetupConflictError(Exception):
    """Il lock non consente un setup coerente; nessun retry automatico."""


def _maps_json_path() -> Path:
    """Trova maps.json accettando sia backend/json sia backend/JSON."""
    base = MEDIA_DIR.parent
    for name in JSON_DIR_NAMES:
        candidate = base / name / MAPS_FILENAME
        if candidate.is_file():
            return candidate
    return base / JSON_DIR_NAMES[0] / MAPS_FILENAME


def _normalized_path(value: object) -> str:
    return value.replace("\\", "/").strip().lower() if isinstance(value, str) else ""


def _non_negative_int(value: object) -> int | None:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        return None
    return value


def map_stats(
    map_path: str | None,
) -> tuple[int | None, int | None, int | None, int | None]:
    """Restituisce stress, heat, curve e caselle della mappa estratta da maps.json."""
    target = _normalized_path(map_path)
    if not target:
        return None, None, None, None
    try:
        items = json.loads(_maps_json_path().read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError):
        return None, None, None, None
    if not isinstance(items, list):
        return None, None, None, None
    for item in items:
        if not isinstance(item, dict):
            continue
        if _normalized_path(item.get("image")) != target:
            continue
        return (
            _non_negative_int(item.get("stress")),
            _non_negative_int(item.get("heat")),
            _non_negative_int(item.get("curve")),
            _non_negative_int(item.get("caselle")),
        )
    return None, None, None, None


def map_card_counts(map_path: str | None) -> tuple[int | None, int | None]:
    """Restituisce stress e heat della mappa estratta, letti da maps.json."""
    stress, heat, _, _ = map_stats(map_path)
    return stress, heat


def _draw(relative_dir: str) -> str:
    """Restituisce il percorso relativo a media di un'immagine casuale.

    Parametri: cartella sotto media. Ritorna un percorso con separatori '/'.
    RaceSetupFilesError se la cartella non esiste o non contiene WebP.
    La scelta usa il generatore sicuro del modulo, sostituibile nei test.
    """
    directory = MEDIA_DIR / relative_dir
    names = (
        sorted(
            path.relative_to(MEDIA_DIR).as_posix()
            for path in directory.iterdir()
            if path.is_file() and path.suffix.lower() == IMAGE_SUFFIX
        )
        if directory.is_dir()
        else []
    )
    if not names:
        raise RaceSetupFilesError(f"Nessuna immagine disponibile in {relative_dir}")
    return _choose(names)


def prepare_next_race(db: Session, championship_id: int) -> Championship:
    """Prepara mappa ed evento della prossima gara in una transazione protetta.

    Parametri: sessione e campionato. Ritorna il campionato aggiornato. Rifiuta
    campionato chiuso, gara non conclusa, draft attiva o setup già presente.
    Il segnale SSE, i percorsi e il commit condividono la stessa transazione;
    errori di dominio, lock o SQL causano rollback senza retry.
    """
    try:
        acquire_sqlite_write_lock(db)
        championship = get_championship(db, championship_id)
        if championship.is_closed:
            raise ChampionshipClosedError
        if has_race_in_progress(db, championship_id):
            raise RaceInProgressError
        require_no_draft(db, championship_id)
        if championship.next_map_path or championship.next_event_path:
            raise RaceSetupAlreadyExistsError("Il setup della prossima gara è già pronto")
        # Lettura delle immagini dentro il lock, prima di qualunque scrittura.
        map_path = _draw(MAP_DIR)
        event_path = _draw(EVENT_DIR)
        championship.next_map_path = map_path
        championship.next_event_path = event_path
        append_event(db, EventCreate(
            type="championship.setup_changed", championship_id=championship_id
        ))
        db.commit()
        db.refresh(championship)
        return championship
    except SQLiteWriteLockError as exc:
        db.rollback()
        raise RaceSetupConflictError from exc
    except OperationalError as exc:
        db.rollback()
        code = getattr(exc.orig, "sqlite_errorcode", 0) or 0
        if (code & 255) in (5, 6):
            raise RaceSetupConflictError from exc
        raise
    except Exception:
        db.rollback()
        raise
