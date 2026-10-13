from pathlib import Path

DATABASE_URL = "sqlite:///./heat.db"
SESSION_COOKIE_NAME = "heat_session"
SESSION_COOKIE_SECURE = False
# Cartella dei file multimediali (backend/media), servita all'indirizzo /media.
MEDIA_DIR = Path(__file__).resolve().parent.parent / "media"
# Caricamento delle carte (solo admin): dimensione massima del file ricevuto e misure
# esatte dell'immagine, che il frontend taglia prima dell'invio (larghezza, altezza).
MAX_CARD_UPLOAD_BYTES = 2 * 1024 * 1024
CARD_IMAGE_SIZE = (560, 870)
