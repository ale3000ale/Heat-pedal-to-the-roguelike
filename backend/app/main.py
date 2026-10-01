from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.auth import router as auth_router
from app.db.session import SessionLocal
from app.services.sessions import purge_expired


@asynccontextmanager
async def lifespan(app: FastAPI):
    with SessionLocal() as db:
        purge_expired(db)
    yield


app = FastAPI(title="Heat", lifespan=lifespan)

app.include_router(auth_router, prefix="/api/auth")


@app.get("/health")
async def read_health():
    return {"status": "ok"}