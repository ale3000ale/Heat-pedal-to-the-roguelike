"""Conversione e nomi per lo strumento immagini di mappe ed eventi."""
import re
import unicodedata
from io import BytesIO
from pathlib import Path

from PIL import Image, ImageOps, UnidentifiedImageError

# Stessa scatola massima delle carte: 5,6 x 8,7 cm a 100 pixel per centimetro.
MAX_SIZE = (560, 870)
MAX_UPLOAD_BYTES = 25 * 1024 * 1024
DEFAULT_NAME = "immagine"


class ImageToolError(ValueError):
    """File non valido, nome o destinazione non accettabili."""


def slugify(name: str) -> str:
    # Nome di file sicuro: senza accenti, minuscolo, solo lettere, numeri e trattini.
    ascii_text = unicodedata.normalize("NFKD", name).encode("ascii", "ignore").decode()
    slug = re.sub(r"[^a-z0-9]+", "-", ascii_text.lower()).strip("-")
    return slug or DEFAULT_NAME


def unique_filename(directory: Path, slug: str) -> str:
    # Se esiste già un file con questo nome aggiunge -2, -3, ...
    candidate = f"{slug}.webp"
    number = 2
    while (directory / candidate).exists():
        candidate = f"{slug}-{number}.webp"
        number += 1
    return candidate


def load_image(data: bytes) -> Image.Image:
    # Legge un'immagine dai byte caricati; errore leggibile se il file non è valido.
    try:
        image = Image.open(BytesIO(data))
        image.load()
    except (UnidentifiedImageError, OSError, Image.DecompressionBombError) as exc:
        raise ImageToolError("File immagine non valido") from exc
    return image


def fit_image(image: Image.Image) -> Image.Image:
    # Riduce dentro la scatola massima mantenendo il rapporto, senza tagliare e
    # senza ingrandire; applica anche l'orientamento memorizzato nei metadati.
    fitted = ImageOps.exif_transpose(image)
    if fitted.mode not in ("RGB", "RGBA"):
        fitted = fitted.convert("RGBA")
    fitted.thumbnail(MAX_SIZE, Image.Resampling.LANCZOS)
    return fitted


def save_webp(image: Image.Image, path: Path) -> tuple[int, int]:
    # Scrive il WebP in un file temporaneo e lo sostituisce solo dopo la verifica.
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    try:
        fitted = fit_image(image)
        fitted.save(temporary, "WEBP", quality=90, method=6)
        with Image.open(temporary) as check:
            check.verify()
        temporary.replace(path)
    except (OSError, ValueError):
        temporary.unlink(missing_ok=True)
        raise
    return fitted.size


def list_destinations(root: Path) -> list[str]:
    # Sottocartelle esistenti, in ordine, senza quelle nascoste.
    root = root.resolve()
    found = []
    for path in root.rglob("*"):
        if not path.is_dir():
            continue
        relative = path.relative_to(root)
        if any(part.startswith(".") for part in relative.parts):
            continue
        found.append(relative.as_posix())
    return sorted(found)


def default_destination(destinations: list[str]) -> str:
    for name in ("board/events", "board/maps", "events", "maps"):
        if name in destinations:
            return name
    return destinations[0] if destinations else "board/events"


def resolve_destination(root: Path, value: str) -> Path:
    # Accetta una sottocartella relativa; rifiuta percorsi assoluti o esterni.
    value = value.strip()
    if not value:
        raise ImageToolError("Indica la cartella di destinazione")
    if ":" in value:
        raise ImageToolError("La cartella deve essere relativa a backend/media")
    candidate = Path(value)
    if candidate.is_absolute() or candidate.drive:
        raise ImageToolError("La cartella deve essere relativa a backend/media")
    parts = candidate.parts
    if not parts or any(part in ("", ".", "..") for part in parts):
        raise ImageToolError("La cartella deve essere una sottocartella di backend/media")
    root = root.resolve()
    resolved = (root / candidate).resolve()
    if resolved == root or root not in resolved.parents:
        raise ImageToolError("La cartella deve stare dentro backend/media")
    return resolved
