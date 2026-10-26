# Guida di lavoro — Heat

<!-- draft-validation-current:start -->

## Draft - stato verificato del 26 ottobre 2026

Questa sezione prevale esclusivamente sulle precedenti note di stato e verifica del flusso draft. Regole, specifiche delle altre fasi e contenuti storici restano conservati.

Base funzionale: commit 8ba03aa1aa8a20f8c346b3e20b4f1352d9b2d74a, ramo draft, PR #18 ancora in bozza e senza merge in main. Correzione delle chiavi del flusso e della proprieta delle risorse UI, non una nuova modifica di regole o API.

Verifiche lette: frontend (check, lint, test, build), runtime, backend pytest e migrazioni su database di test tutti success. Run CI 40269135082 e runtime 40269135447. I due job documentali di fase 16 sono skipped, non falliti.

Collaudo manuale positivo riferito dall autore il 26 ottobre alle 05:31: ora funziona tutto senza errori. Il riscontro segue i reset di presenze, zoom e mazzi e la correzione lifecycle. Non e un test browser automatizzato o una certificazione di tutti i dispositivi.

I checkpoint negativi precedenti restano come cronologia e non descrivono piu lo stato corrente del ciclo di reset UI della draft.

Questo riallineamento non cambia codice applicativo, dipendenze, lockfile o dati e non esegue nuovi test dell applicazione. Nessun rilascio, ZIP finale o merge implicito. Interventi grafici successivi sospesi fino alla scelta dell autore.

[Evidenze, cronologia e limiti della validazione](DRAFT_VALIDATION.md).
<!-- draft-validation-current:end -->

<!-- draft-backend-current:start -->
## Draft - backend consolidato e limiti correnti

Aggiornamento del 25 ottobre 2026, solo ramo draft e PR 18. Questa sezione aggiorna il solo stato del flusso draft e prevale sulle note storiche di avanzamento, senza alterare gli altri requisiti.

Sorgenti recuperati dall artefatto draft-backend-materialized della run 40152061495, job materialize-and-check concluso con success sul commit tecnico 1052e5d. Gli hash SHA-256 dei sorgenti sono conservati in docs/DRAFT_BACKEND_MANIFEST.json.

Prima della pubblicazione questo workflow verifica di nuovo pytest backend, upgrade/downgrade/upgrade con controlli dello schema e frontend check, lint, test e build. Esecuzione di pubblicazione: https://github.com/ale3000ale/Heat-pedal-to-the-roguelike/actions/runs/40153346360. Il controllo dedicato sul commit risultante documenta queste verifiche pre-push; non e una nuova esecuzione dei job ordinari della PR.

Nessun conteggio di test o warning inventato, nessun test locale o collaudo browser attestato. Nessun merge, rilascio, ZIP finale del progetto o intervento sul database reale. Il frontend draft non e implementato da questo consolidamento.

I nuovi moduli backend provengono dai checkpoint PR 18; i percorsi e gli hash dei sorgenti sono elencati in docs/DRAFT_BACKEND_MANIFEST.json. Non viene creato un secondo frontend o uno scaffold nuovo.
<!-- draft-backend-current:end -->

Questo file serve a chi lavora sul progetto (anche l'assistente) per ripartire senza rileggere tutto. La fonte delle regole di gioco e di prodotto è `docs/PROJECT_SPEC.md`: qui ci sono mappa del codice, comandi, convenzioni e stato del lavoro. Si aggiorna passo passo, ogni volta che qualcosa cambia.

Ultimo riallineamento: 2026-10-22.

## Contesto corrente - fase 15 chiusa

Il 2026-10-22 alle 00:47 CEST l'autore autorizza chiusura della fase 15 e
riallineamento di PROJECT_SPEC.md/PROJECT_STATUS.md con limiti pratici di
collaudo accettati: 2/3 non verificabili, 8/10 non eseguiti, mai convertiti
in PASS. Codice finale 1226172, CI 39674942800 verde e iscrizioni confermate
funzionanti. Ramo corrente phase-15-sse-sistemazione, PR 14 ancora separata
dal merge. Nessun ulteriore fix, test manuale obbligatorio o nuova fase avviati.
Le sezioni 13/14 e i comandi sotto conservano contesto storico: per timer,
polling, SSE e stato corrente leggere l'appendice della specifica e PHASE_15.md.
Nessuna migrazione o avvio sul DB originale senza autorizzazione e backup;
accettazione della fase non certifica produzione o risolve vulnerabilita'.
SHOP_DESIGN.md e questa guida riletti per il riallineamento, senza cambiare
regole del Negozio. Dettagli in PHASE_15_CLOSURE.md.

## Regole di lavoro con l'assistente

- Mai presumere: prima di modificare un file lo si legge, anche se si pensa di conoscerlo.
- Se le chiamate di un messaggio non bastano, si dichiara cosa manca e si salva qui il contesto, poi si prosegue nel messaggio successivo.
- I file esistenti si modificano solo dopo averli letti nella versione attuale del ramo.
- Un messaggio vuoto dell'utente significa "continua, mi sta bene".
- I documenti si riallineano quando una modifica è finita e i controlli sono andati a buon fine.
- Non si creano rami per le sottofasi: tutto il lavoro della fase 13 resta nel ramo `phase-13a-card-plays` (decisione dell'autore del 2026-10-12). Un ramo creato per errore, `phase-13a-judge-guard-tests`, è stato unito con la pull request #11 e non compare più tra i rami.
- Non si scrive che un test è stato eseguito se l'esito non è stato letto o riferito: in caso di dubbio lo si dichiara.
- Non si scrivono nei documenti file, rotte, numeri o hash che non sono stati letti: si copia da una fonte letta o si dichiara che manca.

## Mappa del progetto

| Percorso | Contenuto |
|---|---|
| `heat.py` | Menu e comandi: `setup`, `start`, `migrate`, `test`, `check` |
| `backend/` | FastAPI, SQLAlchemy, Alembic (SQLite) |
| `backend/app/api/` | Router: `auth`, `teams`, `pilots`, `championships`, `races`, `pools`, `admin` e quelli del Negozio; per la fase 13 anche `race_review.py` (revisione, riepilogo, correzioni) e `card_admin.py` (caricamento ed eliminazione delle carte, prefisso `/api/admin/cards`, registrato in `main.py` prima del router `admin`); dipendenze in `deps.py` |
| `backend/app/config.py` | `DATABASE_URL`, cookie di sessione, `MEDIA_DIR` (`backend/media`), `CARD_IMAGE_SIZE` (560x870) e `MAX_CARD_UPLOAD_BYTES` (dimensione massima del file caricato) |
| `backend/app/db/models/` | Modelli SQLAlchemy (`deck.py`: `DeckPrototype` con `kind`, `Deck` con `version`; `championship.py`: `Championship`, `ChampionshipDefaults` (con `card_poll_seconds`), `GOLD_FIELDS`; `shop.py`: tabelle del Negozio, tra cui `PackPurchase`; fase 13: `CardPlay` (`card_play`), `CardGift` (`card_gift`) e le colonne `Race.review_started_at` e `Race.review_started_by_user_id`) |
| `backend/app/schemas/` | Schemi Pydantic delle risposte e delle richieste (`card_poll.py` per l'intervallo di controllo; `card_admin.py` per caricamento ed eliminazione delle carte; `PilotDetail` include `sponsor_inventory`) |
| `backend/app/services/` | Regole di business: campionati, gare (`races.py`), oro (`gold.py`), pool, carte, mazzi (`pilot_deck.py`), piloti, pulizia, immagini, nomi, ruoli, sessioni, team, utenti; Negozio: `packs.py`, `pack_images.py`, `shop_draw.py`, `shop_purchase.py`, `shop_view.py`, `shop_history.py`, `shop_inventory.py`, `shop_list.py`; carte sponsor in gara: `card_play.py`, `card_play_close.py`, `card_gift.py`, `card_judge.py`, `race_review.py`; amministrazione delle carte: `card_upload.py`, `card_delete.py` |
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
- Test backend: `python heat.py test` (224 test alla chiusura della fase 11, 248 alla fine della 12a, 447 prima della 13e, 474 dopo la 13e: gli ultimi due numeri sono esiti riferiti dall'autore in locale). Controlli frontend: `python heat.py check`.
- Ridimensionare le carte, da `backend`: `python -m app.scripts.resize_cards [cartella] [--dry-run]`.
- Il lint del frontend (`npm run lint`) esegue `prettier --check` e `eslint`: dopo ogni modifica a un file `.svelte` o `.ts` conviene lanciare `npx prettier --write` sul file (le righe troppo lunghe sono la causa più comune di errore).
- Dopo un'unione di teste Alembic, `alembic downgrade -1` dà "Ambiguous walk": si usa la revisione precisa.

## Carte e immagini

Le immagini stanno in `backend/media/cards/`:

- `base/modifiche/`: pool di base delle modifiche.
- `base/sponsor/`: pool di base degli sponsor (usata dai pacchetti per le carte sponsor).
- `starter/`: carte dell'inventario di partenza di ogni pilota. `STARTER_INVENTORY` (in `services/cards.py`) usa i file `velocita-1.webp` … `velocita-4.webp`, 3 copie ciascuno.
- `uploads/<tipo>/`: carte caricate dall'admin (13e), file `nome_quantità.webp`, una cartella per tipo (`modifiche` o `sponsor`).

Le cartelle `base/` e `starter/` le riempie a mano l'autore del progetto; `uploads/` si riempie con il caricamento dell'admin. Nomi dei file: `nome_N.ext`, con N pari al numero di copie. Le carte Calore non sono ancora state fotografate: per ora si considerano parte delle modifiche. Nel frontend i percorsi delle carte si servono con il prefisso `/media/` (nella revisione della pagina della gara, `/media/cards/`).

Lo script `resize_cards` porta ogni immagine (png, jpg, jpeg, webp) in WebP dentro la scatola massima di 560x870 px, senza tagliare, e lascia intatti i WebP già della misura giusta. Con `--dry-run` mostra solo cosa farebbe. Non cancella gli originali: la ricarica usa soltanto i WebP.

## Pool di base e ricarica

- Tipi: `modifiche` e `sponsor`. Nomi tecnici delle pool di base: `default` (modifiche) e `sponsor`, definiti in `BASE_POOL_NAMES` (`services/pools.py`). La rinomina di `default` in `modifiche` non è stata fatta, per non rompere codice e test.
- Ricarica (`POST /api/pools/base/{kind}/reload`, solo admin): legge `backend/media/cards/base/<tipo>`, aggiunge in fondo le carte nuove e toglie quelle il cui file non esiste più (solo quelle con percorso `cards/base/<tipo>/`: le carte caricate non si toccano; se la cartella manca o non ha immagini non toglie nulla). Le carte presenti non si modificano, così nomi e copie corretti a mano si conservano: una carta è già presente se coincide il nome (senza distinguere le maiuscole) o il percorso. File senza `_N` finale: scartati con avviso. File non WebP senza il loro WebP: avviso. Cartella assente: avviso.
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
- Frontend (13c e 13d): sezione a scomparsa per pilota con uso delle carte (`components/pilot-card-plays.svelte`), popup "Hai ottenuto una carta sponsor" (`components/card-gift-popup.svelte`), inventario del pilota in due sezioni "Modifiche" e "Sponsor", tasto S nella pagina della gara (`components/pilot-gift-button.svelte`) e campo dell'intervallo nelle impostazioni generali (`lib/card-poll-form.ts`). Secondo `PHASE_13_SPEC.md` la 13d (tasto S sull'elenco piloti, revisione nella pagina della gara con riepilogo con immagini, correzioni e riapertura per l'admin) è confermata dall'autore il 2026-10-13, che ha verificato a mano il flusso e le migrazioni su una copia del database. Lo stato di Indietro (13c) non è scritto in `PHASE_13_SPEC.md`: va letto in `PROJECT_STATUS.md`.
- Test della fase: `test_card_plays.py`, `test_card_gifts.py`, `test_card_judge.py`, `test_card_judge_reopen.py`, `test_race_review.py`, `test_race_review_reopen.py`, `test_card_poll_settings.py`, i test della 13e (commit `14557ab`; i nomi dei file non sono stati riletti) e 3 test dell'inventario sponsor in `test_pilot_deck_api.py`. Le funzioni di supporto sono in `test_race_review.py`; in `test_card_judge.py` e nei file più vecchi alcune sono ancora ricopiate e la duplicazione si può ripulire. I test della pull request #11 (commit `2f12768`) riguardano scadenza della revisione, secondo giudice, bonus e annullo.
- Il frontend delle carte non ha test dedicati ai componenti nuovi: la CI conferma solo type-check, lint e build.

## Amministrazione delle carte (13e)

Regole complete in `PHASE_13_SPEC.md` (parte B). Riassunto per ripartire, riportato da quel documento:

- Rotte (solo admin, router `api/card_admin.py`): `POST /api/admin/cards?kind=&name=&copies=` carica una carta (il corpo è l'immagine già tagliata a 560x870; 201 con nome, percorso, copie e tipo; 404 pool di base mancante, 409 nome già usato, 413 file troppo grande, 422 immagine o dati non validi). `DELETE /api/admin/cards?kind=&name=` elimina una carta caricata dalla pool di base e cancella i file rimasti senza uso (risposta con `removed_files`; 404 se la carta non c'è, 409 se non è una carta caricata).
- Caricamento (`services/card_upload.py`): formati JPEG, PNG e WebP, misure esatte `CARD_IMAGE_SIZE` (altrimenti 422), conversione in WebP (qualità 90, senza trasparenza); nome senza spazi ai bordi, da 1 a 64 caratteri, senza punto iniziale e senza `/ \ : * ? " < > |`; copie da 1 a 999. Il file diventa `cards/uploads/<tipo>/nome_quantità.webp` e la carta entra in fondo alla pool di base. Se la scrittura nel database fallisce, il file viene rimosso. Nome già presente (senza distinguere le maiuscole) o file già esistente: 409.
- Limite del file: `MAX_CARD_UPLOAD_BYTES` in `config.py`; secondo il commento della rotta sono 2 MB, ma il valore numerico non è stato riletto. Oltre il limite: 413 se l'intestazione `content-length` lo rivela subito, altrimenti 422 dal servizio.
- Eliminazione (`services/card_delete.py`): solo le carte con percorso `cards/uploads/`; le carte di base e di partenza non si eliminano mai (409). Il file immagine resta finché un campionato usa la carta in una copia di pool; i file orfani si cancellano anche quando si cancella un campionato (`delete_championship`).
- Origine "caricata": si riconosce dal percorso, non da una colonna; la 13e non ha migrazioni. Dipendenza aggiunta: `python-multipart==0.0.32` in `backend/requirements.txt`.
- Commit del backend (dal 13 ottobre 2026): `d89f75d` (dipendenza), `ba7a587` (limiti), `358297a` (caricamento), `cb934d8` (eliminazione), `3a79199` (pulizia in `delete_championship`), `e26801e` (rotte), `14557ab` (test), `a5bbe26` e `020ef6e` (`delete_championship` cancella anche giocate e regali di carte delle gare, con test).
- Test: 474 test del backend passati in 60,54 secondi, esito riferito dall'autore. L'esito della CI della 13e non è stato riletto; la CI della testa del ramo (che comprende la 13e) è verde, letta il 18 ottobre 2026.
- Stato del frontend della 13f: vedi la sezione successiva (18 ottobre 2026).

## Frontend della 13f (18 ottobre 2026)

Regole in `PHASE_13_SPEC.md` (parte B, caricamento ed eliminazione). Stato:

- Fatto: logica pura con test (`lib/card-crop.ts` con `card-crop.spec.ts`, `lib/card-admin-api.ts` con `card-admin-api.spec.ts`, commit `9261af2`), componenti `card-crop-editor.svelte` (ritaglio 560x870 con zoom e spostamento), `card-upload-form.svelte` (nome, copie, file) e `pool-card-picker.svelte` (elenco con nomi in arancione per le carte caricate a mano e tasto «Elimina»), integrati nella pagina `routes/admin/pools/+page.svelte` (commit `e5cf313`; correzioni di lint `254b015`, `062629f`, `1391a70`, `8dbd7c2`).
- Esiti: l'autore ha riferito il 18 ottobre 2026 che test e CI sono passati tutti; la CI è stata letta il 18 ottobre 2026, verde sul commit `9f3b517` (esecuzione 38480483060: Backend pytest, Migrazioni e Frontend con successo).
- Tasti di esclusione (aggiunti il 18 ottobre 2026): `lib/pool-exclusion.ts` (`excludeCardGroup`, con test) e `isBaseCard` in `lib/card-origin.ts` (percorso `cards/base/`), con i due tasti «Escludi tutte le carte caricate» ed «Escludi tutte le carte di base» sopra l'elenco di `PoolCardPicker` in `routes/admin/pools/+page.svelte`. Azzera le copie scelte del gruppo nel solo modulo, senza toccare il database.
- Riepilogo del mazzo e sezione aperta (13c, aggiunti il 18 ottobre 2026): in fondo alla sezione per pilota di `pilot-card-plays.svelte` c'è l'intestazione «Mazzo da gioco» con la griglia di `CardTile` in sola lettura (copie nel mazzo), dati da `lib/pilot-deck-api.ts` (`fetchPilotGameDeck`, legge `game_deck` di `GET /api/pilots/{id}`) con il test `pilot-deck-api.spec.ts`; la sezione nasce già aperta quando il giocatore ha un solo pilota iscritto (proprietà `startOpen`, letta in `onMount` per il solo valore iniziale).
- Controlli locali del 18 ottobre 2026: `npm run check` (0 errori), `npm run lint`, `npm test` (110 test passati su 110: base misurata 101) e `npm run build` riusciti; backend non toccato.
- La 13f è completata: CI verde sul commit `5ed659e` (esecuzione 39126355821, letta il 18 ottobre 2026) e documenti riallineati; resta l'unione della pull request #9 in `main` (13g, incarico dell'autore del 18 ottobre 2026).

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

## Contesto di lavoro (18 ottobre 2026)

Le fasi da 8 a 12 sono concluse e unite a `main` (pull request da #1 a #5). Anche la fase 13 (carte sponsor in gara e amministrazione delle carte) è conclusa: la pull request #9 è stata unita in `main` il 18 ottobre 2026 (merge `cdea876`, testa precedente `68dd4d7`), con la 13f chiusa lo stesso giorno (tasti di esclusione delle pool personalizzate e riepilogo del mazzo nella sezione per pilota, commit `5ed659e`, CI verde). La fase 14 (sistemazione generale e miglioramenti) è da definire con l'autore. La pull request #11 aveva unito nel ramo i test aggiuntivi sulla revisione (merge `f733886`, commit dei test `2f12768`); la CI di quel commit non è stata letta. Dopo la 13e l'autore ha riferito 474 test del backend passati in locale; il 18 ottobre 2026 l'assistente ha eseguito in locale i controlli frontend (check, lint, 110 test, build) per la chiusura della 13f.

Documenti: `PHASE_13_SPEC.md` è aggiornata alla 13f (sezione «Avanzamento della 13f»); `PROJECT_STATUS.md`, `PROJECT_NOTES.md` e `README.md` riallineati alla 13f il 18 ottobre 2026; `PROJECT_SPEC.md` ha l'ultimo riallineamento noto nel commit `bc0fbfb`. `DATABASE.md` esiste in `docs/` dal 13 ottobre 2026 e descrive `card_play`, `card_gift`, le colonne della revisione e `card_poll_seconds`; `SETUP.md` e `SCRIPTS.md`, creati lo stesso giorno, descrivono installazione e comandi. La 13e e la 13f non aggiungono migrazioni: verificato il 18 ottobre 2026 nello storico di `backend/alembic/versions`, il cui ultimo commit è `57b4637` del 2026-10-12, prima della 13e.

Da fare, in ordine:

1. Con l'autore: definire la fase 14 (sistemazione generale, modifiche di vivibilità e miglioramenti; compreso il menu dell'intestazione che a 375 px sfora, trovato il 2026-10-18).
2. Unione del ramo `phase-12f-docs` (solo documenti) in `main`, a cura dell'autore.

## Questioni aperte

- Carte sponsor a consumo, spareggio, amministrazione delle carte e pool reale: dettaglio in `OPEN_QUESTIONS.md`.

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

## Fase 16 - Incremento API admin di lettura

Data: 2026-10-22. Solo ramo phase-16-admin-pilot-inventory, PR 15 in bozza.
Questo incremento espone letture, non il salvataggio o la gestione frontend.

## Contratto

- GET /api/admin/championships/{championship_id}/pilots: iscritti visibili,
  con pilot_id, name, user_id e username. Solo admin, mai password o sessioni.
- GET /api/admin/championships/{championship_id}/pilots/{pilot_id}/cards:
  metadati del pilota, read_only, blocked_reason e cinque contenitori distinti.
- Ogni contenitore espone available, id, version e cards nel formato corrente
  name/path/copies. Le pool assenti hanno available=false, id/version null e
  cards vuoto; una pool esistente ma vuota e' disponibile. Nessuna pool creata.
- Tutti i Deck presenti vengono letti con una sola query. Riferimenti duplicati
  o mancanti e JSON corrotto danno 409, non carte inventate o svuotate.
- Campionato chiuso, gara o revisione non confermata sono leggibili ma indicati
  in sola lettura. Nessuna conferma automatica della revisione dentro queste GET.
- Il servizio ricontrolla il ruolo oltre alla dipendenza HTTP AdminUser.
  Pilota nascosto o non iscritto: 404. Giudice e giocatore: 403; anonimo: 401.

## File e verifiche

Nuovi schemas/admin_pilot_cards.py, services/admin_pilot_cards.py e
api/admin_pilot_cards.py; main.py registra il router senza alterare lifespan.
Test HTTP in backend/tests/test_admin_pilot_cards_api.py: 13 casi, inclusi i
parametri per ruoli e revisione. Verificano anche assenza di modifiche a Deck
ed EventLog, immagini/versioni, pool assenti o vuote, dati corrotti e privacy.
Alla preparazione: parsing Python e git diff --check riusciti. Test HTTP non
eseguiti localmente: vanno eseguiti nel repository completo, senza dichiararli
PASS sulla sola analisi sintattica. Il workflow documentale li esegue prima di
riallineare i dieci documenti generali e di fase. La CI completa resta separata.

## Limiti e seguito

Nessuna POST/PUT di gestione carte, transazione di salvataggio, evento nuovo,
regola di avvio da 15, modifica ai movimenti del giocatore o interfaccia ancora
aggiunta da questo incremento. Quelle parti restano da implementare e testare.
Le versioni lette non autorizzano una futura scrittura: il salvataggio dovra'
ricontrollare ruolo, iscrizione, stato gara/revisione e tutti i contenitori.
Nessun nuovo schema DB, migrazione, dipendenza o accesso al DB reale. Restano
il formato confermato name/path/copies e i percorsi relativi ai media correnti.
Un messaggio vuoto o solo @GitHub approva la proposta pendente; le sole modifiche
documentali non richiedono attesa della CI applicativa. Nessun merge implicito.

<!-- phase16-admin-save:start -->
## Fase 16 - Salvataggio admin atomico

Aggiornamento: 2026-10-23. Ramo phase-16-admin-pilot-inventory, PR 15 in bozza.
Stato sintetico fase 16: Perimetro funzionale implementato, incluso live e riepilogo effettivo; CI 40026443509 riuscita su 2366d1d; riscontro manuale complessivamente positivo dell'autore, senza protocollo caso per caso; riallineamento finale documentale; nessun merge autorizzato.

L'intestazione H1 e la riga Stato sintetico fase 16 sono contratti del workflow.
Il titolo deve restare esattamente quello corrente; la riga di stato e' unica e
senza pipe. Questo documento consolida lo stato corrente; le note incrementali
precedenti restano nello storico Git. Non costituisce merge o rilascio in main.

### Contratto backend e conservazione delle copie

GET /api/admin/championships/{championship_id}/pilots restituisce iscritti visibili
con nome e username. GET e PUT sul percorso
/api/admin/championships/{championship_id}/pilots/{pilot_id}/cards leggono o
salvano il contesto del pilota. Accesso solo admin; nessun diritto ampliato al
giudice e nessuna modifica a utenti, team, ruoli, saldi o punteggi.

Il PUT riceve versions di tutti i cinque contenitori e transfers con soli
source/path. ID/version interi positivi; solo le due pool possono essere null.
Campi extra, destinazioni client e sostituzioni arbitrarie sono rifiutati.
Pool assente distinta da pool vuota, mai creata automaticamente. Riferimenti
Deck incoerenti o JSON corrotto non diventano contenitori validi o vuoti.

Ogni clic sposta una copia nelle sole direzioni approvate:
- game_deck verso modification_pool;
- modification_inventory verso modification_pool;
- sponsor_inventory verso sponsor_pool;
- modification_pool verso modification_inventory;
- sponsor_pool verso sponsor_inventory.

Nessun movimento diretto pool/mazzo, sponsor/mazzo o inventario/mazzo nella
schermata admin. Una rimozione dal mazzo non sottrae anche dall'inventario.
Il pianificatore clona gli input e rifiuta copie non valide, percorsi ambigui
e nomi associati a immagini discordanti, senza mutazioni parziali su errore.

Il backend ricontrolla ruolo, pilota visibile/iscritto, campionato chiuso, gara
aperta, revisione non confermata e tutte le versioni nella transazione. 409 per
conflitto, 422 per movimento non applicabile, senza retry automatici. Commit
unico di Deck/eventi e rollback anche su errore eventi. Differenze effettive
soltanto: versioni ed eventi non cambiano per un salvataggio senza differenze.
Dopo commit: cards.changed pubblico vuoto e privato al proprietario con solo
pilot_id, senza carte o notifiche regalo/tasto S.

### Lock condiviso e avvio con mazzi da 15

services/sqlite_write_lock.py e' condiviso da salvataggio admin, move_card e
create_race prima delle letture autorevoli. Invalida identita' ORM precedenti e
rifiuta modifiche pendenti; promuove una transazione nativa gia' aperta tramite
UPDATE senza righe, senza cambiare carte/versioni. Il retry preesistente di
move_card resta limitato a StaleDataError; admin e avvio non ritentano i lock.

create_race richiede esattamente 15 copie nel mazzo da gioco di tutti gli
iscritti, inclusi i nascosti, sotto lo stesso lock. Non 15 nomi o il totale degli
inventari; nessun nuovo minimo di iscritti. race_deck_snapshot.py riusa il
dominio race_deck_readiness.py. Mancanza mazzo o JSON corrotto non sono sanati.
Tra le gare un mazzo puo' restare incompleto, anche dopo un salvataggio admin.

Rifiuto di avvio: nessuna nuova gara o race.started, rollback e 409 con nomi e
conteggi dei non pronti, senza carte. BUSY/LOCKED diventano RaceStartConflictError
e 409; altri errori SQL non sono mascherati. Restano blocchi di chiusura e
gara/revisione non confermata; gestione precedente delle revisioni scadute invariata.

### UI, richiesta e riepilogo effettivo

Nelle impostazioni campionato l'admin apre Piloti, vede nome/username e un
pulsante Carte accessibile. Cinque sezioni apribili con immagini e quantita':
mazzo N/15 per copie, due inventari distinti e due pool. Su mobile le aree
restano in sequenza. Modal e CardTile riusati, senza nuovo scaffold o risorse.

Il piano costruisce versions dalla baseline, anche per contenitori non toccati,
e ricalcola la sequenza senza fidarsi di un'anteprima alterata. Percorsi entro
255 code point, identita' nomi coerente con strip().casefold() del backend.
Nessun arrotondamento di ID/version e nessuna destinazione/copertura di copie
arbitraria nella richiesta. Tutti gli output sono indipendenti dalla sessione.

Salva in fondo a destra apre un modal solo testuale con pilota, username, nome
carta, quantita', sorgente/destinazione e nuovo conteggio del mazzo. Il riepilogo
accorpa copie e compensa i versi opposti inventario/pool della stessa carta,
senza inventare un verso inverso verso il mazzo. Non cambia il registro PUT:
il server riceve i clic originali validati in ordine. Nessuna proposta di PUT
quando non restano variazioni effettive. Annulla, X, Escape e sfondo non inviano
e conservano la bozza. Solo Conferma e salva consuma una proposta una volta.

Durante conferme e operazioni sono protetti clic, ripristino, ritorno, chiusura
ordinaria e navigazione. Successo: nuova sessione da snapshot PUT e versioni
server. Errori conservano la bozza; 422 consente azioni manuali, altri errori
bloccano nuovi invii fino a rilettura. Esito di rete o risposta inutilizzabile
non provano un rollback. Rileggi dal server e' esplicito: con bozza pendente
richiede conferma e la sostituisce soltanto dopo risposta utilizzabile.
Ripristina bozza e' locale e conserva i blocchi, non equivale a una rilettura.
Il client controlla contesto e la creazione della sessione controlla carte:
non e' una validazione runtime completa di ogni campo del DTO.

### Live e lifecycle

Il pannello usa eventClient condiviso e riletture REST autorizzate tramite il
coordinatore createRefreshCoalescer. Nessun secondo EventSource, polling o
autosalvataggio. I segnali non trasferiscono carte e non autorizzano scritture.
Eventi pertinenti di carte, iscrizioni, gara/revisione, resync e riapertura del
trasporto invalidano il contesto; gli altri campionati sono filtrati. Lo stato
della connessione non viene presentato come prova della freschezza dei dati.

Riletture accorpate e risultati obsoleti scartati. Una bozza non viene
sovrascritta: aggiornamenti incompatibili la bloccano conservando i dati.
Le conferme aperte sono distinte dalle richieste HTTP effettivamente in corso:
un evento puo' invalidare la proposta prima dell'invio; durante PUT/GET viene
rinviato, evitando di scartare il successo del proprio salvataggio. Una GET
live puo' seguire un evento pendente dopo il PUT: non e' un retry della scrittura.
Solo l'accettazione di uno snapshot server utilizzabile libera il blocco delle
riletture, non un reset locale o un cambio di stato del trasporto.

Cambio utente/ruolo, campionato, pilota o smontaggio invalidano il contesto;
risposte e callback tardive non ripopolano un contesto successivo. I cleanup
rimuovono i soli listener propri, senza chiudere lo stream condiviso. Una
chiusura forzata del browser non annulla una scrittura gia' inviata.

### Esiti finali verificati e collaudo dell'autore

Codice candidato: 2366d1de37cf1cf638b45c55313a3e31601eebff. CI 40026443509
riuscita per Frontend (check, lint, test, build), job 120664599995, Backend
(pytest), job 120664600371, Migrazioni (database di test), job 120664600375,
e Documenti fase 16 dopo backend, job 120665715224. Non sono nuove esecuzioni
locali. I conteggi complessivi di test e warning non sono stati letti dai log.

Dopo il via libera e la checklist in conversazione sul candidato 2366d1d,
il 2026-10-23 alle 23:59 CEST l'autore riferisce: «sembra funzionare tutto».
E' un riscontro manuale complessivamente positivo, non un verbale con esito
per ogni caso. Non sono stati forniti browser/dispositivo, log o risultati
individuali; non si marca automaticamente ogni voce OK. Non e' un collaudo
browser eseguito dall'assistente ne' prova di tutte le condizioni concorrenti.

Restano non attestati singolarmente i casi avanzati della checklist: doppio
invio, rete interrotta/esito incerto, conflitti tra sessioni, risposte tardive,
permessi e scadenza durante rete, rollback/concorrenza reale e privacy dei
payload. Le coperture automatiche e il riscontro qualitativo non vanno confusi.

### Tracciabilita' delle verifiche precedenti

Storico: dominio 934333c; sessione eedd729; chiusura modal d9ee662; UI c950510;
trasporto PUT 549e83e/f95c915; piano 024d47a/ad377d4; salvataggio 9769dd5/7d449cb;
adattatore eventi ecbf684/e725ba4; riletture 914ee47; collegamento live
fbcbd89/dc06e29; rimozione import 78661d8; prefer-const nei test 283c0ac;
riepilogo effettivo e posizione Salva 6d1b7cd/2366d1d. I controlli finali
sopra sostituiscono come stato corrente le letture incrementali in coda.

Il precedente riepilogo dell'autore era 748 passed, 14 warnings e 14 subtests
passed prima della pulizia 4514348; 27 asserzioni snapshot conservate tramite
AST. La regressione 72 failed/676 passed, poi un fallimento, era stata corretta
senza saltare test o allentare il dominio. Non sono i conteggi della CI finale.
Dieci casi di readiness includevano lock simulato, non tutta la concorrenza reale.

Identita' Unicode 15.0 verificata con confronto Node/Python su 1.112.064 scalari
e nove casi composti, senza NFC/rimozione accenti; non era type-check. Controlli
Node senza tipi: dodici scenari politica modal, venticinque adattatore eventi
e nove coordinatore riletture; non equivalgono a Vitest o browser. Sette test
Python della trasformazione documentale su fixture temporanee erano riusciti,
non il workflow GitHub completo. Le esecuzioni npm locali non sono inventate.

### Riallineamento documentale e consegna

Il titolo stabile e' stato ripristinato in f8a94e4; la tabella PROJECT_STATUS
deriva dalla riga Stato sintetico fase 16, senza stato hardcoded su vecchi commit.
Il pin CI aggiornato usa il blob 6858f05d89072cca488efeeb46166a2770383545 del
workflow approvato. Restano controlli su titolo, stato unico e marcatori anche
invertiti/adiacenti, protezioni di ramo e percorsi e nessun force-push.

Questo commit aggiorna soltanto i documenti sorgente e dedicati, dopo codice e
verifiche come richiesto dall'autore. La propagazione ai dieci documenti generali
va verificata dopo la pubblicazione, senza attendere nuovi test applicativi
per i soli docs. Il successo del job documentale sul codice precedente non
dimostra gia' propagato questo nuovo testo. Nessun merge, rilascio o ZIP finale
creato implicitamente; la PR resta in bozza.

Deck.cards resta TEXT con JSON name/path/copies e percorsi relativi ai media,
come confermato il 2026-10-22. Nessuna conversione a path/value o /images/cards,
migrazione, dipendenza, modifica di setup/avvio o accesso al database reale
da parte dell'assistente. Perimetro funzionale fase 16 distinto dal resto
delle istruzioni generali del progetto e da una consegna ZIP complessiva.

Test mirati superati dal workflow prima di questo riallineamento; CI completa separata.
<!-- phase16-admin-save:end -->

<!-- production-lan-current:start -->
## Produzione Wi-Fi/LAN - aggiornamento corrente del 24 ottobre 2026

Per la produzione prevale questa sezione sulle indicazioni storiche relative al solo loopback o al tunnel. Funzionalita sul ramo production-lan, PR #16 in bozza, senza merge in main.

Dalla radice: python heat.py production, oppure voce 7 del menu. Senza URL esplicito seleziona l IPv4 privato del PC e mostra l indirizzo da usare anche sugli altri dispositivi della LAN. Nessun tunnel o client aggiuntivo richiesto. --public-url resta facoltativo per un origine esplicita, incluso il solo loopback.

Gateway sul solo IPv4 scelto:5173, backend su 127.0.0.1:8000 con un worker. API, immagini e SSE passano dal gateway; controlli Host/Origin mantenuti. HTTP solo su rete fidata: traffico non cifrato. Nessuna modifica automatica a firewall o router. PC acceso e dispositivi reciprocamente raggiungibili necessari.

Production non installa dipendenze, non crea DB e non applica migrazioni: verifica soltanto le revisioni in lettura. Il comportamento storico di setup/start/migrate resta invariato. Nessuna modifica a schema, dati reali, formato carte, risorse, dipendenze o lockfile.

Verifica osservata: Production runtime checks 40047553032, job runtime 120733397223, success sul codice formattato 09a9aa594bd75650fe0af0556b67b64f2c0dcc15. Include test launcher/LAN/gateway, tipi, frontend, build, smoke test e lint. Non e una nuova attestazione di tutti i job della CI generale, ne un collaudo Wi-Fi/browser. Conteggi e warning non letti dai log. Nessun nuovo test locale per questo riallineamento; nessun merge o ZIP finale implicito.

Guida operativa e limiti: [Produzione Wi-Fi/LAN](PRODUCTION_LAN.md).
<!-- production-lan-current:end -->

<!-- account-password-current:start -->
## Impostazioni account e cambio password - 24 ottobre 2026

Su main: clic sul proprio nome apre Impostazioni account. Password attuale e doppio inserimento della nuova; nuova password di 8-128 caratteri, validata anche sul server. La sessione corrente resta attiva con token e scadenza invariati; le altre sessioni dello stesso account vengono revocate. Hash e revoche sono nella stessa transazione con rollback su errore. Gli altri account non cambiano.

Endpoint POST /api/auth/change-password, autenticato, successo 204. Nessuna migrazione o dipendenza nuova. Nessuna modifica al DB reale eseguita dall assistente. Durante l invio niente doppio invio o chiusura ordinaria; campi svuotati dopo la richiesta e alla chiusura. Errori di rete: esito incerto e nessun retry automatico. SSE riusa il controllo periodico delle sessioni.

Riallineamento dopo pytest backend, tipi, lint, test frontend e build riusciti nel runner: run 40114589745, checkout 97653418434af55ff904d36ab75d80fb0e8fe365, formattazione circoscritta applicata prima delle verifiche. Nessun conteggio inventato, test locale o collaudo browser attestato.

Dettagli, limiti e prove: [Impostazioni account](ACCOUNT_SETTINGS.md).
<!-- account-password-current:end -->

<!-- account-password-ui-current:start -->
## Aggiornamento grafico impostazioni e login - 24 ottobre 2026

Nel modal Impostazioni account la sezione Cambio password e a scomparsa e inizialmente chiusa a ogni nuova apertura. La chiusura della sezione svuota i campi. In login e nei tre campi del cambio password e disponibile Mostra/Nascondi, indipendente per ogni campo e nascosto inizialmente. La visibilita non viene salvata; il componente dedicato password-input.svelte e riusato nei due contesti. Durante le richieste i controlli relativi sono disabilitati. Backend, API, database e comportamento di revoca delle altre sessioni restano invariati.

Il fallimento Prettier su account-settings.svelte e stato affrontato applicando il formatter del lockfile solo a quel componente. Prima di questo riallineamento sono riusciti sul runner: npm run check, npm run lint, npm test e npm run build. Run 40124870171, checkout fc8d1f301a9350c555e4c4f2ab0d8ff6a7bb89ae, con componente formattato prima delle verifiche. Il successivo commit pubblica quello stile e questi documenti; non e una nuova esecuzione della CI sul commit risultante. Nessun test locale o conteggio inventato.

I test password-ui.spec.ts presenti nel candidato sono controlli di rendering server, non prove interattive di clic, tastiera o browser. Restano da verificare manualmente espansione/richiusura, reset alla riapertura e Mostra/Nascondi nei quattro campi. Nessuna migrazione, nuova dipendenza, modifica al lockfile o operazione sul DB reale.
<!-- account-password-ui-current:end -->
