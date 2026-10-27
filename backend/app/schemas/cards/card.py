from pydantic import BaseModel, ConfigDict


class CardRead(BaseModel):
    # Una riga di mazzo come la vede il client.
    model_config = ConfigDict(from_attributes=True)

    name: str
    path: str
    copies: int