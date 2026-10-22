# Guida di lavoro — Heat

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

Data: 2026-10-22. Ramo phase-16-admin-pilot-inventory, PR 15 in bozza.
Questo incremento supera il precedente limite delle sole letture. Frontend e
controllo di avvio gara da 15 copie restano da completare, senza merge implicito.

### Contratto di scrittura

PUT /api/admin/championships/{championship_id}/pilots/{pilot_id}/cards riceve
versions e transfers. versions contiene tutti i cinque contenitori: id/version
interi positivi, oppure null per le sole pool assenti. Ogni trasferimento ha solo
source e path; una copia per elemento, destinazione imposta dal dominio. Campi
extra, sostituzioni arbitrarie delle carte e destinazioni client sono rifiutati.

Ruolo, pilota visibile/iscritto, chiusura e gara/revisione non confermata vengono
ricontrollati nella transazione. Confronto id e versione anche dei contenitori
non toccati; pool assenti non sono create e non possono ricevere o fornire copie.
Conflitto: 409 e nessun retry automatico. Movimento non applicabile: 422.

SQLite acquisisce il lock prima delle letture autorevoli e scade le identita'
SQLAlchemy gia' caricate. Una transazione nativa esistente e' promossa con un
UPDATE senza righe; se lo snapshot non puo' essere promosso si rifiuta la scrittura.
Un solo commit per Deck ed eventi, rollback anche per errore nel registro eventi.
Nessun nuovo schema DB, migrazione, dipendenza o accesso al database reale.

Solo le differenze effettive aggiornano le versioni. Nessuna differenza significa
nessun evento. Il mazzo puo' restare incompleto: nessuna aggiunta pool/mazzo o
sponsor/mazzo, nessuna doppia sottrazione. Risposta con snapshot e versioni nuove.
Dopo variazioni sono accodati cards.changed pubblico vuoto e privato al proprietario
con solo pilot_id: nessun dettaglio carte, regalo o notifica tasto S inventata.

### Verifiche e limiti

Preparati 27 casi in backend/tests/test_admin_pilot_card_save.py: cinque direzioni,
versioni di tutti i contenitori, blocchi, ruoli, input non ammessi, pool assenti o
riassegnate, rollback tardivo/eventi, bozza senza differenze, segnali privi di carte
e due salvataggi concorrenti con sessioni distinte su un SQLite temporaneo.
Test HTTP non eseguiti localmente. Eseguiti invece controlli sintattici e una prova
SQLite isolata: UPDATE senza righe blocca il secondo writer, non incrementa
versioni e rollback libera il lock. Il conteggio dei test e' stato corretto dopo
un NameError del solo script di analisi; nessun risultato HTTP PASS inventato.

Il workflow esegue dominio, letture e salvataggi prima del riallineamento generale.
La CI completa resta da leggere separatamente. Non chiudere/riaprire la PR come
procedura abituale. Per commit solo documentali non attendere la CI applicativa.
Restano da integrare il controllo esatto di 15 all'avvio e il coordinamento con
move_card, interfaccia con conferma testuale e protezione bozza, SSE condiviso e
collaudo browser. Il backend non dimostra ancora queste parti. Il formato resta
TEXT con array name/path/copies e percorsi correnti relativi ai media.

### Riscontro CI e diagnosi sincronizzazione - 2026-10-22 20:15 CEST

La lettura della CI 39827070228 riporta successo per backend pytest, frontend
check/lint/test/build e migrazioni sul database di test. Non e' una nuova
esecuzione dei test in locale e non costituisce un collaudo browser.
Il commit fbc7789 aggiunge il collegamento documentale alla CI, ma al controllo
seguente non risultavano nuovi check o un commit documentale successivo.
La lettura della PR 15 esponeva ancora db94beb: i risultati del connettore non
consentono di distinguere sincronizzazione GitHub da dati non aggiornati.
Nessuna causa certa attribuita a token, eventi o configurazione senza prove.

Per la verifica si usa un aggiornamento reale di questo documento con
create_or_update_file (API Contents), anziche' push_files. Nessuna modifica a
workflow, codice o DB reale e nessuna chiusura/riapertura o merge della PR.
L'effettivo aggiornamento della testa PR e l'avvio dei nuovi controlli vanno
verificati dopo la scrittura: questa nota non dichiara gia' risolto il problema
ne' gia' riallineati i dieci documenti generali. Per il solo aggiornamento
documentale non attendere la CI applicativa.

### Preparazione del controllo delle 15 copie - 2026-10-22

Nuovo modulo puro backend/app/services/race_deck_readiness.py: conta le copie
nel solo mazzo da gioco, raccoglie tutti i piloti non pronti e rifiuta anche
il JSON non valido senza trasformarlo in un mazzo vuoto. Nessun dettaglio
delle carte nel riepilogo, nessuna modifica o completamento dei mazzi.
Tredici test in backend/tests/test_race_deck_readiness.py eseguiti con unittest
in ambiente isolato: 13/13 OK; cards.py verificato contro il blob
b329ece85fef6cc232ef322cb857108088ea5cf7. Parsing Python e git diff --check
riusciti. Nuova CI del repository ancora da leggere dopo la pubblicazione.

Questo incremento NON collega ancora il controllo a create_race, non cambia
API gare, lock, move_card o fixture esistenti e non attiva il blocco di avvio.
L'integrazione successiva deve leggere tutti gli iscritti nella transazione,
bloccare gara ed evento race.started in caso di mazzi non pronti, riportare
i conteggi ai gestori e coordinare avvio, salvataggi admin e movimenti giocatore.
Le fixture comuni lette avviano gare senza preparare 15 copie; la ricerca del
codice ha restituito risultati incompleti, non un censimento affidabile dei test.
Adeguare esplicitamente le fixture, senza autocompletamento nella produzione
o hook nascosti che rendano sempre pronti i mazzi durante i test.
Nessun workflow modificato: la pulizia proposta dopo il vecchio errore non e'
stata applicata, poiche' la CI e il riallineamento successivi erano riusciti.
La nota viene ripresa nei documenti generali dal riallineamento esistente.
Nessun nuovo schema DB, migrazione, dipendenza o accesso al database reale.

### Coordinamento scritture admin e giocatore - 2026-10-22

Nuovo helper services/sqlite_write_lock.py condiviso da admin_pilot_card_save
e pilot_deck.move_card: lock di scrittura prima delle letture e invalidazione
delle identita' ORM precedenti. Non accetta modifiche pendenti da scartare con
expire_all; nessuna carta o versione viene cambiata dall'UPDATE senza righe.
I movimenti del giocatore fanno rollback su errori di dominio e SQL. Restano
massimo 15 e blocchi gara/revisione; il retry preesistente resta limitato a
StaleDataError, mentre lock occupato restituisce conflitto senza retry automatico.
Il salvataggio admin mantiene un solo commit e nessun retry. Nessun nuovo evento.

Preparati solo cinque test importanti in test_sqlite_card_write_lock.py:
transazione nativa gia' aperta, rilascio su errore, rilettura di oggetti in cache,
protezione delle modifiche pendenti e due movimenti concorrenti su SQLite di
prova. Nessuna suite locale eseguita, come richiesto alle 21:49: solo controllo
sintattico Python; esecuzione e risultati dei test sono affidati alla CI.

create_race, API gare e fixture gare NON cambiano in questo incremento; la regola
di avvio con esattamente 15 copie non e' ancora attivata. Prossimo collegamento:
lock condiviso anche all'avvio, lettura di tutti gli iscritti, rifiuto atomico con
riepilogo e adeguamento esplicito delle fixture. Non usare autocompletamenti o
hook nascosti per aggirare i test di mazzi incompleti. Nessun workflow modificato,
nessuna migrazione, dipendenza o operazione sul DB reale. Riallineamento generale
tramite il processo documentale gia' esistente; niente attesa CI per soli docs.

Test mirati superati dal workflow prima di questo riallineamento; CI completa separata.
<!-- phase16-admin-save:end -->
