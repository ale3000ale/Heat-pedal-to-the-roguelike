"""Web app locale per media e JSON di mappe ed eventi."""
import json
import os
import re
import shutil
import tempfile
import threading
import uuid
from contextlib import asynccontextmanager
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from urllib.parse import quote

from fastapi import Body, FastAPI, File, HTTPException, UploadFile
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from tools.image_tool.conversion import (
    DEFAULT_NAME,
    MAX_UPLOAD_BYTES,
    ImageToolError,
    default_destination,
    list_destinations,
    load_image,
    resolve_destination,
    save_webp,
    slugify,
    unique_filename,
)
from tools.image_tool.json_store import (
    IMAGE_SUFFIXES,
    StoreError,
    file_path,
    load_items,
    model_for,
    next_id,
    repair_items,
    save_items,
    validate_item,
)

ROOT = Path(__file__).resolve().parents[2]
STATIC_DIR = Path(__file__).resolve().parent / "static"
DEFAULT_MEDIA_DIR = ROOT / "backend" / "media"
DEFAULT_JSON_DIR = ROOT / "backend" / "json"
DEFAULT_STATE_PATH = Path(__file__).resolve().parent / "state.json"
STATE_KINDS = ("events", "maps")
ID_PATTERN = re.compile(r"^[0-9a-f]{32}$")
_STATE_LOCK = threading.Lock()


def _store_error(exc: StoreError) -> HTTPException:
    return HTTPException(status_code=exc.status_code, detail=str(exc))


def _check_state_kind(kind: str) -> None:
    if kind not in STATE_KINDS:
        raise ImageToolError("Tipo di JSON non valido")


def read_last_folder(state_path: Path, kind: str) -> str:
    """Ultima cartella ricordata per un JSON; file assente o rotto significa radice."""
    _check_state_kind(kind)
    try:
        with _STATE_LOCK:
            if not state_path.is_file():
                return ""
            raw = json.loads(state_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError):
        return ""
    if not isinstance(raw, dict):
        return ""
    value = raw.get(kind, "")
    return value if isinstance(value, str) else ""


def write_last_folder(state_path: Path, kind: str, path: str) -> str:
    """Salva la cartella per un JSON senza toccare le altre, con scrittura atomica."""
    _check_state_kind(kind)
    value = (path or "").strip().replace("\\", "/")
    with _STATE_LOCK:
        state: dict[str, Any] = {}
        if state_path.is_file():
            try:
                loaded = json.loads(state_path.read_text(encoding="utf-8"))
                if isinstance(loaded, dict):
                    state = loaded
            except (OSError, UnicodeError, json.JSONDecodeError):
                pass
        state[kind] = value
        payload = json.dumps(state, ensure_ascii=False, indent=2) + "\n"
        temporary = None
        try:
            with tempfile.NamedTemporaryFile(
                mode="w", encoding="utf-8", dir=state_path.parent, prefix=".state-", delete=False
            ) as handle:
                temporary = Path(handle.name)
                handle.write(payload)
                handle.flush()
                os.fsync(handle.fileno())
            os.replace(temporary, state_path)
        except OSError as exc:
            if temporary is not None:
                temporary.unlink(missing_ok=True)
            raise ImageToolError(f"Salvataggio dello stato non riuscito: {exc}") from exc
    return value


@dataclass
class StagedImage:
    path: Path
    suggested: str
    original: str
    width: int
    height: int
    size: int


class Staging:
    """Immagini convertite in attesa di essere salvate nella destinazione."""

    def __init__(self, directory: Path):
        self.directory = directory
        self.items: dict[str, StagedImage] = {}
        self.lock = threading.Lock()

    def add(self, image, original: str) -> tuple[str, StagedImage]:
        staged_id = uuid.uuid4().hex
        path = self.directory / f"{staged_id}.webp"
        width, height = save_webp(image, path)
        item = StagedImage(
            path=path,
            suggested=Path(original).stem or DEFAULT_NAME,
            original=original,
            width=width,
            height=height,
            size=path.stat().st_size,
        )
        with self.lock:
            self.items[staged_id] = item
        return staged_id, item

    def get(self, staged_id: str) -> StagedImage | None:
        if not ID_PATTERN.fullmatch(staged_id):
            return None
        with self.lock:
            return self.items.get(staged_id)

    def remove(self, staged_id: str) -> StagedImage | None:
        with self.lock:
            return self.items.pop(staged_id, None)

    def discard(self, staged_id: str) -> bool:
        item = self.remove(staged_id)
        if item is None:
            return False
        item.path.unlink(missing_ok=True)
        return True


class SaveItem(BaseModel):
    id: str
    name: str | None = None


class SaveRequest(BaseModel):
    destination: str
    items: list[SaveItem]


class LastFolderRequest(BaseModel):
    kind: str
    path: str = ""


def browse_media(root: Path, value: str = "") -> dict[str, Any]:
    """Contenuto immediato di una cartella dentro media, senza uscirne."""
    root = root.resolve()
    value = (value or "").strip().replace("\\", "/")
    if ":" in value:
        raise ImageToolError("La cartella deve essere relativa a backend/media")
    candidate = Path(value) if value else Path()
    if candidate.is_absolute() or candidate.drive:
        raise ImageToolError("La cartella deve essere relativa a backend/media")
    parts = candidate.parts
    if any(part in ("", ".", "..") or part.startswith(".") for part in parts):
        raise ImageToolError("La cartella deve stare dentro backend/media")
    target = root if not value else (root / candidate).resolve()
    if target != root and not target.is_relative_to(root):
        raise ImageToolError("La cartella deve stare dentro backend/media")
    if not target.is_dir():
        raise FileNotFoundError("Cartella non trovata")

    directories = []
    images = []
    for entry in sorted(target.iterdir(), key=lambda item: item.name.casefold()):
        if entry.name.startswith("."):
            continue
        relative = entry.relative_to(root).as_posix()
        if entry.is_dir():
            directories.append({"path": relative, "name": entry.name})
        elif entry.is_file() and entry.suffix.lower() in IMAGE_SUFFIXES:
            images.append(
                {"path": relative, "name": entry.name, "url": "/media/" + quote(relative)}
            )
    relative = "" if target == root else target.relative_to(root).as_posix()
    parent = None
    if relative:
        parent_path = Path(relative).parent
        parent = "" if parent_path == Path(".") else parent_path.as_posix()
    return {
        "path": relative,
        "parent": parent,
        "directories": directories,
        "images": images,
    }


def create_app(
    media_dir: Path | None = None,
    json_dir: Path | None = None,
    staging_dir: Path | None = None,
    state_path: Path | None = None,
) -> FastAPI:
    """Crea l'app; le cartelle servono anche ai test isolati."""
    media_dir = (Path(media_dir) if media_dir else DEFAULT_MEDIA_DIR).resolve()
    json_dir = (Path(json_dir) if json_dir else DEFAULT_JSON_DIR).resolve()
    state_path = (Path(state_path) if state_path else DEFAULT_STATE_PATH).resolve()
    if not media_dir.is_dir():
        raise ImageToolError(f"Cartella media non trovata: {media_dir}")
    json_dir.mkdir(parents=True, exist_ok=True)
    owns_staging = staging_dir is None
    staging_dir = (
        Path(staging_dir) if staging_dir else Path(tempfile.mkdtemp(prefix="heat-image-tool-"))
    )
    staging_dir.mkdir(parents=True, exist_ok=True)
    staging = Staging(staging_dir)

    @asynccontextmanager
    async def lifespan(_app: FastAPI):
        yield
        if owns_staging:
            shutil.rmtree(staging_dir, ignore_errors=True)

    app = FastAPI(title="Strumento di sviluppo Heat", lifespan=lifespan)
    app.state.media_dir = media_dir
    app.state.json_dir = json_dir
    app.state.staging = staging
    app.state.state_path = state_path
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
    app.mount("/media", StaticFiles(directory=media_dir), name="media")

    @app.get("/")
    def index():
        return FileResponse(STATIC_DIR / "index.html")

    @app.get("/api/destinations")
    def destinations():
        found = list_destinations(media_dir)
        return {"destinations": found, "default": default_destination(found)}

    @app.get("/api/media/browse")
    def media_browse(path: str = ""):
        try:
            return browse_media(media_dir, path)
        except ImageToolError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
        except FileNotFoundError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc

    @app.get("/api/media/last-folder")
    def media_last_folder(kind: str):
        try:
            stored = read_last_folder(state_path, kind)
            if stored:
                browse_media(media_dir, stored)
            return {"path": stored}
        except ImageToolError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
        except (FileNotFoundError, OSError):
            return {"path": ""}

    @app.post("/api/media/last-folder")
    def media_save_last_folder(payload: LastFolderRequest):
        try:
            browse_media(media_dir, payload.path)
            return {"path": write_last_folder(state_path, payload.kind, payload.path)}
        except ImageToolError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
        except FileNotFoundError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc

    @app.get("/api/data/{kind}")
    def read_data(kind: str):
        try:
            path = file_path(json_dir, kind)
            created = not path.exists()
            items, repaired = repair_items(json_dir, kind, media_dir)
            if created:
                save_items(json_dir, kind, items)
            return {"items": items, "created": created, "repaired": repaired}
        except StoreError as exc:
            raise _store_error(exc) from exc

    @app.post("/api/data/{kind}")
    def create_data(kind: str, payload: dict[str, Any] = Body(...)):
        try:
            items = load_items(json_dir, kind, media_dir)
            items.append(
                validate_item(kind, payload, media_dir, items, item_id=next_id(items))
            )
            save_items(json_dir, kind, items)
            return {"items": items}
        except StoreError as exc:
            raise _store_error(exc) from exc

    @app.put("/api/data/{kind}/{index}")
    def update_data(kind: str, index: int, payload: dict[str, Any] = Body(...)):
        try:
            model_for(kind)
            items = load_items(json_dir, kind, media_dir)
            if index < 0 or index >= len(items):
                raise StoreError("Elemento non trovato", 404)
            items[index] = validate_item(
                kind,
                payload,
                media_dir,
                items,
                exclude_index=index,
                item_id=items[index]["id"],
            )
            save_items(json_dir, kind, items)
            return {"items": items}
        except StoreError as exc:
            raise _store_error(exc) from exc

    @app.post("/api/upload")
    async def upload(files: list[UploadFile] = File(...)):
        items = []
        errors = []
        for file in files:
            original = Path((file.filename or DEFAULT_NAME).replace("\\", "/")).name
            try:
                data = await file.read()
                if len(data) > MAX_UPLOAD_BYTES:
                    raise ImageToolError("File troppo grande (massimo 25 MB)")
                image = load_image(data)
                staged_id, item = staging.add(image, original)
            except (ValueError, OSError) as exc:
                errors.append({"filename": original, "message": str(exc)})
            else:
                items.append(
                    {
                        "id": staged_id,
                        "original": item.original,
                        "suggested": item.suggested,
                        "width": item.width,
                        "height": item.height,
                        "bytes": item.size,
                        "preview_url": f"/api/staged/{staged_id}",
                    }
                )
            finally:
                await file.close()
        return {"items": items, "errors": errors}

    @app.get("/api/staged/{staged_id}")
    def staged(staged_id: str):
        item = staging.get(staged_id)
        if item is None or not item.path.is_file():
            raise HTTPException(status_code=404, detail="Anteprima non disponibile")
        return FileResponse(
            item.path, media_type="image/webp", headers={"Cache-Control": "no-store"}
        )

    @app.delete("/api/staged/{staged_id}")
    def discard(staged_id: str):
        if not staging.discard(staged_id):
            raise HTTPException(status_code=404, detail="Anteprima non disponibile")
        return {"discarded": True}

    @app.post("/api/save")
    def save(request: SaveRequest):
        if not request.items:
            raise HTTPException(status_code=400, detail="Nessuna immagine da salvare")
        try:
            destination = resolve_destination(media_dir, request.destination)
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
        try:
            destination.mkdir(parents=True, exist_ok=True)
        except OSError as exc:
            raise HTTPException(
                status_code=400, detail=f"Cartella non creabile: {exc}"
            ) from exc
        saved = []
        errors = []
        for entry in request.items:
            item = staging.get(entry.id)
            if item is None:
                errors.append({"id": entry.id, "message": "Immagine non più disponibile"})
                continue
            name = (entry.name or "").strip() or item.suggested
            filename = unique_filename(destination, slugify(name))
            target = destination / filename
            try:
                shutil.move(str(item.path), str(target))
            except OSError as exc:
                errors.append(
                    {"id": entry.id, "message": f"Salvataggio non riuscito: {exc}"}
                )
                continue
            staging.remove(entry.id)
            saved.append(
                {
                    "id": entry.id,
                    "file": filename,
                    "destination": destination.relative_to(media_dir).as_posix(),
                    "path": target.relative_to(media_dir).as_posix(),
                }
            )
        return {"saved": saved, "errors": errors}

    return app
