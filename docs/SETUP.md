# Installazione e avvio — Heat

Ultimo aggiornamento: 2026-10-13

Questo documento descrive solo ciò che fa `heat.py` nella radice del repository (letto il 2026-10-13). Per l'elenco dei comandi vedi `SCRIPTS.md`.

## Prerequisiti

- Python 3.11 o superiore (il setup si ferma con un errore se la versione è più bassa).
- Node.js con npm, necessario per il frontend e per i controlli del frontend (`npm` e `node` vengono cercati nel percorso di sistema; se mancano lo script si ferma e indica https://nodejs.org).

## Primo avvio

Dalla radice del repository:

```
python heat.py setup
```

Il setup, nell'ordine:

1. crea l'ambiente virtuale `backend/.venv` se non esiste;
2. aggiorna `pip` e installa `backend/requirements.txt`;
3. applica le migrazioni Alembic (`alembic upgrade head`);
4. popola il prototipo del mazzo (`python -m app.scripts.seed_prototype`), salvo `--skip-seed`;
5. crea l'utente admin (`python -m app.scripts.create_admin`), salvo `--skip-admin`;
6. se esiste `frontend/package.json` installa le dipendenze del frontend con `npm ci` (se c'è `package-lock.json`) oppure `npm install`; altrimenti salta il passaggio.

Il setup si può ripetere: l'ambiente esistente viene riutilizzato e le migrazioni già applicate non cambiano nulla.

## Avvio

```
python heat.py start
```

Prima di avviare il server applica sempre le migrazioni. Poi avvia il backend (uvicorn con `--reload`) su http://127.0.0.1:8000 e il frontend (`npm run dev`, porta fissa) su http://127.0.0.1:5173. Se manca `backend/.venv` o `frontend/node_modules`, lo script si ferma e chiede di eseguire prima il setup. Ctrl+C ferma tutto; se un processo si ferma da solo, vengono chiusi anche gli altri.

Per avviare solo il backend: `python heat.py start --backend-only`.

## Configurazione del backend

In `backend/app/config.py` (letto il 2026-10-13): database `sqlite:///./heat.db`, cookie di sessione `heat_session` senza flag secure, cartella dei file multimediali `backend/media` servita all'indirizzo `/media`, caricamento delle carte con file massimo 2 MB e immagine di 560x870 pixel.

## Non verificato

Questo documento non copre: file `.env`, ripristino o backup del database, reset, build del frontend e il contenuto di `tools/`, a parte il fatto che `heat.py check` richiama `tools/check-frontend.mjs`. Nel ramo non esistono `setup.py`, `setup.bat`, `setup.sh` né la cartella `scripts` previsti dalle istruzioni del progetto: il loro compito è svolto da `heat.py`.
