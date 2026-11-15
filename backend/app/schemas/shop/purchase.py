from pydantic import BaseModel


class ShopPilotRead(BaseModel):
    id: int
    name: str
    gold: int
    sponsor: int


class ShopPackRead(BaseModel):
    # Pacchetto come lo vede chi entra nel negozio; sold_out = "Terminato".
    id: int
    name: str
    image_path: str
    currency: str
    cost: int
    modifiche_count: int
    sponsor_count: int
    filter_enabled: bool
    filter_text: str | None
    sold_out: bool


class ShopViewRead(BaseModel):
    championship_id: int
    championship_name: str
    pilot: ShopPilotRead | None
    read_only: bool
    locked: bool
    packs: list[ShopPackRead]


class PurchaseRequest(BaseModel):
    pilot_id: int
    pack_id: int


class DrawnCardRead(BaseModel):
    name: str
    path: str
    copies: int


class PurchaseRead(BaseModel):
    # Esito dell'acquisto: le carte uscite (modifiche e sponsor, l'animazione mostra
    # prima le modifiche) e il saldo aggiornato del pilota.
    purchase_id: int
    pack_name: str
    currency: str
    cost: int
    cards_modifiche: list[DrawnCardRead]
    cards_sponsor: list[DrawnCardRead]
    gold: int
    sponsor: int
