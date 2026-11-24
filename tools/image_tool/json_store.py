"""Archiviazione e validazione dei JSON di mappe ed eventi.

I file vivono in ``backend/json``; i percorsi ``image`` sono relativi a
``backend/media``, come quelli usati dal backend. Nessuna dipendenza nuova:
json, os e threading appartengono alla libreria standard, Pydantic e già
presente nel progetto.
"""
import json
import os
import tempfile
import threading
from pathlib import Path
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, StrictInt, ValidationError, field_validator

KINDS = ("events", "maps")
FIELD_NAMES = {
    "events": ("nome", "image", "effetto", "sponsor", "fotografi"),
    "maps": ("nome", "image", "giri", "curve", "caselle", "stress", "heat", "sezioni"),
}
IMAGE_SUFFIXES = frozenset({".webp", ".png", ".jpg", ".jpeg"})
_LOCK = threading.RLock()


class StoreError(ValueError):
    """Errore leggibile restituito dallo strumento; status_code per l'API."""

    def __init__(self, message: str, status_code: int = 400):
        super().__init__(message)
        self.status_code = status_code


def _strip(value: Any) -> Any:
    if isinstance(value, str):
        return value.strip()
    return value


def _required(value: Any) -> Any:
    value = _strip(value)
    if not isinstance(value, str) or not value:
        raise ValueError("Il campo non può essere vuoto")
    return value


def _valid_id(value: Any) -> bool:
    return isinstance(value, int) and not isinstance(value, bool) and value > 0


def _valid_number(value: Any) -> bool:
    return isinstance(value, int) and not isinstance(value, bool) and value >= 0


def _valid_sections(value: Any) -> bool:
    return isinstance(value, list) and all(_valid_number(entry) for entry in value)


class EventItem(BaseModel):
    """Una riga del JSON degli eventi."""

    model_config = ConfigDict(extra="forbid")

    id: StrictInt = Field(default=0, ge=0)
    nome: str
    image: str
    effetto: str
    sponsor: StrictInt = Field(ge=0)
    fotografi: str

    @field_validator("nome", "effetto", "fotografi")
    @classmethod
    def campi_obbligatori(cls, value: Any) -> Any:
        return _required(value)


class MapItem(BaseModel):
    """Una riga del JSON delle mappe."""

    model_config = ConfigDict(extra="forbid")

    id: StrictInt = Field(default=0, ge=0)
    nome: str
    image: str
    giri: StrictInt = Field(ge=0)
    curve: StrictInt = Field(ge=0)
    caselle: StrictInt = Field(ge=0)
    stress: StrictInt = Field(ge=0)
    heat: StrictInt = Field(ge=0)
    sezioni: list[StrictInt]

    @field_validator("nome")
    @classmethod
    def nome_obbligatorio(cls, value: Any) -> Any:
        return _required(value)

    @field_validator("sezioni")
    @classmethod
    def sezioni_valide(cls, value: Any) -> Any:
        if not _valid_sections(value):
            raise ValueError("Le sezioni devono essere numeri interi non negativi")
        return value


def model_for(kind: str) -> type[EventItem] | type[MapItem]:
    """Modello Pydantic associato a una delle due colezioni note."""
    if kind == "events":
        return EventItem
    if kind == "maps":
        return MapItem
    raise StoreError(f"Collezione sconosciuta: {kind}", 404)


def next_id(items: list[dict[str, Any]]) -> int:
    """Prossimo ID libero, incrementale rispetto al massimo presente."""
    return max((item.get("id", 0) for item in items), default=0) + 1


def _normalize_ids(items: list[dict[str, Any]]) -> bool:
    """Rende univoci gli ID letti; ritorna True se ha dovuto cambiarli."""
    next_free = max((item["id"] for item in items if _valid_id(item.get("id"))), default=0) + 1
    seen: set[int] = set()
    changed = False
    for item in items:
        current = item.get("id")
        if not _valid_id(current) or current in seen:
            item["id"] = next_free
            next_free += 1
            changed = True
            current = item["id"]
        seen.add(current)
    return changed


def file_path(json_dir: Path, kind: str) -> Path:
    """Percorso del file JSON della collezione, senza scrivere nulla."""
    model_for(kind)
    return json_dir / f"{kind}.json"


def _repaired_field(field: str, value: Any, media_dir: Path) -> Any:
    """Ritorna il valore valido oppure None, senza sollevare errori."""
    if field == "image":
        try:
            return validate_image_path(value, media_dir)
        except StoreError:
            return None
    if field in ("nome", "effetto", "fotografi"):
        stripped = _strip(value)
        return stripped if isinstance(stripped, str) and stripped else None
    if field in ("sponsor", "giri", "curve", "caselle", "stress", "heat"):
        return value if _valid_number(value) else None
    if field == "sezioni":
        return [entry for entry in value] if _valid_sections(value) else None
    return value


def repair_items(json_dir: Path, kind: str, media_dir: Path) -> tuple[list[dict[str, Any]], bool]:
    """Legge, ripara e riscrive il JSON; ritorna elementi e flag di modifica."""
    model_for(kind)
    path = file_path(json_dir, kind)
    with _LOCK:
        if not path.exists():
            return [], False
        try:
            raw = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, UnicodeError, json.JSONDecodeError) as exc:
            raise StoreError(f"File JSON non valido: {path.name} ({exc})", 500) from exc
        if not isinstance(raw, list):
            raise StoreError(f"Il file {path.name} deve contenere un elenco di oggetti", 500)

        expected = {"id", *FIELD_NAMES[kind]}
        changed = False
        items: list[dict[str, Any]] = []
        for entry in raw:
            if not isinstance(entry, dict):
                entry = {}
                changed = True
            item = dict(entry)
            for key in list(item):
                if key not in expected:
                    del item[key]
                    changed = True
            for field in FIELD_NAMES[kind]:
                if field not in item:
                    item[field] = None
                    changed = True
                    continue
                repaired = _repaired_field(field, item[field], media_dir)
                if repaired != item[field]:
                    item[field] = repaired
                    changed = True
            items.append(item)
        if _normalize_ids(items):
            changed = True
        if changed:
            save_items(json_dir, kind, items)
        return items, changed


def load_items(json_dir: Path, kind: str, media_dir: Path) -> list[dict[str, Any]]:
    """Legge il JSON riparando i campi non validi; file assente significa elenco vuoto."""
    items, _ = repair_items(json_dir, kind, media_dir)
    return items


def save_items(json_dir: Path, kind: str, items: list[dict[str, Any]]) -> None:
    """Sovrascrive il JSON in modo atomico, con UTF-8 e indentazione stabile."""
    path = file_path(json_dir, kind)
    payload = json.dumps(items, ensure_ascii=False, indent=2) + "\n"
    with _LOCK:
        json_dir.mkdir(parents=True, exist_ok=True)
        temporary = None
        try:
            with tempfile.NamedTemporaryFile(
                mode="w", encoding="utf-8", dir=json_dir, prefix=".tmp-", delete=False
            ) as handle:
                temporary = Path(handle.name)
                handle.write(payload)
                handle.flush()
                os.fsync(handle.fileno())
            os.replace(temporary, path)
        except OSError as exc:
            if temporary is not None:
                temporary.unlink(missing_ok=True)
            raise StoreError(f"Salvataggio di {path.name} non riuscito: {exc}", 500) from exc


def validate_image_path(image: Any, media_dir: Path) -> str:
    """Accetta solo un file immagine esistente dentro backend/media.

    Parametri: valore del campo image e radice media. Ritorna il percorso
    normalizzato con separatori '/'. Solleva StoreError per percorsi assoluti,
    esterni, inesistenti o con estensione non immagine.
    """
    value = _strip(image)
    if not isinstance(value, str) or not value:
        raise StoreError("Indica il path di un'immagine")
    candidate = Path(value.replace("\\", "/"))
    if ":" in candidate.as_posix() or candidate.is_absolute():
        raise StoreError("Il path deve essere relativo a backend/media")
    parts = candidate.parts
    if not parts or any(part in ("", ".", "..") for part in parts):
        raise StoreError("Il path deve stare dentro backend/media")
    root = media_dir.resolve()
    target = (root / candidate).resolve()
    if not target.is_relative_to(root):
        raise StoreError("Il path deve stare dentro backend/media")
    if not target.is_file():
        raise StoreError("L'immagine indicata non esiste")
    if target.suffix.lower() not in IMAGE_SUFFIXES:
        raise StoreError("Il file indicato non è un'immagine supportata")
    return candidate.as_posix()


def find_duplicate(
    items: list[dict[str, Any]], item: dict[str, Any], exclude_index: int | None = None
) -> str | None:
    """Restituisce 'nome' o 'image' se il valore è già presente, altrimenti None."""
    name = item["nome"].casefold()
    image = item["image"].replace("\\", "/").casefold()
    for index, existing in enumerate(items):
        if index == exclude_index:
            continue
        if existing["nome"].casefold() == name:
            return "nome"
        if existing["image"].replace("\\", "/").casefold() == image:
            return "image"
    return None


def validate_item(
    kind: str,
    payload: Any,
    media_dir: Path,
    items: list[dict[str, Any]],
    exclude_index: int | None = None,
    item_id: int | None = None,
) -> dict[str, Any]:
    """Valida una riga, assegna l'ID, normalizza il path e rifiuta i duplicati."""
    model = model_for(kind)
    try:
        data = model.model_validate(payload).model_dump()
    except ValidationError as exc:
        first = exc.errors()[0]
        field = ".".join(str(part) for part in first["loc"]) or "dati"
        raise StoreError(f"Campo {field} non valido: {first['msg']}") from exc
    data["id"] = item_id if item_id is not None else next_id(items)
    data["image"] = validate_image_path(data["image"], media_dir)
    if find_duplicate(items, data, exclude_index) is not None:
        raise StoreError("errore elemento già esistente", 409)
    return data
