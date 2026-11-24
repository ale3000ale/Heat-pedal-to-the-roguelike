"""Pool per campionato di mappe ed eventi.

Il catalogo completo è letto da ``JSON/maps.json`` e ``JSON/events.json``; sul
campionato si salvano soltanto gli ID ancora disponibili. La colonna NULL indica
una pool mai inizializzata, mentre ``[]`` indica una pool esaurita.
"""
import json
import secrets
from dataclasses import dataclass
from pathlib import Path

from app.config import MEDIA_DIR
from app.db.models.championship import Championship

MAPS_FILENAME = "maps.json"
EVENTS_FILENAME = "events.json"
JSON_DIR_NAMES = ("json", "JSON")

POOL_KINDS = ("mappe", "eventi")
POOL_COLUMNS = {"mappe": "map_pool_ids", "eventi": "event_pool_ids"}
CATALOG_FILES = {"mappe": MAPS_FILENAME, "eventi": EVENTS_FILENAME}
POOL_LABELS = {"mappe": "mappa", "eventi": "evento"}

# Sostituibile nei test, come la scelta delle carte modifiche.
_choose = secrets.choice


class BoardPoolKindError(ValueError):
    """Tipo di pool non riconosciuto."""


class BoardPoolEmptyError(Exception):
    """La pool non ha più carte disponibili."""


class BoardPoolFilesError(Exception):
    """Le immagini delle carte della pool non sono disponibili."""


@dataclass(frozen=True)
class BoardPoolField:
    label: str
    value: str


@dataclass(frozen=True)
class BoardPoolCard:
    id: int
    nome: str
    image: str
    in_pool: bool
    fields: tuple[BoardPoolField, ...]


def _column(kind: str) -> str:
    try:
        return POOL_COLUMNS[kind]
    except KeyError as exc:
        raise BoardPoolKindError(kind) from exc


def _json_path(filename: str) -> Path:
    base = MEDIA_DIR.parent
    for name in JSON_DIR_NAMES:
        candidate = base / name / filename
        if candidate.is_file():
            return candidate
    return base / JSON_DIR_NAMES[0] / filename


def _catalog(kind: str) -> list[dict]:
    """Voci valide del catalogo, con ID univoci e campi minimi presenti."""
    _column(kind)
    filename = CATALOG_FILES[kind]
    try:
        items = json.loads(_json_path(filename).read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError):
        return []
    if not isinstance(items, list):
        return []
    catalog: list[dict] = []
    seen: set[int] = set()
    for item in items:
        if not isinstance(item, dict):
            continue
        card_id = item.get("id")
        image = item.get("image")
        nome = item.get("nome")
        if isinstance(card_id, bool) or not isinstance(card_id, int) or card_id <= 0:
            continue
        if not isinstance(image, str) or not image.strip():
            continue
        if not isinstance(nome, str) or not nome.strip():
            continue
        if card_id in seen:
            continue
        seen.add(card_id)
        catalog.append(item)
    return catalog


def _pool_ids(championship: Championship, kind: str) -> list[int] | None:
    """ID della pool; None se non è mai stata inizializzata o è illeggibile."""
    raw = getattr(championship, _column(kind))
    if raw is None:
        return None
    try:
        values = json.loads(raw)
    except (TypeError, json.JSONDecodeError):
        return None
    if not isinstance(values, list):
        return None
    ids: list[int] = []
    for value in values:
        if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
            continue
        if value not in ids:
            ids.append(value)
    return ids


def _write_ids(championship: Championship, kind: str, ids: list[int]) -> None:
    setattr(championship, _column(kind), json.dumps(ids))


def initialize_pools(championship: Championship) -> None:
    """Inizializza le pool mai create con tutti gli ID del catalogo corrente."""
    for kind in POOL_KINDS:
        if _pool_ids(championship, kind) is not None:
            continue
        ids = [item["id"] for item in _catalog(kind)]
        if ids:
            _write_ids(championship, kind, ids)


def _available_ids(championship: Championship, kind: str) -> list[int]:
    ids = _pool_ids(championship, kind)
    if ids is not None:
        return ids
    return [item["id"] for item in _catalog(kind)]


def _normalized_path(value: object) -> str:
    return value.replace("\\", "/").strip().lower() if isinstance(value, str) else ""


def _find_by_image(kind: str, image_path: str) -> dict | None:
    target = _normalized_path(image_path)
    if not target:
        return None
    for item in _catalog(kind):
        if _normalized_path(item.get("image")) == target:
            return item
    return None


def draw_card(championship: Championship, kind: str) -> dict:
    """Estrae una carta disponibile dalla pool, inizializzandola se serve.

    Non rimuove la carta: il consumo avviene alla prima registrazione dei risultati.
    BoardPoolEmptyError se la pool è vuota, BoardPoolFilesError se nessuna immagine
    delle carte rimaste esiste su disco.
    """
    _column(kind)
    initialize_pools(championship)
    ids = _pool_ids(championship, kind) or []
    by_id = {item["id"]: item for item in _catalog(kind)}
    available = [
        by_id[card_id]
        for card_id in ids
        if card_id in by_id and (MEDIA_DIR / by_id[card_id]["image"]).is_file()
    ]
    if not ids:
        raise BoardPoolEmptyError(f"Nessuna {POOL_LABELS[kind]} rimasta nella pool")
    if not available:
        raise BoardPoolFilesError(
            f"Nessuna immagine disponibile per la pool {POOL_LABELS[kind]}"
        )
    return _choose(available)


def consume_setup(championship: Championship) -> None:
    """Toglie dalla pool la mappa e l'evento del setup appena disputato."""
    for kind, attribute in (("mappe", "next_map_path"), ("eventi", "next_event_path")):
        image = getattr(championship, attribute)
        if not image:
            continue
        card = _find_by_image(kind, image)
        if card is None:
            continue
        ids = _pool_ids(championship, kind)
        if ids is None or card["id"] not in ids:
            continue
        _write_ids(championship, kind, [card_id for card_id in ids if card_id != card["id"]])


def _value_text(value: object) -> str | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, int):
        return str(value)
    if isinstance(value, str):
        text = value.strip()
        return text or None
    if isinstance(value, list):
        parts = [str(part) for part in value if isinstance(part, int) and not isinstance(part, bool)]
        return " · ".join(parts) if parts else None
    return None


def _fields(kind: str, item: dict) -> tuple[BoardPoolField, ...]:
    labels = (
        ("giri", "Giri"),
        ("curve", "Curve"),
        ("caselle", "Caselle"),
        ("stress", "Stress"),
        ("heat", "Heat"),
        ("sezioni", "Sezioni"),
    ) if kind == "mappe" else (
        ("effetto", "Effetto"),
        ("sponsor", "Sponsor"),
        ("fotografi", "Fotografi"),
    )
    fields: list[BoardPoolField] = []
    for key, label in labels:
        value = _value_text(item.get(key))
        if key == "effetto" and value is not None:
            # L'effetto degli eventi ha descrizione e codifica su due righe separate:
            # nella vista si mostra solo la prima stringa.
            value = value.split("\n", 1)[0].strip() or None
        if value is not None:
            fields.append(BoardPoolField(label=label, value=value))
    return tuple(fields)


def pool_view(championship: Championship, kind: str) -> list[BoardPoolCard]:
    """Tutte le carte del catalogo con l'indicazione se sono ancora in pool."""
    in_pool = set(_available_ids(championship, kind))
    return [
        BoardPoolCard(
            id=item["id"],
            nome=item["nome"],
            image=item["image"],
            in_pool=item["id"] in in_pool,
            fields=_fields(kind, item),
        )
        for item in _catalog(kind)
    ]
