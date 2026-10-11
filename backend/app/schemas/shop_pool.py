from pydantic import BaseModel


class ShopPoolCard(BaseModel):
    # Una carta della pool con le copie rimaste e la probabilità (in percentuale) che
    # esca alla prima estrazione senza filtro.
    name: str
    path: str
    copies: int
    probability: float


class ShopPoolSection(BaseModel):
    # Una pool (modifiche o sponsor): copie totali rimaste e carte, dalla più probabile.
    total_copies: int
    cards: list[ShopPoolCard]


class ShopPoolRead(BaseModel):
    modifiche: ShopPoolSection
    sponsor: ShopPoolSection
