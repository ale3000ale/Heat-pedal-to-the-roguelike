# Guida di lavoro — Heat

Questo file serve a chi lavora sul progetto (anche l'assistente) per ripartire senza rileggere tutto. La fonte delle regole di gioco e di prodotto è `docs/PROJECT_SPEC.md`: qui ci sono mappa del codice, comandi, convenzioni e stato del lavoro. Si aggiorna passo passo, ogni volta che qualcosa cambia.

Ultimo riallineamento: 2026-10-13.

## Regole di lavoro con l'assistente

- Mai presumere: prima di modificare un file lo si legge, anche se si pensa di conoscerlo.
- Se le chiamate di un messaggio non bastano, si dichiara cosa manca e si salva qui il contesto, poi si prosegue nel messaggio successivo.
- I file esistenti si modificano solo dopo averli letti nella versione attuale del ramo.
- Un messaggio vuoto dell'utente significa "continua, mi sta bene".
- I documenti si riallineano quando una modifica è finita e i controlli sono andati a buon fine.
- Non si creano rami per le sottofasi: tutto il lavoro della fase 13 resta nel ramo `phase-13a-card-plays` (decisione dell'autore del 2026-10-12). Un ramo creato per errore, `phase-13a-judge-guard-tests`, è stato unito con la pull request #11 e non compare più tra i rami.
- Non si scrive che un test è stato eseguito se l'esito non è stato letto o riferito: in caso di dubbio lo si dichiara.

## Mappa del progetto

| Percorso | Contenuto |
|---|---|
| `heat.py` | Menu e comandi: `setup`, `start`, `migrate`, `test`, `check` |
| `backend/` | FastAPI, SQLAlchemy, Alembic (SQLite) |
| `backend/app/api/` | Router: `auth`, `teams`, `pilots`, `championships`, `races`, `pools`, `admin` e quelli del Negozio; per la fase 13 anche `race_review.py` (revisione, riepilogo, correzioni); dipendenze in `deps.py` |
| `backend/app/config.py` | `DATABASE_URL`, cookie di sessione, `MEDIA_DIR` (`backend/media`) |
| `backend/app/db/models/` | Modelli SQLAlchemy (`deck.py`: `DeckPrototype` con `kind`, `Deck` con `version`; `championship.py`: `Championship`, `ChampionshipDefaults` (con `card_poll_seconds`), `GOLD_FIELDS`; `shop.py`: tabelle del Negozio, tra cui `PackPurchase`; fase 13: `CardPlay` (`card_play`), `CardGift` (`card_gift`) e le colonne `Race.review_started_at` e `Race.review_started_by_user_id`) |
| `backend/app/schemas/` | Schemi Pydantic delle risposte e delle richieste (`card_poll.py` per l'intervallo di controllo; `PilotDetail` include `sponsor_inventory`) |
| `backend/app/services/` | Regole di business: campionati, gare (`races.py`), oro (`gold.py`), pool, carte, mazzi (`pilot_deck.py`), piloti, pulizia, immagini, nomi, ruoli, sessioni, team, utenti; Negozio: `packs.py`, `pack_images.py`, `shop_draw.py`, `shop_purchase.py`, `shop_view.py`, `shop_history.py`, `shop_inventory.py`, `shop_list.py`; carte sponsor in gara: `card_play.py`, `card_play_close.py`, `card_gift.py`, `card_judge.py`, `race_review.py` |
| `backend/app/scripts/` | `create_admin`, `seed_prototype`, `resize_cards` |
| `backend/alembic/versions/` | Migrazioni (elenco nella sezione 11 della specifica) |
| `backend/media/cards/` | Immagini delle carte (vedi sotto) |
| `backend/media/pack/` | Immagini dei pacchetti (`defaultIllustration`, `illustration`) |
| `backend/tests/` | Test; `conftest.py` crea un database SQLite in memoria con `create_all` (senza migrazioni) |
| `frontend/` | SvelteKit; pagine in `src/routes`, codice condiviso in `src/lib` |
| `tools/check-frontend.mjs` | format, check, lint e test del frontend in sequenza |
| `.github/` | CI: test backend e controlli frontend a ogni pull request |
| `docs/` | Specifica, stato, note, domande aperte, progetto e schema del Negozio, specifica della fase 13; documenti storici di bootstrap e autenticazione |

## Comandi utili

- Primo avvio o nuovo PC: `python heat.py setup`, poi `python heat.py start`.
- Dopo un `git pull` o un cambio di ramo: `python heat.py migrate` (l'avvio migra comunque da solo).
- Test backend: `python heat.py test` (224 test alla chiusura della fase 11, 248 alla fine della 12a; il numero attuale, dopo la fase 13, non è stato aggiornato qui). Controlli frontend: `python heat.py check`.
- Ridimensionare le carte, da `backend`: `python -m app.scripts.resize_cards [cartella] [--dry-run]`.
- Il lint del frontend (`npm run lint`) esegue `prettier --check` e `eslint`: dopo ogni modifica a un file `.svelte` o `.ts` conviene lanciare `npx prettier --write` sul file (le righe troppo lunghe sono la causa più comune di errore).
- Dopo un'unione di teste Alembic, `alembic downgrade -1` dà "Ambiguous walk": si usa la revisione precisa.

## Carte e immagini

Le immagini stanno in `backend/media/cards/`:

- `base/modifiche/`: pool di base delle modifiche.
- `base/sponsor/`: pool di base degli sponsor (usata dai pacchetti per le carte sponsor).
- `starter/`: carte dell'inventario di partenza di ogni pilota. `STARTER_INVENTORY` (in `services/cards.py`) usa i file `velocita-1.webp` … `velocita-4.webp`, 3 copie ciascuno.
- `uploads/`: carte extra caricate in seguito, utilizzabili nella creazione delle pool.

Le cartelle le riempie a mano l'autore del progetto. Nomi dei file: `nome_N.ext`, con N pari al numero di copie. Le carte Calore non sono ancora state fotografate: per ora si considerano parte delle modifiche. Nel frontend i percorsi delle carte si servono con il prefisso `/media/` (nella revisione della pagina della gara, `/media/cards/`).

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
- Alla prima chiusura di una gara, `set_results` richiama nella stessa transazione `consume_plays` (`services/card_play_close.py`): vedi la sezione sulle carte sponsor.

## Carte sponsor in gara (fase 13)

Le decisioni stanno in `PHASE_13_SPEC.md`, lo stato per sottofase in `PROJECT_STATUS.md`. Riassunto per ripartire:

- Giocata (13a): tabella `card_play` con stato `giocata`, `annullata` o `consumata`. Le copie disponibili sono quelle dell'inventario sponsor meno le giocate attive della gara in corso; l'inventario non cambia durante la gara. Massimo 5 annullamenti consecutivi, azzerati giocando una nuova carta. Alla prima chiusura della gara le giocate attive diventano `consumata`, escono dall'inventario del pilota e tornano nella pool sponsor del campionato; le annullate restano in inventario. Le righe del registro non si cancellano mai durante il gioco.
- Revisione (13b): "termina gara" apre la revisione (`Race.review_started_at`, `Race.review_started_by_user_id`) e chi la avvia è il revisore unico: ogni altro utente, giudici e admin compresi, riceve 409. Durante la revisione giocata, annullamento del giocatore e tasto S sono bloccati (409). Scadenza di 15 minuti con conferma automatica fatta da `settle_expired_reviews` alla prima richiesta successiva, senza processi in background. Il revisore può rinunciare o confermare; con la revisione scaduta o mai aperta può confermare solo l'admin. L'admin può riaprire la revisione confermata dell'ultima gara (`reopen_review`, `is_last_race`): 403 a chi non è admin, 409 per gara non ultima o revisione non confermata.
- Correzioni del revisore (`services/card_judge.py`): `get_card_summary`, `cancel_play` (anche di giocate già consumate, solo se la pool ha ancora una copia uguale, altrimenti 409), `grant_bonus` e `remove_card`. Tutte passano da `_reviewed_race`.
- Tasto S (13b e 13d): `draw_gift` in `services/card_gift.py` estrae una carta dalla pool sponsor con probabilità proporzionale alle copie e la mette nell'inventario del pilota con una notifica (`card_gift`, `seen_at` vuoto finché non vista). Il giocatore agisce solo sui propri piloti, giudice e admin su qualsiasi pilota iscritto (`_load_gift_pilot`, `_authorize_gift`). Serve una gara in corso non in revisione e almeno una copia in pool.
- Intervallo di controllo (13c-1): `card_poll_seconds` su `championship_defaults`, da 1 a 10 secondi, predefinito 5; `GET /api/admin/card-poll` per ogni utente collegato, `PUT` solo per l'admin. Vale per tutti i campionati, anche quelli già creati. Il frontend lo legge una volta all'apertura della pagina del campionato (`lib/card-poll.svelte.ts`).
- Frontend (13c e 13d, parziale): sezione a scomparsa per pilota con uso delle carte (`components/pilot-card-plays.svelte`), popup "Hai ottenuto una carta sponsor" (`components/card-gift-popup.svelte`), inventario del pilota in due sezioni "Modifiche" e "Sponsor", tasto S nella pagina della gara (`components/pilot-gift-button.svelte`) e campo dell'intervallo nelle impostazioni generali (`lib/card-poll-form.ts`). Da fare: Indietro (13c) e la revisione nella pagina della gara (13d).
- Test della fase: `test_card_plays.py`, `test_card_gifts.py`, `test_card_judge.py`, `test_card_judge_reopen.py`, `test_race_review.py`, `test_race_review_reopen.py`, `test_card_poll_settings.py` e 3 test dell'inventario sponsor in `test_pilot_deck_api.py`. Le funzioni di supporto sono in `test_race_review.py`; in `test_card_judge.py` e nei file più vecchi alcune sono ancora ricopiate e la duplicazione si può ripulire. I test della pull request #11 (commit `2f12768`) riguardano scadenza della revisione, secondo giudice, bonus e annullo.
- Il frontend delle carte non ha test dedicati ai componenti nuovi: la CI conferma solo type-check, lint e build.

## Negozio

- Regole e schema: `SHOP_DESIGN.md` e `SHOP_SCHEMA.md`. Fase 12 completata e unita in `main` con la pull request #5 (commit `6dd5619`).
- Acquisto (`services/shop_purchase.py`): una transazione sola. Prima delle letture prende un lock di processo e, su SQLite, `BEGIN IMMEDIATE` (`_lock_database`); su altri database il blocco sul database non è attivo. Tetto di 100 copie per carta nell'inventario (409).
- Elenco dei negozi dell'utente: `GET /api/me/shops` (`api/shop_me.py`, `services/shop_list.py`), usato dalla voce "Negozio" della barra di navigazione e dalla scelta del pilota.
- Pacchetti: se valuta e costo mancano valgono 10 oro; con valuta sponsor e costo mancante valgono 2 sponsor. Il modulo del frontend parte da 10 e passa a 2 cambiando valuta solo se il costo non è stato modificato a mano.
- Pagina del giocatore: `frontend/src/routes/championships/[id]/shop/+page.svelte`. In alto a destra stanno il pilota scelto con oro e punti sponsor e i pulsanti (Inventario in popup, link Storico verso la pagina `history`, scelta del pilota, impostazioni per l'admin).
- Animazione di apertura (decisioni dell'11 ottobre): componente `components/pack-reveal.svelte`, fasi e tempi in `lib/pack-reveal-phases.ts` (test in `pack-reveal-phases.spec.ts`). La busta ha come texture l'immagine del pacchetto; la striscia superiore se ne va con uno strappo e la busta resta tagliata in alto. Poi le carte escono **una alla volta**, già scoperte: ogni tocco (o Invio, o Spazio) mostra la successiva, con il contatore "Carta N di M". Dopo l'ultima carta un altro tocco apre il **riepilogo finale**: griglia con le carte ottenute, ciascuna con immagine ed etichetta "Modifica" o "Sponsor", e il testo "Hai ottenuto N carte". Le copie uguali compaiono una sola volta con "x N" (`groupByCard` in `lib/pack-summary.ts`, test in `pack-summary.spec.ts`). Il tasto "Salta" porta al riepilogo da qualsiasi fase. La finestra si chiude con la X in ogni momento; il clic fuori e il tasto Esc valgono solo dal riepilogo (`done` di `pack-reveal.svelte`, passato a `closeOnOutside` di `modal.svelte`). Con il movimento ridotto si parte dalle carte. Busta, scorrimento e riepilogo sono solo CSS e markup, senza test dedicati, e sono stati verificati a mano dall'autore. `cardDelayMs` resta solo per il suo test.
- Ordinamento e ricerca dei pacchetti: `frontend/src/lib/shop-sort.ts` (`sortPacks`, `filterPacksByName`, `PACK_SORT_OPTIONS`, `DEFAULT_PACK_SORT`), con test in `shop-sort.spec.ts`. Predefinito: dal meno caro al più caro; a parità contano il nome e poi l'id. La scelta non viene salvata.
- Le impostazioni del campionato aperte dal negozio usano l'opzione `shopOnly` di `championship-settings.svelte` e mostrano solo pacchetti, pool completa e storico. Lo storico completo dell'admin è in `championship-history-panel.svelte` (rotta `history/all`).
- Deploy online: un solo server con pochi worker (SQLite accetta una sola scrittura alla volta).

## Convenzioni

- Testi dell'interfaccia, commenti e messaggi di errore in italiano.
- Ogni cambiamento di schema richiede una migrazione Alembic.
- Le regole stanno nei `services`, i router traducono gli errori in codici HTTP.
- Ogni risposta che descrive un utente deve ammettere i ruoli `admin`, `judge`, `player`.
- Nelle liste `{#each}` la chiave deve essere univoca: il rango della classifica non lo è (vedi `src/lib/standings.ts`).
- Niente `dialog` né `confirm` nativi: si usano i popup propri (`confirm-dialog.svelte`). La pagina admin delle pool usa ancora `confirm` nativo per l'eliminazione di una pool: da sostituire.
- Il lavoro avanza su un ramo per fase, non per sottofase (ora `phase-13a-card-plays`, con la pull request #9 in bozza); prima di unire a `main` devono passare `python heat.py test` e `python heat.py check` (la CI li esegue a ogni pull request).
- I documenti si aggiornano al momento, non a fine fase.

## Contesto di lavoro (13 ottobre 2026)

Le fasi da 8 a 12 sono concluse e unite a `main` (pull request da #1 a #5). La fase 13 (carte sponsor in gara e amministrazione delle carte) è nel ramo `phase-13a-card-plays`, pull request #9: completate 13a, 13b e 13c-1; in corso 13c (mancano Indietro e la verifica a mano del campo dell'intervallo e delle due sezioni dell'inventario) e 13d (fatto il tasto S nella pagina della gara, manca la revisione); da fare 13e, 13f e 13g. La pull request #11 ha unito nel ramo i test aggiuntivi sulla revisione (merge `f733886`, commit dei test `2f12768`); la CI di quel commit non è stata letta. L'esito dei test eseguiti in locale dall'autore dopo l'ultimo riallineamento non è stato registrato nei documenti.

Documenti riallineati alla fase 13: `PROJECT_SPEC.md` (commit `bc0fbfb`), `PHASE_13_SPEC.md` (commit `9405c97`) e questo file. Da riallineare: `PROJECT_STATUS.md` e `SHOP_DESIGN.md`. `DATABASE.md`, `SCRIPTS.md` e `SETUP.md` non esistono ancora in `docs/` e vanno creati; lo schema delle tabelle `card_play`, `card_gift` e delle colonne `card_poll_seconds`, `review_started_at` e `review_started_by_user_id` non è ancora descritto in un documento di schema.

Da fare, in ordine:

1. Finire 13c (Indietro) e 13d (revisione nella pagina della gara), poi 13e, 13f e 13g.
2. Riallineare `PROJECT_STATUS.md` e `SHOP_DESIGN.md` e creare `DATABASE.md`, `SCRIPTS.md` e `SETUP.md`.
3. Prima dell'unione in `main`, rileggere il diff di `PROJECT_SPEC.md` e verificare che `python heat.py test`, `python heat.py check` e la CI passino sull'ultimo commit.

## Questioni aperte

- Carte sponsor a consumo, spareggio, amministrazione delle carte e pool reale: dettaglio in `OPEN_QUESTIONS.md`.
