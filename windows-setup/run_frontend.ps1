# run_frontend.ps1
# Installa le dipendenze (se necessario) e avvia il server di sviluppo SvelteKit.
#
# Uso: powershell -ExecutionPolicy Bypass -File run_frontend.ps1
# (oppure: .\run_frontend.ps1)

$ErrorActionPreference = "Stop"

Set-Location ../frontend

if (-not (Test-Path "node_modules")) {
    Write-Host "node_modules non trovato, installo le dipendenze..."
    npm install   # oppure: pnpm install
}

npm run dev       # oppure: pnpm dev
