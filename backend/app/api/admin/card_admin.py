from fastapi import APIRouter, HTTPException, Query, Request, status

from app.api.deps import AdminUser, DbDep
from app.config import MAX_CARD_UPLOAD_BYTES
from app.schemas.cards.card_admin import CardDeleteRead, CardUploadRead
from app.schemas.championship.pool import PoolKind
from app.services.cards.card_delete import (
    CardNotDeletableError,
    CardNotFoundError,
    delete_uploaded_card,
)
from app.services.cards.card_upload import CardNameTakenError, CardUploadError, upload_card
from app.services.championship.pools import PoolNotFoundError

router = APIRouter(tags=["cards"])

POOL_MISSING = HTTPException(status.HTTP_404_NOT_FOUND, "Pool di base non trovata")


@router.post("", response_model=CardUploadRead, status_code=status.HTTP_201_CREATED)
async def upload(
    request: Request,
    admin: AdminUser,
    db: DbDep,
    kind: PoolKind,
    name: str = Query(min_length=1, max_length=64),
    copies: int = Query(ge=1, le=999),
):
    # Carica una carta (solo admin). Il corpo della richiesta è l'immagine già tagliata a
    # 560x870 (JPEG, PNG o WebP, al massimo 2 MB); tipo, nome e copie sono nell'indirizzo.
    length = request.headers.get("content-length")
    if length is not None and length.isdigit() and int(length) > MAX_CARD_UPLOAD_BYTES:
        raise HTTPException(status.HTTP_413_CONTENT_TOO_LARGE, "Il file è troppo grande")
    data = await request.body()
    try:
        entry = upload_card(db, kind, name, copies, data)
    except PoolNotFoundError:
        raise POOL_MISSING
    except CardNameTakenError:
        raise HTTPException(status.HTTP_409_CONFLICT, "Esiste già una carta con questo nome")
    except CardUploadError as exc:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_CONTENT, str(exc))
    return CardUploadRead(name=entry.name, path=entry.path, copies=entry.copies, kind=kind)


@router.delete("", response_model=CardDeleteRead)
def remove(
    admin: AdminUser,
    db: DbDep,
    kind: PoolKind,
    name: str = Query(min_length=1, max_length=64),
):
    # Elimina una carta caricata dalla pool di base (solo admin). I file senza più uso
    # vengono cancellati; le carte di base e di partenza non si eliminano (409).
    try:
        removed = delete_uploaded_card(db, kind, name)
    except PoolNotFoundError:
        raise POOL_MISSING
    except CardNotFoundError:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Carta non trovata nella pool di base")
    except CardNotDeletableError:
        raise HTTPException(status.HTTP_409_CONFLICT, "Si possono eliminare solo le carte caricate")
    return CardDeleteRead(removed_files=removed)
