from pydantic import BaseModel


class ReviewCardRead(BaseModel):
    # Una carta sponsor di un pilota nella revisione: copie rimaste su copie totali.
    card_name: str
    card_path: str
    # Copie che il pilota ha avuto nella gara: partenza + bonus del tasto S.
    total: int
    # Copie ancora in suo possesso dopo le giocate (total - giocate attive o consumate).
    remaining: int
    # Copie arrivate con il tasto S in questa gara.
    gifted: int
    # Copie di partenza (total - gifted, mai sotto zero).
    start: int
    # Copie della carta nella pool sponsor del campionato adesso.
    pool_now: int
    # Copie della carta nella pool di partenza; vuoto se non si conosce.
    pool_max: int | None


class ReviewPilotRead(BaseModel):
    pilot_id: int
    pilot_name: str
    cards: list[ReviewCardRead]


class ReviewInventoryRead(BaseModel):
    race_id: int
    pilots: list[ReviewPilotRead]
