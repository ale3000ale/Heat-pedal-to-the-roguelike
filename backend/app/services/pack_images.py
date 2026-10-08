from pathlib import Path

from app.services.images import CardImageError, save_card_image, slugify

# Cartella dei file: backend/media/pack, con l'immagine predefinita e quelle caricate.
DEFAULT_MEDIA_DIR = Path(__file__).resolve().parents[2] / "media" / "pack"
DEFAULT_FOLDER = "defaultIllustration"
UPLOAD_FOLDER = "illustration"

MAX_UPLOAD_BYTES = 5 * 1024 * 1024
UPLOAD_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp"}
LISTED_EXTENSIONS = UPLOAD_EXTENSIONS


class PackImageError(ValueError):
    """File non valido come immagine di un pacchetto (formato, peso o contenuto)."""


def validate_upload(filename: str, data: bytes) -> None:
    # Controlla estensione e peso del file caricato; non ne legge il contenuto.
    # Errori: PackImageError se il file è vuoto, troppo grande o di un formato non ammesso.
    if not data:
        raise PackImageError("File vuoto")
    if len(data) > MAX_UPLOAD_BYTES:
        raise PackImageError("File troppo grande (massimo 5 MB)")
    if Path(filename).suffix.lower() not in UPLOAD_EXTENSIONS:
        raise PackImageError("Formato non ammesso (png, jpg, jpeg o webp)")


def save_pack_image(filename: str, data: bytes, media_dir: Path | None = None) -> str:
    # Salva l'immagine caricata in WebP, nella scatola massima delle carte, dentro la
    # cartella dei caricamenti. Restituisce il percorso relativo, es. "illustration/turbo.webp".
    # Errori: PackImageError se il file non è ammesso o non è un'immagine leggibile.
    validate_upload(filename, data)
    base = media_dir or DEFAULT_MEDIA_DIR
    try:
        saved = save_card_image(data, base / UPLOAD_FOLDER, slugify(Path(filename).stem))
    except CardImageError as exc:
        raise PackImageError(str(exc)) from exc
    return f"{UPLOAD_FOLDER}/{saved}"


def list_pack_images(media_dir: Path | None = None) -> list[str]:
    # Percorsi relativi delle immagini disponibili: prima la predefinita, poi i caricamenti,
    # ciascun gruppo in ordine alfabetico. Le cartelle mancanti danno un elenco vuoto.
    base = media_dir or DEFAULT_MEDIA_DIR
    paths: list[str] = []
    for folder in (DEFAULT_FOLDER, UPLOAD_FOLDER):
        directory = base / folder
        if not directory.is_dir():
            continue
        names = sorted(
            item.name
            for item in directory.iterdir()
            if item.is_file() and item.suffix.lower() in LISTED_EXTENSIONS
        )
        paths.extend(f"{folder}/{name}" for name in names)
    return paths


def is_available_pack_image(path: str, media_dir: Path | None = None) -> bool:
    # Vero solo se il percorso è una delle immagini elencate: impedisce percorsi assoluti
    # o con ".." scelti a mano.
    return path in list_pack_images(media_dir)
