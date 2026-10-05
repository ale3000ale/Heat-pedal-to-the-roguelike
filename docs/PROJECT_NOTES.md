# Guida di lavoro — Heat

Questo file serve a chi lavora sul progetto (anche l'assistente) per ripartire senza rileggere tutto. La fonte delle regole di gioco e di prodotto è `docs/PROJECT_SPEC.md`: qui ci sono mappa del codice, comandi, convenzioni e stato del lavoro. Si aggiorna passo passo, ogni volta che qualcosa cambia.

## Regole di lavoro con l'assistente

- Mai presumere: prima di modificare un file lo si legge, anche se si pensa di conoscerlo.
- Se le chiamate di un messaggio non bastano, si dichiara cosa manca e si salva qui il contesto, poi si prosegue nel messaggio successivo.
- I file esistenti si modificano solo dopo averli letti nella versione attuale del ramo.

## Mappa del progetto

| Percorso | Contenuto |
|---|---|
| `heat.py` | Menu e comandi: `setup`, `start`, `migrate`, `test`, `check` |
| `backend/` | FastAPI, SQLAlchemy, Alembic (SQLite) |
| `backend/app/api/` | Router: `auth`, `teams`, `pilots`, `championships`, `races`, `pools`, `admin`; dipendenze in `deps.py` |
| `backend/app/config.py` | `DATABASE_URL`, cookie di sessione, `MEDIA_DIR` (`backend/media`) |
| `backend/app/db/models/` | Modelli SQLAlchemy (`deck.py`: `DeckPrototype` con `kind`, `Deck`; `championship.py`) |
| `backend/app/schemas/` | Schemi Pydantic delle risposte e delle richieste |
| `backend/app/services/` | Regole di business (campionati, pool, carte, immagini, nomi, ruoli, utenti) |
| `backend/app/scripts/` | `create_admin`, `seed_prototype`, `resize_cards` |
| `backend/alembic/versions/` | Migrazioni (elenco nella sezione 11 della specifica) |
| `backend/media/cards/` | Immagini delle carte (vedi sotto) |
| `backend/tests/` | Test; `conftest.py` crea un database SQLite in memoria con `create_all` (senza migrazioni) |
| `frontend/` | SvelteKit; pagine in `src/routes`, codice condiviso in `src/lib` |
| `tools/check-frontend.mjs` | format, check, lint e test del frontend in sequenza |
| `docs/` | Specifica, stato, note, domande aperte |

## Comandi utili

- Primo avvio o nuovo PC: `python heat.py setup`, poi `python heat.py start`.
- Dopo un `git pull`: `python heat.py migrate` (l'avvio migra comunque da solo).
- Test backend: `python heat.py test`. Controlli frontend: `python heat.py check`.
- Ridimensionare le carte, da `backend`: `python -m app.scripts.resize_cards [cartella] [--dry-run]`.

## Carte e immagini

Le immagini stanno in `backend/media/cards/`:

- `base/modifiche/`: pool di base delle modifiche.
- `base/sponsor/`: pool di base degli sponsor (predisposta).
- `starter/`: carte dell'inventario di partenza di ogni pilota. `STARTER_INVENTORY` (in `services/cards.py`) usa i file `velocita-1.webp` … `velocita-4.webp`, 3 copie ciascuno.
- `uploads/`: carte extra caricate in seguito, utilizzabili nella creazione delle pool.

Le cartelle le riempie a mano l'autore del progetto. Nomi dei file: `nome_N.ext`, con N pari al numero di copie. Le carte Calore non sono ancora state fotografate: per ora si considerano parte delle modifiche.

Lo script `resize_cards` porta ogni immagine (png, jpg, jpeg, webp) in WebP dentro la scatola massima di 560x870 px, senza tagliare, e lascia intatti i WebP già della misura giusta. Con `--dry-run` mostra solo cosa farebbe. Non cancella gli originali: la ricarica usa soltanto i WebP.

## Pool di base e ricarica

- Tipi: `modifiche` e `sponsor`. Nomi tecnici delle pool di base: `default` (modifiche) e `sponsor`, definiti in `BASE_POOL_NAMES` (`services/pools.py`). La rinomina di `default` in `modifiche` non è stata fatta, per non rompere codice e test.
- Ricarica (`POST /api/pools/base/{kind}/reload`, solo admin): legge `backend/media/cards/base/<tipo>` e **aggiunge soltanto** in fondo le carte nuove; non modifica e non toglie mai quelle presenti. Una carta è già presente se coincide il nome (senza distinguere le maiuscole) o il percorso. File senza `_N` finale: scartati con avviso. File non WebP senza il loro WebP: avviso. Cartella assente: avviso.
- Il database di prova non contiene la pool `sponsor` se un test non la crea: in quel caso il campionato nasce senza copia degli sponsor.
- Il campionato ha `pool_deck_id` (copia delle modifiche) e `sponsor_pool_deck_id` (copia degli sponsor).

## Convenzioni

- Testi dell'interfaccia, commenti e messaggi di errore in italiano.
- Ogni cambiamento di schema richiede una migrazione Alembic.
- Le regole stanno nei `services`, i router traducono gli errori in codici HTTP.
- Ogni risposta che descrive un utente deve ammettere i ruoli `admin`, `judge`, `player`.
- Nelle liste `{#each}` la chiave deve essere univoca: il rango della classifica non lo è (vedi `src/lib/standings.ts`).
- Il lavoro avanza sul ramo `phase-8-frontend`; prima di unire a `main` devono passare `python heat.py test` e `python heat.py check`.
- I documenti si aggiornano al momento, non a fine fase.

## Contesto di lavoro (5 ottobre 2026, sera)

Fase 8b (backend delle due pool di base):

- Fatto: colonna `kind`, `sponsor_pool_deck_id`, migrazione `e5b9c3d7a2f8`, `services/pools.py` (pool di base per tipo, ricarica), `services/championships.py` (due copie di pool, cancellazione di entrambe), schemi e router `pools` e `championships`, `seed_prototype` per entrambe le pool.
- Test: 156 passati prima dei test nuovi. Scritto `tests/test_pool_kinds_api.py` (ricarica, tipo delle pool, campionato con due pool): da eseguire con `python heat.py test`.
- Da fare, in ordine:
  1. Eseguire i test nuovi e correggere eventuali errori.
  2. Leggere `app/main.py` e aggiungere l'avviso nel log all'avvio se le cartelle `base/` contengono carte non ancora nelle pool (nessuna scrittura nel database).
  3. Correggere `PROJECT_SPEC.md`: nome tecnico `default` per le modifiche, migrazione `e5b9c3d7a2f8` nella sezione 11.
  4. Fase 8c (frontend admin): leggere `frontend/src/lib` (helper `api`) e `src/routes/admin/users`; poi pagina pool con "Ricarica", creazione campionato con due scelte, chiusura e cancellazione.

## Questioni aperte

- Uso della pool degli sponsor nel gioco: predisposta ma non ancora usata.
- Le voci di fine specifica (Negozio, pacchetti, spareggio, interfaccia di caricamento carte).
