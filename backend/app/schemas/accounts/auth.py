from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


def _normalize_username(value):
    return value.strip().lower() if isinstance(value, str) else value


class RegisterRequest(BaseModel):
    username: str = Field(min_length=3, max_length=32, pattern=r"^[a-z0-9_.-]+$")
    password: str = Field(min_length=8, max_length=128)

    _norm = field_validator("username", mode="before")(_normalize_username)


class LoginRequest(BaseModel):
    username: str = Field(min_length=1, max_length=32)
    password: str = Field(min_length=1, max_length=128)

    _norm = field_validator("username", mode="before")(_normalize_username)


class UserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    role: Literal["admin", "judge", "player"]
