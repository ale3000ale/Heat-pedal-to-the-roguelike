#!/bin/bash
# setup.sh
# Prepara l'intero ambiente di sviluppo Heat su macOS/Linux:
# 1. Verifica/installa Node.js LTS (necessario per il frontend SvelteKit).
# 2. Crea/ricrea il venv del backend usando la versione di Python piu' recente trovata sul sistema
#    (preferendo 3.10+ per compatibilita' con la sintassi "X | None" usata nel codice).
# 3. Installa le dipendenze Python e inizializza il database SQLite.
# 4. Installa le dipendenze npm del frontend.
#
# Uso: bash setup.sh

set -e

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# ensure_node_installed()
# Nessun parametro.
# Controlla se "npm" e' disponibile nel PATH; se non lo trova, installa Node.js LTS
# tramite Homebrew (macOS), cosi' non serve installarlo manualmente prima di lanciare il frontend.
ensure_node_installed() {
  if command -v npm >/dev/null 2>&1; then
    echo "Node.js/npm gia' presente ($(npm --version))."
    return 0
  fi

  echo "npm non trovato: installazione di Node.js LTS..."

  if command -v brew >/dev/null 2>&1; then
    # Passaggio critico: installa Node.js LTS tramite Homebrew, senza intervento manuale
    brew install node
  else
    echo "Errore: Homebrew non trovato su questo sistema." >&2
    echo "Installa Node.js manualmente da https://nodejs.org e rilancia questo script." >&2
    exit 1
  fi

  if ! command -v npm >/dev/null 2>&1; then
    echo "ATTENZIONE: npm ancora non riconosciuto in questa sessione." >&2
    echo "Chiudi e riapri il terminale, poi rilancia setup.sh." >&2
    exit 1
  fi
}

# find_best_python()
# Nessun parametro.
# Cerca, in ordine di preferenza dalla piu' recente alla piu' vecchia, un interprete Python
# disponibile nel PATH (es. python3.13, python3.12, ... python3.9) e ne stampa il percorso.
# Se non trova nessuna versione >=3.10, usa "python3" di sistema come fallback e avvisa l'utente.
find_best_python() {
  local candidates=("python3.13" "python3.12" "python3.11" "python3.10")
  for candidate in "${candidates[@]}"; do
    if command -v "$candidate" >/dev/null 2>&1; then
      echo "$candidate"
      return 0
    fi
  done

  if command -v python3 >/dev/null 2>&1; then
    echo "python3"
    return 0
  fi

  echo ""
  return 1
}

# --- 1. Node.js / npm --------------------------------------------------
ensure_node_installed

# --- 2. Backend Python / venv -------------------------------------------
cd "$ROOT_DIR/backend"

PYTHON_BIN="$(find_best_python)"

if [ -z "$PYTHON_BIN" ]; then
  echo "Errore: nessun interprete Python trovato nel PATH. Installa Python 3.10+ (es. 'brew install python@3.12')."
  exit 1
fi

PYTHON_VERSION="$("$PYTHON_BIN" --version 2>&1)"
echo "Uso interprete: $PYTHON_BIN ($PYTHON_VERSION)"

PY_MAJOR_MINOR="$("$PYTHON_BIN" -c 'import sys; print(f"{sys.version_info.major}{sys.version_info.minor}")')"
if [ "$PY_MAJOR_MINOR" -lt "310" ]; then
  echo "ATTENZIONE: la versione trovata e' inferiore a Python 3.10."
  echo "Il codice usa sintassi 'X | None' che richiede Python 3.10+."
  echo "Consigliato: brew install python@3.12"
fi

if [ -d "venv" ]; then
  echo "Rimozione venv esistente..."
  rm -rf venv
fi

echo "Creazione nuovo venv con $PYTHON_BIN..."
"$PYTHON_BIN" -m venv venv

source venv/bin/activate

echo "Aggiornamento pip/setuptools/wheel..."
pip install --upgrade pip setuptools wheel

echo "Installazione dipendenze da requirements.txt..."
pip install -r requirements.txt

echo "Inizializzazione database heat.db..."
python init_db.py

echo ""
echo "Setup backend completato. Venv creato con $(python --version)."
echo "Per attivarlo manualmente in futuro: cd backend && source venv/bin/activate"

# --- 3. Frontend: installazione dipendenze npm ---------------------------
cd "$ROOT_DIR/frontend"

echo ""
echo "Installazione dipendenze frontend (npm install)..."
npm install
echo "Setup frontend completato."

cd "$ROOT_DIR"
echo ""
echo "Setup completo del progetto Heat."