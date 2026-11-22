"""Web app locale per importare immagini di mappe ed eventi."""
import re
import shutil
import tempfile
import threading
import uuid
from contextlib import asynccontextmanager
from dataclasses import dataclass
from pathlib import Path

from fastapi import FastAPI, File, HTTPException, UploadFile
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

ROOT = Path(__file__).resolve().parents[2]
STATIC_DIR = Path(__file__).resolve().parent / "static"
ID_PATTERN = re.compile(r"^[0-9a-f]{32}$")


def default_board_dir() -> Path:
    return ROOT / "backend" / "media" / "board"


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


def create_app(board_dir: Path | None = None, staging_dir: Path | None = None) -> FastAPI:
    """Crea l'app; board_dir e staging_dir servono anche ai test."""
    board_dir = (Path(board_dir) if board_dir else default_board_dir()).resolve()
    if not board_dir.is_dir():
        raise ImageToolError(f"Cartella non trovata: {board_dir}")
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

    app = FastAPI(title="Immagini di mappe ed eventi", lifespan=lifespan)
    app.state.board_dir = board_dir
    app.state.staging = staging
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

    @app.get("/")
    def index():
        return FileResponse(STATIC_DIR / "index.html")

    @app.get("/api/destinations")
    def destinations():
        found = list_destinations(board_dir)
        return {"destinations": found, "default": default_destination(found)}

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
            destination = resolve_destination(board_dir, request.destination)
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
                    "destination": destination.relative_to(board_dir).as_posix(),
                    "path": target.relative_to(board_dir).as_posix(),
                }
            )
        return {"saved": saved, "errors": errors}

    return app
