from pydantic import BaseModel


class SiteQrRead(BaseModel):
    """Origine del sito e QR PNG come data URL; nessun dato sensibile."""

    url: str
    image: str
