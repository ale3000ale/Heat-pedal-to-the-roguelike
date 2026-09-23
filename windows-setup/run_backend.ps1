# run_backend.ps1
# Attiva il venv del backend e avvia il server FastAPI in modalita' reload.
#
# Uso: powershell -ExecutionPolicy Bypass -File run_backend.ps1
# (oppure: .\run_backend.ps1)

$ErrorActionPreference = "Stop"

Set-Location ../backend
& .\venv\Scripts\Activate.ps1
uvicorn app.main:app --reload --port 8000
