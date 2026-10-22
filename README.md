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

Le immagini stanno in `backend/media/cards/` (`base/modifiche`, `base/sponsor`, `starter`, `uploads`). Le cartelle `base` e `starter` vanno riempite a mano; `uploads` si riempie con il caricamento dell'admin (`POST /api/admin/cards`, immagine già tagliata a 560x870 px, al massimo 2 MB) e le carte caricate si eliminano con `DELETE /api/admin/cards`. L'interfaccia di caricamento con ritaglio e zoom è nella pagina admin delle pool (13f): le carte caricate si riconoscono dal nome in arancione e si eliminano dall'elenco. I nomi seguono `nome_N.ext`, con N pari al numero di copie. Per portarle al formato usato dall'applicazione (WebP, scatola massima 560x870 px), da `backend`:

```
python -m app.scripts.resize_cards [cartella] [--dry-run]
```

Le immagini dei pacchetti del Negozio stanno in `backend/media/pack/`.

## Documentazione

- `docs/PROJECT_SPEC.md`: regole di gioco e di prodotto, fonte principale.
- `docs/PROJECT_STATUS.md`: stato di avanzamento.
- `docs/PROJECT_NOTES.md`: mappa del codice, comandi e convenzioni di lavoro.
- `docs/OPEN_QUESTIONS.md`: domande ancora aperte.
- `docs/PHASE_13_SPEC.md`: specifica della fase 13 (carte sponsor in gara, revisione e amministrazione delle carte).
- `docs/SHOP_DESIGN.md` e `docs/SHOP_SCHEMA.md`: funzionamento e schema tecnico del Negozio.
- `docs/DATABASE_ANALYSIS.md`: analisi del database.

## Sicurezza

Non vanno inseriti nel repository ambiente virtuale, `node_modules`, database reali, file `.env`, password o token.

## Stato corrente fase 16 - decisione formato e primo dominio (2026-10-22)

Questa sezione aggiorna lo stato corrente; le descrizioni precedenti conservano
la cronologia e non dichiarano nuovamente aperte le fasi gia' unite.
Fase 15 integrata in main con PR 14, merge 6dcdc83. Fase 16 solo su
phase-16-admin-pilot-inventory, PR 15 in bozza, senza merge autorizzato.

Alle 18:49 CEST l'autore conferma il contratto gia' usato dall'applicazione:
Deck.cards resta TEXT con array JSON di name, path e copies. Si mantengono i
percorsi correnti relativi ai media, inclusi cards/starter/velocita-1.webp;
nessuna conversione al precedente esempio path/value o a /images/cards.
Questa decisione aggiorna quel precedente requisito per la fase 16. Nessuna
migrazione, modifica del DB reale, nuovo scaffold o dipendenza introdotta.

backend/app/services/admin_card_transfers.py prepara una copia indipendente dei
cinque contenitori e applica una copia per clic nelle sole direzioni approvate.
Non modifica gli input neppure su errore; non espone endpoint e non salva dati.
Nessuna aggiunta pool/mazzo, nessuna doppia sottrazione. I nomi mantengono
l'identita' normalizzata esistente e le immagini non vengono sostituite.

backend/tests/test_admin_card_transfers.py: 19 test unitari, con cinque sottocasi
per le direzioni. Eseguiti con unittest nell'ambiente isolato dell'assistente
usando cards.py verificato contro il blob b329ece85fef6cc232ef322cb857108088ea5cf7;
esito 19/19 OK. Rieseguiti da questo workflow prima del commit documentale.
Non sono test transazionali/HTTP o di concorrenza, ne' collaudo browser.
La precedente CI 39815434564 era verde prima di questo incremento: non ne e'
una verifica. Rileggere la CI sul nuovo codice; nessun nuovo verde globale gia'
dichiarato. Setup, script d'avvio e schema DB restano invariati.

Da completare nel blocco backend approvato: rotte/DTO admin, iscrizione e username,
letture dei cinque Deck, versioni e salvataggio atomico senza retry automatici,
blocchi gara/revisione/chiusura, eventi privati e segnali senza carte nel payload,
coordinamento con move_card e create_race per il controllo esatto delle 15 copie.
Poi frontend, conferma testuale, live autorizzato e prove browser. Il dominio
puro non garantisce ancora queste integrazioni e non va presentato come funzione
utilizzabile. Nessun test, reset o migrazione sul database reale autorizzato.
