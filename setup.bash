#!/bin/bash
# setup.sh
# Crea/ricrea il venv del backend usando la versione di Python piu' recente trovata sul sistema
# (preferendo 3.10+ per compatibilita' con la sintassi "X | None" usata nel codice),
# installa le dipendenze e inizializza il database SQLite.
#
# Uso: bash setup.sh

set -e

cd backend

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

  # Nessuna versione moderna trovata: fallback su python3 di sistema, con avviso
  if command -v python3 >/dev/null 2>&1; then
    echo "python3"
    return 0
  fi

  echo "" # nessun python trovato
  return 1
}

PYTHON_BIN="$(find_best_python)"

if [ -z "$PYTHON_BIN" ]; then
  echo "Errore: nessun interprete Python trovato nel PATH. Installa Python 3.10+ (es. 'brew install python@3.12')."
  exit 1
fi

PYTHON_VERSION="$("$PYTHON_BIN" --version 2>&1)"
echo "Uso interprete: $PYTHON_BIN ($PYTHON_VERSION)"

# Avviso se la versione trovata e' inferiore alla 3.10 (rischio incompatibilita' sintassi "X | None")
PY_MAJOR_MINOR="$("$PYTHON_BIN" -c 'import sys; print(f"{sys.version_info.major}{sys.version_info.minor}")')"
if [ "$PY_MAJOR_MINOR" -lt "310" ]; then
  echo "ATTENZIONE: la versione trovata e' inferiore a Python 3.10."
  echo "Il codice usa sintassi 'X | None' che richiede Python 3.10+."
  echo "Consigliato: brew install python@3.12"
fi

# Rimuove un eventuale venv precedente per evitare mix di versioni Python diverse
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
echo "Setup completato. Venv creato con $(python --version)."
echo "Per attivarlo manualmente in futuro: cd backend && source venv/bin/activate"