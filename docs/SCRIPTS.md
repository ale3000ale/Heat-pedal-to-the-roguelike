# Script — Heat

Ultimo aggiornamento: 2026-10-13

Descrizione dei comandi di `heat.py` (letto il 2026-10-13). Si eseguono dalla radice del repository. Senza argomenti `python heat.py` apre un menu interattivo.

## Comandi

| Comando | Cosa fa |
|---|---|
| `python heat.py` | Menu con sei voci (setup, migrazioni, avvio completo, solo backend, test backend, controlli frontend) e `0` per uscire. Mostra il sistema operativo e la versione di Python rilevati. |
| `python heat.py setup` | Ambiente virtuale, dipendenze, migrazioni, prototipo del mazzo, utente admin, dipendenze frontend. Opzioni: `--skip-admin`, `--skip-seed`. |
| `python heat.py migrate` | Esegue `alembic upgrade head` nell'ambiente `backend/.venv`. |
| `python heat.py start` | Applica le migrazioni, poi avvia backend (127.0.0.1:8000) e frontend (127.0.0.1:5173). Opzione: `--backend-only`. |
| `python heat.py test` | Esegue `python -m pytest -q` in `backend/`. |
| `python heat.py check` | Esegue `node tools/check-frontend.mjs` (format, check, lint e test del frontend, come indicato nel commento dello script). |

## Comportamento comune

- Gli errori fermano il comando con un messaggio che inizia con "ERRORE"; dal menu l'errore viene mostrato e il menu resta aperto.
- `test` e `check` non fermano lo script se falliscono: il codice di uscita dei test non viene propagato come errore di `heat.py`.
- I comandi che usano il backend richiedono `backend/.venv`; se manca indicano di scegliere prima "Setup".
- Su Windows i processi si fermano con `taskkill`, su macOS e Linux con un segnale al gruppo di processi.

## Non verificato

Non ho letto il contenuto di `tools/` (oltre al nome `check-frontend.mjs`), né gli script `app.scripts.seed_prototype`, `app.scripts.create_admin` e `app.scripts.resize_cards`. Non ci sono backup, ripristino, reset o build del frontend: nel ramo non esiste una cartella `scripts` né i file `setup.bat` e `setup.sh`.
