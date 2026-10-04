from datetime import datetime

from pydantic import BaseModel


class DeletedPilotRead(BaseModel):
    id: int
    name: str
    owner: str
    deleted_at: datetime
    purge_at: datetime
    can_purge: bool


class DeletedTeamRead(BaseModel):
    id: int
    name: str
    owner: str
    deleted_at: datetime
    purge_at: datetime
    pilots_count: int
    can_purge: bool


class PurgeRead(BaseModel):
    deleted_pilots: int
    deleted_teams: int
    skipped_pilots: int
    skipped_teams: int