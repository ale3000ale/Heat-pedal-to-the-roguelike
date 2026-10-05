from typing import Literal

from pydantic import BaseModel


class UserRoleRead(BaseModel):
    id: int
    username: str
    role: str


class RoleSet(BaseModel):
    # Si può assegnare solo giocatore o giudice: l'admin si crea con il setup.
    role: Literal["player", "judge"]
