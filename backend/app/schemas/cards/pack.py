from datetime import datetime

from pydantic import BaseModel


class PackRead(BaseModel):
    # Pacchetto del negozio di un campionato.
    model_config = {"from_attributes": True}

    id: int
    championship_id: int
    name: str
    image_path: str
    currency: str
    cost: int
    modifiche_count: int
    sponsor_count: int
    filter_enabled: bool
    filter_text: str | None
    created_at: datetime
    updated_at: datetime
