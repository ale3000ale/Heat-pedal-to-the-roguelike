import re
import unicodedata
from io import BytesIO
from pathlib import Path

from PIL import Image, ImageOps, UnidentifiedImageError

# Scatola massima delle carte: 5,6 x 8,7 cm a 100 pixel per centimetro.
MAX_CARD_SIZE = (560, 870)


class CardImageError(ValueError):
    """File non valido o non leggibile come immagine."""


def slugify(name: str) -> str:
    # Nome di file sicuro: senza accenti, minuscolo, solo lettere, numeri e trattini.
    # "Forza motrice" -> "forza-motrice", "Velocità 1" -> "velocita-1".
    ascii_text = unicodedata.normalize("NFKD", name).encode("ascii", "ignore").decode()
    slug = re.sub(r"[^a-z0-9]+", "-", ascii_text.lower()).strip("-")
    return slug or "carta"


def unique_filename(directory: Path, slug: str, extension: str = ".webp") -> str:
    # Se esiste già un file con questo nome aggiunge -2, -3, ...
    candidate = f"{slug}{extension}"
    number = 2
    while (directory / candidate).exists():
        candidate = f"{slug}-{number}{extension}"
        number += 1
    return candidate


def load_image(data: bytes) -> Image.Image:
    # Legge un'immagine dai byte caricati; errore leggibile se il file non è valido.
    try:
        image = Image.open(BytesIO(data))
        image.load()
    except (UnidentifiedImageError, OSError, Image.DecompressionBombError) as exc:
        raise CardImageError("File immagine non valido") from exc
    return image


def fit_card_image(image: Image.Image) -> Image.Image:
    # Riduce l'immagine dentro la scatola massima mantenendo le proporzioni, senza
    # tagliare e senza ingrandire. Applica anche l'orientamento memorizzato nei metadati.
    fitted = ImageOps.exif_transpose(image)
    if fitted.mode not in ("RGB", "RGBA"):
        fitted = fitted.convert("RGBA")
    fitted.thumbnail(MAX_CARD_SIZE, Image.Resampling.LANCZOS)
    return fitted


def save_card_image(data: bytes, directory: Path, name: str) -> str:
    # Salva l'immagine ridimensionata in WebP e restituisce il nome del file creato.
    image = fit_card_image(load_image(data))
    directory.mkdir(parents=True, exist_ok=True)
    filename = unique_filename(directory, slugify(name))
    image.save(directory / filename, "WEBP", quality=90, method=6)
    return filename