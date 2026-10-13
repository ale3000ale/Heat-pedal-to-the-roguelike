# SETUP

Guida all'installazione e al primo avvio di Heat — Pedal to the Roguelike. Tutti i comandi vanno eseguiti dalla radice del progetto.

## Prerequisiti

- Python 3.11 o superiore (lo script si ferma con un errore se la versione è inferiore).
- Node.js con npm (https://nodejs.org). Serve per il frontend e per `python heat.py check`.

## Primo avvio

```
python heat.py setup
python heat.py start
```

## Cosa fa il setup

Il comando `python heat.py setup` esegue, in ordine:

1. Crea l'ambiente virtuale `backend/.venv` se non esiste già.
2. Aggiorna `pip` e installa le dipendenze da `backend/requirements.txt`.
3. Applica le migrazioni del database con Alembic (`alembic upgrade head`).
4. Popola il prototipo del mazzo (`app.scripts.seed_prototype`), salvo `--skip-seed`.
5. Crea l'utente admin (`app.scripts.create_admin`, chiede i dati), salvo `--skip-admin`.
6. Se esiste `frontend/package.json`, installa le dipendenze del frontend con `npm ci` (se c'è `package-lock.json`) oppure `npm install`.

Il setup si può ripetere senza danni: l'ambiente virtuale esistente viene riutilizzato e le migrazioni già applicate non vengono rieseguite.

## Indirizzi dopo l'avvio

- Backend: http://127.0.0.1:8000
- Frontend: http://127.0.0.1:5173

Ctrl+C ferma entrambi i processi. Se un processo si ferma da solo, lo script chiude anche l'altro.

## Dopo un git pull o un cambio di ramo

`python heat.py start` applica sempre le migrazioni prima di avviare il server, quindi il database viene aggiornato da solo. In alternativa si può usare `python heat.py migrate`.

## Errori comuni

- `Ambiente non pronto. Scegli prima 'Setup'`: manca `backend/.venv`; esegui `python heat.py setup`.
- `Dipendenze frontend mancanti`: manca `frontend/node_modules`; esegui `python heat.py setup`.
- `npm non trovato` o `node non trovato`: installa Node.js.

## Sicurezza

Non vanno inseriti nel repository ambiente virtuale, `node_modules`, database reali, file `.env`, password o token.
