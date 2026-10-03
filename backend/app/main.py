from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.auth import router as auth_router
from app.db.session import SessionLocal
from app.services.sessions import purge_expired
from app.api.teams import router as teams_router
from fastapi.staticfiles import StaticFiles
from app.api.pilots import router as pilots_router
from app.api.championships import router as championships_router
from app.api.pools import router as pools_router
from app.api.races import router as races_router

from app.config import MEDIA_DIR


@asynccontextmanager
async def lifespan(app: FastAPI):
    with SessionLocal() as db:
        purge_expired(db)
    yield


app = FastAPI(title="Heat", lifespan=lifespan)


app.include_router(auth_router, prefix="/api/auth")
app.include_router(teams_router, prefix="/api/teams")
app.include_router(pilots_router, prefix="/api/pilots")
app.include_router(pools_router, prefix="/api/pools")
app.include_router(championships_router, prefix="/api/championships")
app.include_router(races_router, prefix="/api/championships")

MEDIA_DIR.mkdir(parents=True, exist_ok=True)
app.mount("/media", StaticFiles(directory=MEDIA_DIR), name="media")


@app.get("/health")
async def read_health():
    return {"status": "ok"}