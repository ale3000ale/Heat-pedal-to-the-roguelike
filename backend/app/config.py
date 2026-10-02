from pathlib import Path

DATABASE_URL = "sqlite:///./heat.db"
SESSION_COOKIE_NAME = "heat_session"
SESSION_COOKIE_SECURE = False
# Cartella dei file multimediali (backend/media), servita all'indirizzo /media.
MEDIA_DIR = Path(__file__).resolve().parent.parent / "media"