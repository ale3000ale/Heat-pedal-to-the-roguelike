from pydantic import BaseModel

from app.schemas.pool import PoolKind


class CardUploadRead(BaseModel):
    # Carta appena caricata: nome, percorso relativo a backend/media, copie e tipo.
    name: str
    path: str
    copies: int
    kind: PoolKind


class CardDeleteRead(BaseModel):
    # Esito dell'eliminazione: percorsi dei file cancellati (vuoto se la carta è ancora in uso).
    removed_files: list[str]
