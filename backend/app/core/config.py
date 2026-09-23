# backend/app/core/config.py
# Configurazione centralizzata dell'app (chiavi JWT, scadenze token, CORS).
# In produzione locale, SECRET_KEY va spostata in variabile d'ambiente.

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    SECRET_KEY: str = "change-this-secret-key-in-production"  # usato per firmare i JWT
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 1 giorno
    CORS_ORIGINS: list[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ]
    MIN_PASSWORD_LENGTH: int = 8
    CARDS_IMAGE_BASE_PATH: str = "src/images/cards"  # path base per validazione carte

    class Config:
        env_file = ".env"


settings = Settings()
