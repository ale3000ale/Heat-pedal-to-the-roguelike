# Guida di lavoro — Heat

Questo file serve a chi lavora sul progetto (anche l'assistente) per ripartire senza rileggere tutto. La fonte delle regole di gioco e di prodotto è `docs/PROJECT_SPEC.md`: qui ci sono mappa del codice, comandi, convenzioni e stato del lavoro. Si aggiorna passo passo, ogni volta che qualcosa cambia.

## Mappa del progetto

| Percorso | Contenuto |
|---|---|
| `heat.py` | Menu e comandi: `setup`, `start`, `migrate`, `test`, `check` |
| `backend/` | FastAPI, SQLAlchemy, Alembic (SQLite) |
| `backend/app/api/` | Router: `auth`, `teams`, `pilots`, `championships`, `races`, `pools`, `admin`; dipendenze in `deps.py` |
| `backend/app/db/models/` | Modelli SQLAlchemy (es. `deck.py` con `DeckPrototype`) |
| `backend/app/schemas/` | Schemi Pydantic delle risposte e delle richieste |
| `backend/app/services/` | Regole di business (campionati, pool, carte, immagini, nomi, ruoli, utenti) |
| `backend/app/scripts/` | `create_admin`, `seed_prototype`, `resize_cards` |
| `backend/alembic/versions/` | Migrazioni (elenco nella sezione 11 della specifica) |
| `backend/media/cards/` | Immagini delle carte (vedi sotto) |
| `frontend/` | SvelteKit; pagine in `src/routes`, codice condiviso in `src/lib` |
| `tools/check-frontend.mjs` | format, check, lint e test del frontend in sequenza |
| `docs/` | Specifica e questa guida |

## Comandi utili

- Primo avvio o nuovo PC: `python heat.py setup`, poi `python heat.py start`.
- Dopo un `git pull`: `python heat.py migrate` (l'avvio migra comunque da solo).
- Test backend: `python heat.py test`. Controlli frontend: `python heat.py check`.
- Ridimensionare le carte, da `backend`: `python -m app.scripts.resize_cards [cartella] [--dry-run]`.

## Carte e immagini

Le immagini stanno in `backend/media/cards/`:

- `base/modifiche/`: pool di base delle modifiche.
- `base/sponsor/`: pool di base degli sponsor (predisposta).
- `starter/`: carte dell'inventario di partenza di ogni pilota (Velocità 1-4).
- `uploads/`: carte extra caricate in seguito, utilizzabili nella creazione delle pool.

Le cartelle le riempie a mano l'autore del progetto. Nomi dei file: `nome_N.ext`, con N pari al numero di copie. Le carte Calore non sono ancora state fotografate: per ora si considerano parte delle modifiche.

Lo script `resize_cards` porta ogni immagine (png, jpg, jpeg, webp) in WebP dentro la scatola massima di 560x870 px, senza tagliare. Lavora su tutta la cartella indicata, sottocartelle comprese, e lascia intatti i WebP già della misura giusta. Con `--dry-run` mostra solo cosa farebbe.

### Ricarica delle pool di base

Regola decisa: la ricarica solo **aggiunge** le carte nuove in fondo alla pool e non modifica né toglie quelle esistenti, perché nomi e quantità corretti a mano non vadano persi. Una carta è già presente se coincide nome o percorso. File senza `_N` finale: scartati con avviso. All'avvio nessuna scrittura, solo un avviso nel log. Dettagli nella sezione 6 della specifica.

## Convenzioni

- Testi dell'interfaccia, commenti e messaggi di errore in italiano.
- Ogni cambiamento di schema richiede una migrazione Alembic.
- Le regole stanno nei `services`, i router traducono gli errori in codici HTTP.
- Ogni risposta che descrive un utente deve ammettere i ruoli `admin`, `judge`, `player`.
- Nelle liste `{#each}` la chiave deve essere univoca: il rango della classifica non lo è (vedi `src/lib/standings.ts`).
- Il lavoro avanza sul ramo `phase-8-frontend`; prima di unire a `main` devono passare `python heat.py test` e `python heat.py check`.
- I documenti si aggiornano al momento, non a fine fase.

## Stato del lavoro (5 ottobre 2026)

- Realizzato: tutto il backend delle fasi precedenti; frontend per login, registrazione, home, team, dettaglio pilota (mazzi in sola lettura), campionati con iscrizione, gare e classifica, gestione gare per admin e giudice, utenti e ruoli.
- In corso, nell'ordine:
  1. Backend: due pool di base (modifiche e sponsor) con colonna `kind`, seconda pool sul campionato, migrazione, ricarica delle pool.
  2. Frontend admin: pagina pool con "Ricarica", creazione campionato con due scelte, chiusura e cancellazione.
- Dopo: costruzione del mazzo da gioco, pulizia di team e piloti nascosti, Negozio.
- Endpoint già presenti: `/championships` (crea, chiudi, cancella) e `/pools` (elenco, dettaglio, crea, elimina); da adeguare alle due pool.

## Questioni aperte

- Dove nasce l'inventario iniziale (Velocità 1-4 dalla cartella `starter/`): da verificare nel codice.
- Uso della pool degli sponsor nel gioco: predisposta ma non ancora usata.
- Le voci di fine specifica (Negozio, pacchetti, spareggio, interfaccia di caricamento carte).
