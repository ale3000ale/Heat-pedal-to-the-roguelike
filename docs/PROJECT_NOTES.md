# Guida di lavoro — Heat

Questo file serve a chi lavora sul progetto (anche l'assistente) per ripartire senza rileggere tutto. La fonte delle regole di gioco e di prodotto è `docs/PROJECT_SPEC.md`: qui ci sono mappa del codice, comandi, convenzioni e stato del lavoro. Si aggiorna passo passo, ogni volta che qualcosa cambia.

## Regole di lavoro con l'assistente

- Mai presumere: prima di modificare un file lo si legge, anche se si pensa di conoscerlo.
- Se le chiamate di un messaggio non bastano, si dichiara cosa manca e si salva qui il contesto, poi si prosegue nel messaggio successivo.
- I file esistenti si modificano solo dopo averli letti nella versione attuale del ramo.
- Un messaggio vuoto dell'utente significa "continua, mi sta bene".
- I documenti si riallineano quando una modifica è finita e i controlli sono andati a buon fine.

## Mappa del progetto

| Percorso | Contenuto |
|---|---|
| `heat.py` | Menu e comandi: `setup`, `start`, `migrate`, `test`, `check` |
| `backend/` | FastAPI, SQLAlchemy, Alembic (SQLite) |
| `backend/app/api/` | Router: `auth`, `teams`, `pilots`, `championships`, `races`, `pools`, `admin` e quelli del Negozio; dipendenze in `deps.py` |
| `backend/app/config.py` | `DATABASE_URL`, cookie di sessione, `MEDIA_DIR` (`backend/media`) |
| `backend/app/db/models/` | Modelli SQLAlchemy (`deck.py`: `DeckPrototype` con `kind`, `Deck` con `version`; `championship.py`: `Championship`, `ChampionshipDefaults`, `GOLD_FIELDS`; `shop.py`: tabelle del Negozio, tra cui `PackPurchase`) |
| `backend/app/schemas/` | Schemi Pydantic delle risposte e delle richieste |
| `backend/app/services/` | Regole di business: campionati, gare (`races.py`), oro (`gold.py`), pool, carte, mazzi (`pilot_deck.py`), piloti, pulizia, immagini, nomi, ruoli, sessioni, team, utenti; Negozio: `packs.py`, `pack_images.py`, `shop_draw.py`, `shop_purchase.py`, `shop_view.py`, `shop_history.py`, `shop_inventory.py` |
| `backend/app/scripts/` | `create_admin`, `seed_prototype`, `resize_cards` |
| `backend/alembic/versions/` | Migrazioni (elenco nella sezione 11 della specifica) |
| `backend/media/cards/` | Immagini delle carte (vedi sotto) |
| `backend/media/pack/` | Immagini dei pacchetti (`defaultIllustration`, `illustration`) |
| `backend/tests/` | Test; `conftest.py` crea un database SQLite in memoria con `create_all` (senza migrazioni) |
| `frontend/` | SvelteKit; pagine in `src/routes`, codice condiviso in `src/lib` |
| `tools/check-frontend.mjs` | format, check, lint e test del frontend in sequenza |
| `.github/` | CI: test backend e controlli frontend a ogni pull request |
| `docs/` | Specifica, stato, note, domande aperte, schema del Negozio; documenti storici di bootstrap e autenticazione |

## Comandi utili

- Primo avvio o nuovo PC: `python heat.py setup`, poi `python heat.py start`.
- Dopo un `git pull` o un cambio di ramo: `python heat.py migrate` (l'avvio migra comunque da solo).
- Test backend: `python heat.py test` (224 test alla chiusura della fase 11, 248 alla fine della 12a). Controlli frontend: `python heat.py check`.
- Ridimensionare le carte, da `backend`: `python -m app.scripts.resize_cards [cartella] [--dry-run]`.
- Il lint del frontend (`npm run lint`) esegue `prettier --check` e `eslint`: dopo ogni modifica a un file `.svelte` o `.ts` conviene lanciare `npx prettier --write` sul file (le righe troppo lunghe sono la causa più comune di errore).

## Carte e immagini

Le immagini stanno in `backend/media/cards/`:

- `base/modifiche/`: pool di base delle modifiche.
- `base/sponsor/`: pool di base degli sponsor (usata dai pacchetti per le carte sponsor).
- `starter/`: carte dell'inventario di partenza di ogni pilota. `STARTER_INVENTORY` (in `services/cards.py`) usa i file `velocita-1.webp` … `velocita-4.webp`, 3 copie ciascuno.
- `uploads/`: carte extra caricate in seguito, utilizzabili nella creazione delle pool.

Le cartelle le riempie a mano l'autore del progetto. Nomi dei file: `nome_N.ext`, con N pari al numero di copie. Le carte Calore non sono ancora state fotografate: per ora si considerano parte delle modifiche. Nel frontend i percorsi delle carte si servono con il prefisso `/media/`.

Lo script `resize_cards` porta ogni immagine (png, jpg, jpeg, webp) in WebP dentro la scatola massima di 560x870 px, senza tagliare, e lascia intatti i WebP già della misura giusta. Con `--dry-run` mostra solo cosa farebbe. Non cancella gli originali: la ricarica usa soltanto i WebP.

## Pool di base e ricarica

- Tipi: `modifiche` e `sponsor`. Nomi tecnici delle pool di base: `default` (modifiche) e `sponsor`, definiti in `BASE_POOL_NAMES` (`services/pools.py`). La rinomina di `default` in `modifiche` non è stata fatta, per non rompere codice e test.
- Ricarica (`POST /api/pools/base/{kind}/reload`, solo admin): legge `backend/media/cards/base/<tipo>`, aggiunge in fondo le carte nuove e toglie quelle il cui file non esiste più (solo nella cartella `cards/base/<tipo>/`; se la cartella manca o non ha immagini non toglie nulla). Le carte presenti non si modificano, così nomi e copie corretti a mano si conservano: una carta è già presente se coincide il nome (senza distinguere le maiuscole) o il percorso. File senza `_N` finale: scartati con avviso. File non WebP senza il loro WebP: avviso. Cartella assente: avviso.
- Anteprima (`GET /api/pools/base/{kind}/reload/preview`): stessa logica con `apply=False` in `reload_base_pool`, non scrive nulla; `preview_reload` indica per ogni carta da togliere se è nella copia di pool di un campionato attivo (`_active_championship_paths`). Il frontend la chiede prima della ricarica e apre un popup di conferma se ci sono carte da togliere.
- Le copie di pool dei campionati già creati non cambiano con la ricarica.
- Il database di prova non contiene la pool `sponsor` se un test non la crea: in quel caso il campionato nasce senza copia degli sponsor.
- Il campionato ha `pool_deck_id` (copia delle modifiche) e `sponsor_pool_deck_id` (copia degli sponsor).

## Gare e oro

- `services/races.py`: `create_race` rifiuta un campionato chiuso e una gara già in corso (`RaceInProgressError`); la data è quella della creazione. `set_results` accetta l'elenco ordinato, i punti sponsor e, facoltativo, la lista degli assenti: se presente, ogni iscritto deve stare in classifica o tra gli assenti. `list_races` restituisce le gare per numero; la pagina del campionato le mostra per data decrescente (a parità, numero decrescente).
- `services/gold.py`: regole `GoldRules` (base, modificatori per le posizioni 1-6, modificatore "altre"), limiti `MAX_GOLD_BASE` e `MAX_GOLD_MODIFIER`, impostazioni generali in `ChampionshipDefaults` (riga con id 1). L'oro si assegna una sola volta, alla prima chiusura della gara; le correzioni non lo toccano.
- Il dettaglio di una gara mostra anche gli iscritti assenti con posizione vuota e 0 punti.

## Negozio

- Regole e schema: `SHOP_DESIGN.md` e `SHOP_SCHEMA.md`. Backend completato (12a-12c); frontend in corso (12d, 12e).
- Acquisto (`services/shop_purchase.py`): una transazione sola. Prima delle letture prende un lock di processo e, su SQLite, `BEGIN IMMEDIATE` (`_lock_database`); su altri database il blocco sul database non è attivo. Tetto di 100 copie per carta nell'inventario (409).
- Pacchetti: se valuta e costo mancano valgono 10 oro; con valuta sponsor e costo mancante valgono 2 sponsor. Il modulo del frontend parte da 10 e passa a 2 cambiando valuta solo se il costo non è stato modificato a mano.
- Pagina del giocatore: `frontend/src/routes/championships/[id]/shop/+page.svelte`. In alto a destra stanno il pilota scelto con oro e punti sponsor e i pulsanti (Inventario in popup, link Storico verso la pagina `history`, scelta del pilota, impostazioni per l'admin). Decisione del 10 ottobre: un solo pulsante Inventario e lo Storico come pagina separata, non come previsto in `SHOP_DESIGN.md` prima della modifica (il documento è stato aggiornato).
- Ordinamento e ricerca dei pacchetti: `frontend/src/lib/shop-sort.ts` (`sortPacks`, `filterPacksByName`, `PACK_SORT_OPTIONS`, `DEFAULT_PACK_SORT`), con test in `shop-sort.spec.ts`. Predefinito: dal meno caro al più caro; a parità contano il nome e poi l'id. La scelta non viene salvata.
- Le impostazioni del campionato aperte dal negozio usano l'opzione `shopOnly` di `championship-settings.svelte` e mostrano solo pacchetti, pool completa e storico.
- Deploy online: un solo server con pochi worker (SQLite accetta una sola scrittura alla volta).

## Convenzioni

- Testi dell'interfaccia, commenti e messaggi di errore in italiano.
- Ogni cambiamento di schema richiede una migrazione Alembic.
- Le regole stanno nei `services`, i router traducono gli errori in codici HTTP.
- Ogni risposta che descrive un utente deve ammettere i ruoli `admin`, `judge`, `player`.
- Nelle liste `{#each}` la chiave deve essere univoca: il rango della classifica non lo è (vedi `src/lib/standings.ts`).
- Niente `dialog` né `confirm` nativi: si usano i popup propri (`confirm-dialog.svelte`). La pagina admin delle pool usa ancora `confirm` nativo per l'eliminazione di una pool: da sostituire.
- Il lavoro avanza su un ramo per fase (ora `phase-12-shop`); prima di unire a `main` devono passare `python heat.py test` e `python heat.py check` (la CI li esegue a ogni pull request).
- I documenti si aggiornano al momento, non a fine fase.

## Contesto di lavoro (10 ottobre 2026)

Le fasi 8, 9, 10 e 11 sono concluse e unite a `main` (pull request #1, #2, #3 e #4). La fase 12 (Negozio e pacchetti) è sul ramo `phase-12-shop` (pull request #5, in bozza): backend 12a-12c completato e approvato; controlli verdi dopo le modifiche alla pagina del negozio (ordinamento, ricerca, saldo in alto a destra).

Da fare, in ordine:

1. Riallineare `PROJECT_SPEC.md`, `SHOP_SCHEMA.md` e `OPEN_QUESTIONS.md` con le regole del Negozio e le decisioni del 10 ottobre (`SHOP_DESIGN.md`, `PROJECT_STATUS.md` e questo file sono già allineati).
2. Sottofase 12d: verificare le altre pagine del giocatore (barra di navigazione, scelta del pilota, pagina dello storico, popup di inventario, animazione) e completare quanto manca.
3. Sottofase 12e: frontend admin (impostazioni del negozio, pacchetti, template, cronologia).
4. Sottofase 12f: documenti finali, verifica complessiva e unione in `main`.

## Questioni aperte

- Avviso per un template di negozio senza pacchetti (da riportare in `SHOP_SCHEMA.md`).
- Carte sponsor a consumo, spareggio, amministrazione delle carte e pool reale: dettaglio in `OPEN_QUESTIONS.md`.
