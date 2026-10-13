# Heat — Pedal to the Roguelike

Applicazione web locale per gestire campionati del gioco da tavolo Heat: utenti e ruoli, team, piloti, mazzi, pool di carte, gare con carte sponsor e revisione, classifiche, oro e Negozio con apertura dei pacchetti.

## Tecnologie

- **Backend**: Python, FastAPI, SQLAlchemy, Alembic, Pydantic, SQLite.
- **Frontend**: SvelteKit con TypeScript.
- **Automazione**: `heat.py`, uno script Python multipiattaforma con menu e comandi.

## Prerequisiti

- Python 3.11 o superiore.
- Node.js con npm (https://nodejs.org).

## Primo avvio

Dalla radice del progetto:

```
python heat.py setup
python heat.py start
```

Il setup crea l'ambiente virtuale `backend/.venv`, installa le dipendenze Python da `backend/requirements.txt`, applica le migrazioni, popola il prototipo del mazzo, crea l'utente admin (chiede i dati) e installa le dipendenze del frontend con `npm ci` (o `npm install` se manca `package-lock.json`). Si può ripetere senza danni.

Dopo l'avvio:

- Backend: http://127.0.0.1:8000
- Frontend: http://127.0.0.1:5173

Premi Ctrl+C per fermare entrambi.

## Comandi

| Comando | Cosa fa |
|---|---|
| `python heat.py` | Apre il menu interattivo. |
| `python heat.py setup [--skip-admin] [--skip-seed]` | Installa tutto; le opzioni saltano la creazione dell'admin o del prototipo. |
| `python heat.py migrate` | Applica le migrazioni del database (`alembic upgrade head`). |
| `python heat.py start [--backend-only]` | Migra il database e avvia backend e frontend (o solo il backend). |
| `python heat.py test` | Esegue i test del backend con pytest. |
| `python heat.py check` | Esegue format, check, lint e test del frontend (`tools/check-frontend.mjs`). |

Dopo un `git pull` o un cambio di ramo l'avvio migra comunque da solo il database.

## Struttura

| Percorso | Contenuto |
|---|---|
| `backend/` | API FastAPI, modelli, servizi, migrazioni Alembic, test, immagini in `backend/media/`. |
| `frontend/` | Applicazione SvelteKit (`src/routes`, `src/lib`). |
| `database/` | Cartella del database. |
| `docs/` | Specifica, stato, note, domande aperte, specifica della fase 13, progetto e schema del Negozio. |
| `tools/` | Script di supporto, tra cui `check-frontend.mjs`. |
| `.github/` | Controlli automatici (CI) a ogni pull request. |
| `heat.py` | Setup, avvio, migrazioni, test e controlli. |

## Immagini delle carte

Le immagini stanno in `backend/media/cards/` (`base/modifiche`, `base/sponsor`, `starter`, `uploads`) e vanno riempite a mano. I nomi seguono `nome_N.ext`, con N pari al numero di copie. Per portarle al formato usato dall'applicazione (WebP, scatola massima 560x870 px), da `backend`:

```
python -m app.scripts.resize_cards [cartella] [--dry-run]
```

Le immagini dei pacchetti del Negozio stanno in `backend/media/pack/`.

## Documentazione

- `docs/PROJECT_SPEC.md`: regole di gioco e di prodotto, fonte principale.
- `docs/PROJECT_STATUS.md`: stato di avanzamento.
- `docs/PROJECT_NOTES.md`: mappa del codice, comandi e convenzioni di lavoro.
- `docs/OPEN_QUESTIONS.md`: domande ancora aperte.
- `docs/PHASE_13_SPEC.md`: specifica della fase 13 (carte sponsor in gara e revisione).
- `docs/SHOP_DESIGN.md` e `docs/SHOP_SCHEMA.md`: funzionamento e schema tecnico del Negozio.
- `docs/DATABASE_ANALYSIS.md`: analisi del database.

## Sicurezza

Non vanno inseriti nel repository ambiente virtuale, `node_modules`, database reali, file `.env`, password o token.
