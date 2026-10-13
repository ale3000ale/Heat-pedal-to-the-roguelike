# SCRIPTS

Elenco degli script di automazione presenti nel repository.

## heat.py

Script Python multipiattaforma nella radice del progetto. Senza argomenti apre un menu interattivo che mostra il sistema operativo rilevato e la versione di Python; con un sottocomando esegue direttamente l'operazione.

| Comando | Cosa fa |
|---|---|
| `python heat.py` | Apre il menu interattivo. |
| `python heat.py setup [--skip-admin] [--skip-seed]` | Installa tutto (vedi `docs/SETUP.md`). |
| `python heat.py migrate` | Applica le migrazioni (`alembic upgrade head`) nel backend. |
| `python heat.py start [--backend-only]` | Migra il database e avvia backend (uvicorn con `--reload`, porta 8000) e frontend (`npm run dev`, porta 5173 con `--strictPort`); con `--backend-only` avvia solo il backend. |
| `python heat.py test` | Esegue `pytest -q` nel backend. |
| `python heat.py check` | Esegue `tools/check-frontend.mjs` (format, check, lint e test del frontend). |

Voci del menu: setup, aggiornamento del database, avvio completo, avvio del solo backend, test del backend, controlli del frontend, uscita.

### Comportamento

- `migrate`, `start` e `test` richiedono l'ambiente virtuale `backend/.venv`; se manca, si fermano con un messaggio che invita a eseguire il setup.
- Su Windows i processi vengono fermati con `taskkill`, su macOS e Linux con un segnale al gruppo di processi.
- `test` e `check` restituiscono l'esito dei test senza interrompere il menu.
- Lo script non crea backup del database prima delle migrazioni e non offre un reset: queste funzioni non sono implementate.

## tools/check-frontend.mjs

Script Node usato da `python heat.py check`. Richiede `node` nel PATH. Il suo contenuto non è descritto qui nel dettaglio: consulta il file.

## Script del backend

Eseguiti da `backend/` con l'ambiente virtuale:

- `python -m app.scripts.seed_prototype`: popola il prototipo del mazzo.
- `python -m app.scripts.create_admin`: crea l'utente admin.
- `python -m app.scripts.resize_cards [cartella] [--dry-run]`: converte le immagini delle carte in WebP, scatola massima 560x870 px.

## Altri file

- `riapri-aider.bat`: file batch di Windows nella radice, non documentato qui.
