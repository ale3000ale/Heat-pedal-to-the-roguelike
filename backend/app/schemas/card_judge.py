from datetime import datetime

from pydantic import BaseModel, ConfigDict


class JudgePlayRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    card_name: str
    card_path: str
    status: str
    played_at: datetime


class PilotPlaysRead(BaseModel):
    pilot_id: int
    pilot_name: str
    plays: list[JudgePlayRead]


class CardBonusRequest(BaseModel):
    pilot_id: int
    card_name: str


class CardBonusRead(BaseModel):
    pilot_id: int
    card_name: str
    card_path: str
