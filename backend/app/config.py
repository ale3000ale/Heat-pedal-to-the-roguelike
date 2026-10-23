import os
from pathlib import Path

DATABASE_URL = "sqlite:///./heat.db"
SESSION_COOKIE_NAME = "heat_session"
_cookie_secure = os.environ.get("HEAT_SESSION_COOKIE_SECURE", "0")
if _cookie_secure not in ("0", "1"):
    raise ValueError("HEAT_SESSION_COOKIE_SECURE deve essere 0 oppure 1")
SESSION_COOKIE_SECURE = _cookie_secure == "1"
# Default locale invariato; production imposta 1 per un'origine HTTPS.
MEDIA_DIR = Path(__file__).resolve().parent.parent / "media"
MAX_CARD_UPLOAD_BYTES = 2 * 1024 * 1024
CARD_IMAGE_SIZE = (560, 870)
