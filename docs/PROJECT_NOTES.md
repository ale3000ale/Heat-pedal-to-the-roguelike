# Guida di lavoro — Heat

Questo file serve a chi lavora sul progetto (anche l'assistente) per ripartire senza rileggere tutto. La fonte delle regole di gioco e di prodotto è `docs/PROJECT_SPEC.md`: qui ci sono mappa del codice, comandi, convenzioni e stato del lavoro. Si aggiorna passo passo, ogni volta che qualcosa cambia.

## Regole di lavoro con l'assistente

- Mai presumere: prima di modificare un file lo si legge, anche se si pensa di conoscerlo.
- Se le chiamate di un messaggio non bastano, si dichiara cosa manca e si salva qui il contesto, poi si prosegue nel messaggio successivo.
- I file esistenti si modificano solo dopo averli letti nella versione attuale del ramo.
- Un messaggio vuoto dell'utente significa "continua, mi sta bene".

## Mappa del progetto

| Percorso | Contenuto |
|---|---|
| `heat.py` | Menu e comandi: `setup`, `start`, `migrate`, `test`, `check` |
| `backend/` | FastAPI, SQLAlchemy, Alembic (SQLite) |
| `backend/app/api/` | Router: `auth`, `teams`, `pilots`, `championships`, `races`, `pools`, `admin`; dipendenze in `deps.py` |
| `backend/app/config.py` | `DATABASE_URL`, cookie di sessione, `MEDIA_DIR` (`backend/media`) |
| `backend/app/db/models/` | Modelli SQLAlchemy (`deck.py`: `DeckPrototype` con `kind`, `Deck` con `version`; `championship.py`: `Championship`, `ChampionshipDefaults`, `GOLD_FIELDS`) |
| `backend/app/schemas/` | Schemi Pydantic delle risposte e delle richieste |
| `backend/app/services/` | Regole di business: campionati, gare (`races.py`), oro (`gold.py`), pool, carte, mazzi (`pilot_deck.py`), piloti, pulizia, immagini, nomi, ruoli, sessioni, team, utenti |
| `backend/app/scripts/` | `create_admin`, `seed_prototype`, `resize_cards` |
| `backend/alembic/versions/` | Migrazioni (elenco nella sezione 11 della specifica) |
| `backend/media/cards/` | Immagini delle carte (vedi sotto) |
| `backend/tests/` | Test; `conftest.py` crea un database SQLite in memoria con `create_all` (senza migrazioni) |
| `frontend/` | SvelteKit; pagine in `src/routes`, codice condiviso in `src/lib` |
| `tools/check-frontend.mjs` | format, check, lint e test del frontend in sequenza |
| `.github/` | CI: test backend e controlli frontend a ogni pull request |
| `docs/` | Specifica, stato, note, domande aperte; documenti storici di bootstrap e autenticazione |

## Comandi utili

- Primo avvio o nuovo PC: `python heat.py setup`, poi `python heat.py start`.
- Dopo un `git pull` o un cambio di ramo: `python heat.py migrate` (l'avvio migra comunque da solo).
- Test backend: `python heat.py test` (224 test alla chiusura della fase 11). Controlli frontend: `python heat.py check`.
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

## Gare e oro

- `services/races.py`: `create_race` rifiuta un campionato chiuso e una gara già in corso (`RaceInProgressError`); la data è quella della creazione. `set_results` accetta l'elenco ordinato, i punti sponsor e, facoltativo, la lista degli assenti: se presente, ogni iscritto deve stare in classifica o tra gli assenti.
- `services/gold.py`: regole `GoldRules` (base, modificatori per le posizioni 1-6, modificatore "altre"), limiti `MAX_GOLD_BASE` e `MAX_GOLD_MODIFIER`, impostazioni generali in `ChampionshipDefaults` (riga con id 1). L'oro si assegna una sola volta, alla prima chiusura della gara; le correzioni non lo toccano.
- Il dettaglio di una gara mostra anche gli iscritti assenti con posizione vuota e 0 punti.

## Convenzioni

- Testi dell'interfaccia, commenti e messaggi di errore in italiano.
- Ogni cambiamento di schema richiede una migrazione Alembic.
- Le regole stanno nei `services`, i router traducono gli errori in codici HTTP.
- Ogni risposta che descrive un utente deve ammettere i ruoli `admin`, `judge`, `player`.
- Nelle liste `{#each}` la chiave deve essere univoca: il rango della classifica non lo è (vedi `src/lib/standings.ts`).
- Niente `dialog` né `confirm` nativi: si usano i popup propri.
- Il lavoro avanza su un ramo per fase (ora `phase-12-shop`); prima di unire a `main` devono passare `python heat.py test` e `python heat.py check` (la CI li esegue a ogni pull request).
- I documenti si aggiornano al momento, non a fine fase.

## Contesto di lavoro (7 ottobre 2026)

Le fasi 8, 9, 10 e 11 sono concluse e unite a `main` (pull request #1, #2, #3 e #4). La fase 11 ha portato oro per gara con regole per campionato e impostazioni generali, popup propri, una sola gara in corso, data automatica, assenti espliciti e conferma d'uscita dalla gara. La fase 12 (Negozio e pacchetti) è iniziata sul ramo `phase-12-shop`, ma le regole non sono definite: le 19 domande sono in `OPEN_QUESTIONS.md`.

Da fare, in ordine:

1. Ricevere le risposte alle domande sul Negozio (priorità: punti 1, 4, 7, 8, 9 e 12).
2. Proporre e far approvare lo schema delle tabelle del Negozio e le regole in `PROJECT_SPEC.md`.
3. Implementare backend (migrazione, servizi, API, test) e poi frontend.

## Questioni aperte

- Uso della pool degli sponsor nel gioco: predisposta ma non ancora usata.
- Le voci di fine specifica (Negozio, pacchetti, spareggio, interfaccia di caricamento carte): dettaglio in `OPEN_QUESTIONS.md`.
