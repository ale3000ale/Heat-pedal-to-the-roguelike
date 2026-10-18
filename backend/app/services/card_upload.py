import io

from PIL import Image, UnidentifiedImageError
from sqlalchemy.orm import Session

from app.config import CARD_IMAGE_SIZE, MAX_CARD_UPLOAD_BYTES, MEDIA_DIR
from app.services.cards import CardEntry, dump_cards, card_key
from app.services.pools import POOL_KINDS, get_base_pool, pool_cards

# Formati accettati dal caricamento (nomi di formato di Pillow). HEIC non è previsto.
ALLOWED_FORMATS = {"JPEG", "PNG", "WEBP"}
# Caratteri che non possono stare nel nome della carta: finirebbero nel nome del file.
FORBIDDEN_NAME_CHARS = set('/\\:*?"<>|')
MAX_NAME_LENGTH = 64
MAX_COPIES = 999


class CardUploadError(ValueError):
    """Il caricamento non rispetta le regole (messaggio leggibile, risposta 422)."""


class CardNameTakenError(Exception):
    """Esiste già una carta con questo nome nella pool di base del tipo (risposta 409)."""


def _clean_card_name(name: str) -> str:
    # Nome della carta senza spazi ai bordi. Errori: CardUploadError se è vuoto, troppo
    # lungo, comincia con un punto o contiene caratteri non ammessi in un nome di file.
    cleaned = name.strip()
    if not cleaned:
        raise CardUploadError("Il nome della carta è obbligatorio")
    if len(cleaned) > MAX_NAME_LENGTH:
        raise CardUploadError(f"Il nome può avere al massimo {MAX_NAME_LENGTH} caratteri")
    if cleaned.startswith(".") or any(ch in FORBIDDEN_NAME_CHARS for ch in cleaned):
        raise CardUploadError("Il nome contiene caratteri non ammessi")
    return cleaned


def _open_card_image(data: bytes) -> Image.Image:
    # Apre l'immagine ricevuta e controlla dimensione del file, formato e misure.
    # Errori: CardUploadError.
    if not data:
        raise CardUploadError("Il file è vuoto")
    if len(data) > MAX_CARD_UPLOAD_BYTES:
        limit_mb = MAX_CARD_UPLOAD_BYTES // (1024 * 1024)
        raise CardUploadError(f"Il file supera la dimensione massima di {limit_mb} MB")
    try:
        image = Image.open(io.BytesIO(data))
    except (UnidentifiedImageError, OSError, Image.DecompressionBombError) as exc:
        raise CardUploadError("Il file non è un'immagine valida") from exc
    if image.format not in ALLOWED_FORMATS:
        raise CardUploadError("Formato non ammesso: usare JPEG, PNG o WebP")
    if image.size != CARD_IMAGE_SIZE:
        width, height = CARD_IMAGE_SIZE
        raise CardUploadError(f"L'immagine deve essere di {width}x{height} pixel")
    return image


def _write_webp(image: Image.Image, path) -> None:
    # Converte l'immagine in WebP (senza trasparenza) e la scrive su disco.
    # Errori: CardUploadError se l'immagine è danneggiata.
    try:
        image.convert("RGB").save(path, format="WEBP", quality=90)
    except (OSError, ValueError) as exc:
        raise CardUploadError("Impossibile leggere l'immagine") from exc


def upload_card(db: Session, kind: str, name: str, copies: int, data: bytes) -> CardEntry:
    # Carica una carta nella pool di base del tipo scelto. Il file diventa
    # backend/media/cards/uploads/<tipo>/<nome>_<copie>.webp e la carta entra in fondo alla
    # pool con quel percorso relativo. Se il database fallisce il file viene rimosso.
    # Errori: CardUploadError (422), CardNameTakenError (409), PoolNotFoundError
    # se manca la pool di base del tipo.
    if kind not in POOL_KINDS:
        raise CardUploadError("Il tipo deve essere modifiche o sponsor")
    if not 1 <= copies <= MAX_COPIES:
        raise CardUploadError(f"Le copie devono essere da 1 a {MAX_COPIES}")
    name = _clean_card_name(name)
    image = _open_card_image(data)
    pool = get_base_pool(db, kind)
    cards = pool_cards(pool)
    if card_key(name) in {card_key(card.name) for card in cards}:
        raise CardNameTakenError
    filename = f"{name}_{copies}.webp"
    relative = f"cards/uploads/{kind}/{filename}"
    folder = MEDIA_DIR / "cards" / "uploads" / kind
    target = folder / filename
    if target.exists() or any(card.path == relative for card in cards):
        raise CardNameTakenError
    folder.mkdir(parents=True, exist_ok=True)
    _write_webp(image, target)
    entry = CardEntry(name=name, path=relative, copies=copies)
    try:
        pool.base_cards = dump_cards([*cards, entry])
        db.commit()
    except Exception:
        db.rollback()
        target.unlink(missing_ok=True)
        raise
    return entry
