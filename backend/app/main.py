from fastapi import FastAPI

app = FastAPI(title="Heat")

@app.get("/health")
async def read_health():
    return {"status": "ok"}
