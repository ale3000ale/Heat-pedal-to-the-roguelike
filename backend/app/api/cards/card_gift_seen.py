"""Endpoint selettivo aggiuntivo; /card-gifts/seen storico resta invariato."""
from typing import Annotated

from fastapi import APIRouter, HTTPException, Path, status

from app.api.deps import CurrentUser, DbDep
from app.schemas.cards.card_gift_seen import GiftSeenSelection
from app.services.cards.card_gift_seen import mark_selected_gifts_seen
from app.services.championship.championships import ChampionshipNotFoundError
from app.services.pilots.pilots import PilotNotFoundError

router = APIRouter(tags=["card-plays"])


@router.post(
    "/{championship_id}/card-gifts/seen-selected",
    status_code=status.HTTP_204_NO_CONTENT,
)
def mark_selected_card_gifts_seen(
    championship_id: Annotated[int, Path(gt=0, le=9223372036854775807)],
    data: GiftSeenSelection,
    user: CurrentUser,
    db: DbDep,
) -> None:
    """Conferma il sottoinsieme richiesto, senza esporre ID o dati di altri piloti."""
    try:
        mark_selected_gifts_seen(db, user, championship_id, data)
    except ChampionshipNotFoundError:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Campionato non trovato")
    except PilotNotFoundError:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Pilota non trovato")
