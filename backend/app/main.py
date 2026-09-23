# backend/app/main.py
# Entrypoint dell'applicazione FastAPI: registra i router e la configurazione CORS.

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.db import Base, engine
from app.routers import auth, pilots, teams, championships, decks, shop

# Import dei modelli necessario perche' SQLAlchemy registri le tabelle su Base.metadata
from app.models import user, pilot, team, championship, deck, shop as shop_models  # noqa: F401

app = FastAPI(
    title="Heat - API",
    description="API REST per il gioco da tavolo Heat: campionati, team, piloti, mazzi e negozio.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# create_all() crea le tabelle se non esistono ancora (schema derivato da HeatDB_extended.sql).
# Se il DB e' gia' stato inizializzato con lo script SQL, questa chiamata e' no-op sulle tabelle esistenti.
Base.metadata.create_all(bind=engine)

app.include_router(auth.router)
app.include_router(pilots.router)
app.include_router(teams.router)
app.include_router(championships.router)
app.include_router(decks.router)
app.include_router(shop.router)


# health_check()
# Nessun parametro.
# Endpoint minimale per verificare che il backend sia attivo (usato in debug/monitoraggio).
@app.get("/health")
def health_check():
    return {"status": "ok"}
