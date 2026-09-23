# setup.ps1
# Prepara l'intero ambiente di sviluppo Heat su Windows:
# 1. Verifica/installa Node.js LTS (necessario per il frontend SvelteKit).
# 2. Crea/ricrea il venv del backend usando la versione di Python piu' recente trovata sul sistema
#    (preferendo 3.10+ per compatibilita' con la sintassi "X | None" usata nel codice).
# 3. Installa le dipendenze Python e inizializza il database SQLite.
#
# Uso: powershell -ExecutionPolicy Bypass -File setup.ps1
# (oppure, se hai gia' abilitato gli script: .\setup.ps1)

$ErrorActionPreference = "Stop"

$RootDir = $PSScriptRoot

# Ensure-NodeInstalled
# Nessun parametro.
# Controlla se "npm" e' disponibile nel PATH; se non lo trova, installa Node.js LTS
# tramite winget, cosi' non serve installarlo manualmente prima di lanciare il frontend.
function Ensure-NodeInstalled {
    $npmCmd = Get-Command npm -ErrorAction SilentlyContinue
    if ($npmCmd) {
        $npmVersion = npm --version
        Write-Host "Node.js/npm gia' presente (npm v$npmVersion)."
        return
    }

    Write-Host "npm non trovato: installazione di Node.js LTS tramite winget..."

    $wingetCmd = Get-Command winget -ErrorAction SilentlyContinue
    if (-not $wingetCmd) {
        Write-Host "Errore: 'winget' non e' disponibile su questo sistema." -ForegroundColor Red
        Write-Host "Installa Node.js manualmente da https://nodejs.org e riavvia il terminale." -ForegroundColor Red
        exit 1
    }

    # Passaggio critico: installa Node.js in modalita' silenziosa, accettando gli accordi
    # di licenza in automatico, per non bloccare lo script su un prompt interattivo.
    winget install OpenJS.NodeJS.LTS --silent --accept-package-agreements --accept-source-agreements

    Write-Host "Node.js installato. Se il comando 'npm' non viene riconosciuto nei prossimi passi," -ForegroundColor Yellow
    Write-Host "chiudi questo terminale, riaprilo e rilancia setup.ps1 (serve per aggiornare il PATH)." -ForegroundColor Yellow
}

# Find-BestPython
# Nessun parametro.
# Cerca, tramite il Python Launcher "py", la versione di Python piu' recente disponibile
# sul sistema, dalla 3.13 alla 3.10. Ritorna l'argomento da passare a "py" (es. "-3.12"),
# oppure stringa vuota per usare "py" senza versione, oppure $null se Python non e' installato.
function Find-BestPython {
    $candidates = @("-3.13", "-3.12", "-3.11", "-3.10")

    foreach ($arg in $candidates) {
        try {
            & py $arg --version > $null 2>&1
            if ($LASTEXITCODE -eq 0) {
                return $arg
            }
        } catch {}
    }

    try {
        & py --version > $null 2>&1
        if ($LASTEXITCODE -eq 0) {
            return ""
        }
    } catch {}

    return $null
}

# --- 1. Node.js / npm --------------------------------------------------
Ensure-NodeInstalled

# --- 2. Backend Python / venv -------------------------------------------
Set-Location (Join-Path $RootDir "backend")

$PyArg = Find-BestPython

if ($null -eq $PyArg) {
    Write-Host "Errore: nessun interprete Python trovato. Installa Python 3.10+ da https://www.python.org/downloads/ (spunta 'Add python.exe to PATH')." -ForegroundColor Red
    exit 1
}

if ($PyArg -eq "") {
    $PythonVersion = & py --version 2>&1
} else {
    $PythonVersion = & py $PyArg --version 2>&1
}
Write-Host "Uso interprete: py $PyArg ($PythonVersion)"

if ($PyArg -eq "") {
    $versionOutput = (& py --version 2>&1) -replace "Python ", ""
    $parts = $versionOutput.Split(".")
    $majorMinor = [int]($parts[0] + $parts[1])
    if ($majorMinor -lt 310) {
        Write-Host "ATTENZIONE: la versione trovata e' inferiore a Python 3.10." -ForegroundColor Yellow
        Write-Host "Il codice usa sintassi 'X | None' che richiede Python 3.10+." -ForegroundColor Yellow
        Write-Host "Consigliato: scarica Python 3.12 da python.org" -ForegroundColor Yellow
    }
}

if (Test-Path "venv") {
    Write-Host "Rimozione venv esistente..."
    Remove-Item -Recurse -Force "venv"
}

Write-Host "Creazione nuovo venv..."
if ($PyArg -eq "") {
    & py -m venv venv
} else {
    & py $PyArg -m venv venv
}

& .\venv\Scripts\Activate.ps1

Write-Host "Aggiornamento pip/setuptools/wheel..."
python -m pip install --upgrade pip setuptools wheel

Write-Host "Installazione dipendenze da requirements.txt..."
pip install -r requirements.txt

Write-Host "Inizializzazione database heat.db..."
python init_db.py

Write-Host ""
Write-Host "Setup backend completato. Venv creato con $(python --version)."
Write-Host "Per attivarlo manualmente in futuro: cd backend; .\venv\Scripts\Activate.ps1"

# --- 3. Frontend: installazione dipendenze npm ---------------------------
Set-Location (Join-Path $RootDir "frontend")

if (Get-Command npm -ErrorAction SilentlyContinue) {
    Write-Host ""
    Write-Host "Installazione dipendenze frontend (npm install)..."
    npm install
    Write-Host "Setup frontend completato."
} else {
    Write-Host ""
    Write-Host "npm non ancora disponibile in questa sessione: riapri il terminale e lancia" -ForegroundColor Yellow
    Write-Host "'cd frontend; npm install' manualmente, oppure rilancia run_frontend.ps1." -ForegroundColor Yellow
}

Set-Location $RootDir
Write-Host ""
Write-Host "Setup completo del progetto Heat."