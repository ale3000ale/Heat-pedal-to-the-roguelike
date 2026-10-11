from pydantic import BaseModel

from app.schemas.purchase import DrawnCardRead


class InventoryRead(BaseModel):
    # Riepilogo per il popup: ogni sezione del negozio mostra il proprio inventario.
    pilot_id: int
    pilot_name: str
    modifiche: list[DrawnCardRead]
    sponsor: list[DrawnCardRead]
