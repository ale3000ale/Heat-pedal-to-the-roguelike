"""Origine pubblica del sito e QR in PNG per aprirlo da un altro dispositivo."""
import base64
import io
from urllib.parse import urlsplit

import qrcode

# Fallback quando ne HEAT_PUBLIC_URL ne la richiesta indicano un'origine.
DEFAULT_ORIGIN = "http://127.0.0.1:5173"


def normalize_origin(value: str | None) -> str | None:
    """Restituisce l'origine http/https senza percorso, oppure None.

    value: URL oppure host con porta. Sono rifiutati credenziali, query,
    frammenti, schemi diversi da http/https e porte non numeriche. Non
    vengono fatte richieste di rete.
    """
    if not value:
        return None
    candidate = value.strip()
    if not candidate or any(char.isspace() for char in candidate):
        return None
    if "://" not in candidate:
        candidate = f"http://{candidate}"
    parsed = urlsplit(candidate)
    if parsed.scheme not in ("http", "https") or not parsed.hostname:
        return None
    if parsed.path not in ("", "/") or parsed.query or parsed.fragment:
        return None
    if parsed.username or parsed.password:
        return None
    try:
        parsed.port
    except ValueError:
        return None
    return f"{parsed.scheme}://{parsed.netloc}"


def first_header_value(value: str | None) -> str | None:
    """Prima voce di un header inoltrato, per esempio "host:5173, proxy"."""
    if not value:
        return None
    first = value.split(",")[0].strip()
    return first or None


def site_origin(public_url=None, host=None, proto=None) -> str:
    """Origine da mettere nel QR: HEAT_PUBLIC_URL, poi la richiesta, poi loopback.

    public_url: valore di HEAT_PUBLIC_URL impostato dal launcher.
    host: Host oppure X-Forwarded-Host della richiesta corrente.
    proto: X-Forwarded-Proto della richiesta; http se assente o non valido.
    """
    scheme = (first_header_value(proto) or "").lower()
    if scheme not in ("http", "https"):
        scheme = "http"
    forwarded_host = first_header_value(host)
    request_origin = f"{scheme}://{forwarded_host}" if forwarded_host else None
    return normalize_origin(public_url) or normalize_origin(request_origin) or DEFAULT_ORIGIN


def qr_png_data_url(url: str) -> str:
    """PNG del QR come data URL, senza file temporanei ne nuove dipendenze."""
    image = qrcode.make(url, box_size=10, border=2)
    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    encoded = base64.b64encode(buffer.getvalue()).decode("ascii")
    return f"data:image/png;base64,{encoded}"
