# backend/app/schemas/auth.py
# Schemi Pydantic per registrazione, login e token JWT.

from pydantic import BaseModel, field_validator


class UserRegister(BaseModel):
    username: str
    password: str

    # validate_password(v)
    # v: valore grezzo del campo password ricevuto nel body della richiesta.
    # Controlla solo la lunghezza minima (8 caratteri), senza regole di "forza" avanzate,
    # come richiesto dai vincoli funzionali.
    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("La password deve contenere almeno 8 caratteri")
        return v


class UserLogin(BaseModel):
    username: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: str
    username: str


class UserOut(BaseModel):
    id: int
    username: str
    role: str

    class Config:
        from_attributes = True
