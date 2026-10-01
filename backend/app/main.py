from fastapi import FastAPI
from app.api.auth import router as auth_router

app = FastAPI(title="Heat")

app.include_router(auth_router, prefix="/api/auth")

@app.get("/health")
async def read_health():
    return {"status": "ok"}
