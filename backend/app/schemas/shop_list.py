from pydantic import BaseModel


class ShopPilotRef(BaseModel):
    id: int
    name: str


class ShopEntryRead(BaseModel):
    # Un negozio apribile: il campionato e i piloti con cui l'utente può entrare.
    championship_id: int
    championship_name: str
    pilots: list[ShopPilotRef]


class MyShopsRead(BaseModel):
    shops: list[ShopEntryRead]
