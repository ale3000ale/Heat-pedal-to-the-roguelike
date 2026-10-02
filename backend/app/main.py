from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.auth import router as auth_router
from app.db.session import SessionLocal
from app.services.sessions import purge_expired
from app.api.auth import router as auth_router
from app.api.teams import router as teams_router



@asynccontextmanager
async def lifespan(app: FastAPI):
    with SessionLocal() as db:
        purge_expired(db)
    yield


app = FastAPI(title="Heat", lifespan=lifespan)

app.include_router(auth_router, prefix="/api/auth")
app.include_router(auth_router, prefix="/api/auth")
app.include_router(teams_router, prefix="/api/teams")

@app.get("/health")
async def read_health():
    return {"status": "ok"}