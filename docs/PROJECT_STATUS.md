# Stato del progetto — Heat

Ultimo aggiornamento: 2026-10-23

## Chiusura autorizzata della fase 15 - 2026-10-22

Alle 00:47 CEST l'autore autorizza il riallineamento dei documenti generali e
la chiusura della fase 15 senza riprendere i test manuali non praticabili.
Fase 15 completata e chiusa sul ramo phase-15-sse-sistemazione, con limiti di
collaudo accettati. Non significa PR 14 unita a main o messa in produzione.
Codice finale 1226172, CI ordinaria 39674942800 verde; lifecycle/canvas 8018d18,
CI 39658083388 verde. Sei casi manuali PASS (1/4/5/6/7/9), 2/3 non verificabili,
8/10 non eseguiti. Restano tali: non sono convertiti in PASS. Fix iscrizioni
confermato dall'autore alle 23:24 del 2026-10-21 con "funziona".
Nessun ulteriore collaudo di quei quattro casi e' richiesto per questa chiusura.
Restano fuori da questa accettazione produzione, vulnerabilita' npm,
backup/setup sicuro, configurazione online, nuove fasi e migrazioni reali.
Merge e gestione della PR richiedono una richiesta separata.
Dettagli e verifiche in PHASE_15.md, PHASE_15_BROWSER_CHECKLIST.md,
PHASE_15_ENROLLMENT_LIVE.md e PHASE_15_CLOSURE.md.

## Fasi

| Fase | Contenuto | Stato |
|---|---|---|
| 1-2 | Analisi, specifiche, schema database | Completate |
| 3 | Bootstrap frontend: SvelteKit minimal, TypeScript, npm, ESLint, Prettier, Vitest | Completata |
| 4 | Backend FastAPI, modelli SQLAlchemy, migrazioni Alembic, SQLite | Completata |
| 5 | Autenticazione: registrazione, login, logout, sessioni httpOnly, ruoli | Completata |
| 6 | Team, piloti, mazzi, inventario e immagini carte | Completata |
| 7.6 | Pool derivate e campionati | Completata |
| 7.6b | Cancellazione dei campionati chiusi | Completata |
| 7.7 | Gare, risultati e classifica live | Completata |
| 7.8 | Pulizia amministrativa e automatica di team e piloti nascosti | Completata |
| 7.9 | Classifica finale congelata dei campionati chiusi | Completata |
| 7.10 | Ruolo giudice e punti sponsor nei risultati | Completata |
| 8a | Frontend: login, registrazione, team, piloti, campionati, gare, classifica, utenti e ruoli | Completata |
| 8b | Backend: due pool di base (modifiche e sponsor), ricarica delle pool, seconda pool sul campionato | Completata |
| 8c | Frontend admin: pool con ricarica, creazione, chiusura e cancellazione dei campionati | Completata |
| 8d | Frontend: costruzione del mazzo da gioco dall'inventario (max 15 carte), blocco ottimistico sui mazzi | Completata |
| 8e | Frontend admin: pulizia di team e piloti nascosti | Completata |
| 9 | Ricerca piloti per nome e filtro per team, paginazione dell'elenco piloti | Completata |
| 10 | CI con GitHub Actions: test backend e controlli frontend a ogni pull request | Completata |
| 11 | Oro per gara, impostazioni generali e del campionato, popup propri, una sola gara in corso, assenti espliciti | Completata (pull request #4 unita a `main`) |
| 12 | Negozio e pacchetti di carte | Completata (pull request #5 unita a `main`, commit `6dd5619`) |
| 12a | Tabelle del Negozio, inventario sponsor del pilota e reset, servizio e script delle immagini | Completata |
| 12b | Template di pacchetto e di negozio, pacchetti del campionato, creazione del campionato con template | Completata |
| 12c | Estrazione, acquisto, storico e riepilogo inventario (backend) | Completata e approvata |
| 12d | Frontend giocatore: elenco `/shop`, negozio con ordinamento e ricerca, inventario, storico, apertura animata dei pacchetti, riepilogo finale con copie raggruppate | Completata (verifica a mano dell'autore) |
| 12e | Frontend admin: gestione negozio, template, pacchetti del campionato, storico completo di tutti i piloti dalle impostazioni del negozio | Completata (verifica a mano dell'autore) |
| 12f | Verifica complessiva e unione di `phase-12-shop` in `main` | Completata (CI verde sull'ultimo commit `24388ea`) |
| 13 | Carte sponsor in gara e amministrazione delle carte (decisioni in `PHASE_13_SPEC.md`); la pull request #9 raccoglie tutta la fase | Completata: pull request #9 unita in `main` il 2026-10-18 (merge `cdea876`) |
| 13a | Backend carte sponsor: registro delle carte giocate, stack da 5 annullamenti, uso e annullamento, restituzione alla pool alla chiusura | Completata nel ramo `phase-13a-card-plays` (pull request #9 in bozza, CI verde sul commit dei test `a087855`) |
| 13b | Backend: stato "in revisione" con revisore unico e scadenza di 15 minuti con conferma automatica, riepilogo, annullo anche di giocate consumate, bonus, rimozione di carte, riapertura dell'admin sull'ultima gara, tasto S, notifica di carta ottenuta | Completata nel ramo `phase-13a-card-plays` (CI verde, letta il 2026-10-13, sull'esecuzione partita subito dopo il commit dei test `55fbcea`: test backend, migrazioni e frontend). La pull request #11 (merge `f733886`, commit dei test `2f12768`) ha aggiunto test sulla scadenza della revisione e sul secondo giudice, su bonus e annullo |
| 13c-1 | Backend: intervallo di controllo delle notifiche di carta ottenuta (`card_poll_seconds`, da 1 a 10 secondi, predefinito 5, modificabile solo dall'admin) | Completata nel ramo `phase-13a-card-plays` (CI verde sul commit `e1de642`: test backend, migrazioni e frontend) |
| 13c | Frontend giocatore: sezioni per pilota, uso delle carte, Indietro, inventario in due sezioni, popup "Hai ottenuto una carta sponsor", controllo periodico delle notifiche con l'intervallo della 13c-1, campo dell'intervallo nelle impostazioni generali | Completata nel ramo `phase-13a-card-plays`: sezione per pilota, uso con conferma, "Annulla ultima" (il pulsante Indietro della specifica, collegato a `POST .../card-plays/undo`), popup, controllo periodico con l'intervallo letto da `GET /api/admin/card-poll` (predefinito 5 secondi se la lettura fallisce), form dell'intervallo nelle impostazioni generali dei campionati (commit da `1ac7d77` a `eed811a`, che nei messaggi portano per errore il prefisso "13e": appartengono alla 13c), inventario in due sezioni "Modifiche" e "Sponsor" (commit `f2235ed`), sezione già aperta quando il giocatore ha un solo pilota iscritto (proprietà `startOpen` di `PilotCardPlays`, letta in `onMount` per il solo valore iniziale, aggiunta il 2026-10-18) e riepilogo con immagini del mazzo da gioco in uso nella sezione di ogni pilota (aggiunto il 2026-10-18: `pilot-card-plays.svelte` con `lib/pilot-deck-api.ts` e il suo test). Verifica nel browser del 2026-10-18 (assistente, Chromium headless su un'installazione locale con dati di prova): sezione aperta con un solo pilota iscritto, riepilogo del mazzo con immagini e copie in sola lettura. Restano da verificare a mano il campo dell'intervallo e le due sezioni dell'inventario del dettaglio pilota |
| 13d | Frontend giudice e admin: elenco piloti con tasto S, revisione nella pagina della gara con immagini, correzioni | Completata nel ramo `phase-13a-card-plays`: tasto S nella scheda "Piloti iscritti" (commit `b1e202a` e `605a51b`, CI letta il 2026-10-12: i tre controlli sono verdi) e revisione nella pagina della gara (`race-review-panel.svelte`: riepilogo con immagini, annullo, bonus, rimozione, conferma, rinuncia e, per l'admin, riapertura), confermata dall'autore il 2026-10-13 ("Avanzamento della 13b" in `PHASE_13_SPEC.md`); il backend ammette giudice e admin su qualsiasi pilota iscritto per il tasto S (commit `0f9c9b1`, CI verde) |
| 13d+ | Riallineamento di tutti i documenti (richiesto dall'autore) | In corso: `PROJECT_SPEC.md` (commit `bc0fbfb`), `PHASE_13_SPEC.md` (commit `9405c97`), `SHOP_DESIGN.md` (commit `c7fbe7f`) e questo file riallineati; riallineamento alla 13e e alla 13f di questo file fatto il 2026-10-13 e il 2026-10-14, mentre il 2026-10-18 `PHASE_13_SPEC.md` (sezione "Avanzamento della 13f"), `PROJECT_NOTES.md` e `README.md` sono stati riallineati alla 13f e `DATABASE.md` riporta che la 13e e la 13f non aggiungono migrazioni (verificato nello storico di `backend/alembic/versions`: l'ultimo commit che le tocca è `57b4637` del 2026-10-12, prima della 13e); resta da rileggere `PROJECT_SPEC.md` dopo `bc0fbfb`; `DATABASE.md` (commit `12b9b09` e `6ed3d84`), `SETUP.md` e `SCRIPTS.md` (commit `f3bd2b4`) sono stati creati il 2026-10-13 in `docs/` (vedi "Documenti"); `DATABASE.md` è stato scritto dai modelli SQLAlchemy, mentre `SETUP.md` e `SCRIPTS.md` da `heat.py` e `config.py`, non riletti dopo la scrittura |
| 13e | Backend amministrazione carte: caricamento, conversione, eliminazione, origine "caricata" | Completata nel ramo `phase-13a-card-plays` (commit da `358297a` a `14557ab`, tutti del 2026-10-13: servizio di caricamento delle carte, eliminazione delle carte caricate con pulizia dei file orfani, `delete_championship` che cancella i file delle carte rimasti senza uso, rotte admin per caricare ed eliminare le carte, test di caricamento, eliminazione e pulizia dei file; l'autore ha riferito che tutto funziona; CI verde sul commit `9f3b517`, letta il 2026-10-18, esecuzione 38480483060: Backend pytest, Migrazioni e Frontend con successo) |
| 13f | Frontend: ritaglio con zoom, nome e quantità, nomi in arancione, tasti di esclusione nelle pool personalizzate | Completata nel ramo `phase-13a-card-plays`: ritaglio con zoom, modulo di caricamento (nome e copie), elenco delle carte della pool di base con i nomi in arancione per le carte caricate a mano e tasto "Elimina", integrazione nella pagina admin delle pool (commit `254b015`, `e5cf313`, `062629f`, `1391a70`, `8dbd7c2`) e i due tasti di esclusione nella creazione delle pool personalizzate (aggiunti il 2026-10-18: `lib/pool-exclusion.ts` con il suo test, `isBaseCard` in `lib/card-origin.ts`, tasti "Escludi tutte le carte caricate" ed "Escludi tutte le carte di base" sopra l'elenco in `routes/admin/pools/+page.svelte`; azzera le copie scelte del gruppo nel solo modulo, senza toccare il database). Controlli eseguiti in locale il 2026-10-18: `npm run check` (0 errori, resta il solo warning preesistente del canvas in `card-crop-editor.svelte`), `npm run lint`, `npm test` (110 test passati su 110: la base era 101, i 9 nuovi sono 7 di `pool-exclusion.spec.ts` e 2 di `pilot-deck-api.spec.ts`) e `npm run build`; CI verde sul commit `5ed659e`, letta il 2026-10-18 (esecuzione [39126355821](https://github.com/ale3000ale/Heat-pedal-to-the-roguelike/actions/runs/39126355821): Backend pytest, Migrazioni e Frontend con successo) |
| 13g | Documenti e test finali, unione in `main` | Completata: tasti di esclusione e riepilogo del mazzo aggiunti il 2026-10-18 (commit `5ed659e`) con test, verifica nel browser e documenti riallineati; CI verde su `5ed659e` (esecuzione 39126355821); pull request #9 uscita dalla bozza e unita in `main` il 2026-10-18 (merge `cdea876`, testa precedente `68dd4d7`) |
| 14 | Sistemazione generale, modifiche di vivibilità e miglioramenti | Unita a main con PR #13 il 2026-10-19; stato post-merge in PHASE_14_POST_MERGE.md |
| 15 | SSE, aggiornamenti live e correzioni lifecycle/canvas | Completata e unita a main con PR 14, merge 6dcdc83; limiti manuali accettati |
| 16 | Gestione admin carte piloti e avvio con mazzi da 15 | Perimetro funzionale implementato, incluso live e riepilogo effettivo; CI 40026443509 riuscita su 2366d1d; riscontro manuale complessivamente positivo dell'autore, senza protocollo caso per caso; riallineamento finale documentale; nessun merge autorizzato. |

## Come leggere la cronologia

Le righe delle sottofasi 13 e i dettagli tecnici seguenti conservano i riscontri
dell'epoca, inclusi limiti allora aperti. La riga complessiva 13 ne registra il
merge; la fase 15 e l'appendice corrente di PROJECT_SPEC.md prevalgono per SSE,
timer, aggiornamenti UI e chiusura del lavoro. Non rimettere in corso la fase
15 sulla base di una descrizione storica del polling o di un vecchio warning.

## Backend

- FastAPI, SQLAlchemy 2.0, Alembic e SQLite in `backend/`.
- Autenticazione con password hashate e cookie di sessione httpOnly; ruoli `admin`, `judge` e `player`; primo admin creato con setup.
- Team e piloti con nomi unici senza distinguere maiuscole, rinomina ed eliminazione logica. Un pilota può non avere un team, ma deve averne uno per iscriversi a un campionato.
- Ogni pilota possiede tre mazzi: inventario delle modifiche, inventario sponsor (vuoto alla creazione) e mazzo da gioco; blocco ottimistico con numero di versione (409 in caso di conflitto).
- Dettaglio pilota (13c): `PilotDetail` (`schemas/pilot.py`) include il campo `sponsor_inventory`, riempito da `_detail()` in `api/pilots.py` con `sponsor_cards()` di `services/pilots.py`; compare anche nelle risposte di `deck/add` e `deck/remove`. `pilot_decks()` e `move_card` non sono cambiati: le carte sponsor non entrano nel mazzo da gioco (la richiesta dà 404).
- Elenco piloti paginato (`limit`/`offset`), con ricerca per nome, filtro per team e campionato attivo.
- Gestione e validazione delle carte JSON, preparazione e ridimensionamento delle immagini; rinomina delle carte nelle pool.
- Immagini dei pacchetti (`services/pack_images.py`): png, jpg/jpeg e webp fino a 5 MB, conversione in WebP nella scatola 560x870 px, elenco (predefinita in `media/pack/defaultIllustration`, caricamenti in `media/pack/illustration`).
- Script `python -m app.scripts.resize_cards`: porta in WebP le immagini di `media/cards` e `media/pack`; idempotente, non cancella gli originali, con `--dry-run`.
- Pool di base (modifiche `default` e sponsor `sponsor`), pool derivate create dall'admin, due copie di pool per ogni campionato.
- Ricarica delle pool di base: aggiunge le carte nuove e toglie quelle il cui file non esiste più (se la cartella è vuota o manca non toglie nulla). Anteprima `GET /api/pools/base/{kind}/reload/preview` (non scrive, indica le carte nella copia di pool di un campionato attivo); `POST /api/pools/base/{kind}/reload` applica. Le copie dei campionati già creati non cambiano.
- Iscrizione ai campionati con reset di inventario, inventario sponsor, mazzo da gioco, gold, sponsor e punti; il reset si ripete alla chiusura del campionato.
- Gare numerate automaticamente; una sola gara in corso per campionato. Chiusura con ordine di arrivo, punti sponsor e assenti espliciti; correzione dei risultati solo per l'admin; punti 9-6-4-3-2-1, poi 0. Le gare non si eliminano a mano: spariscono solo con la cancellazione del campionato chiuso.
- Oro per gara: regole per campionato (base più modificatore per posizione 1-6 e per "altre"), copiate dalle impostazioni generali alla creazione e assegnate a tutti gli iscritti alla prima chiusura di ogni gara.
- Classifica live per i campionati attivi, congelata per quelli chiusi; cancellazione di un campionato chiuso con tutti i suoi dati.
- Admin: gestione degli elementi nascosti, eliminazione definitiva manuale e pulizia automatica dopo 365 giorni.
- Negozio, parte admin (12b): template di pacchetto e di negozio, rotte delle immagini, pacchetti del campionato, creazione del campionato con template. Un pacchetto senza valuta e senza costo vale 10 oro; con valuta sponsor e costo mancante vale 2 sponsor.
- Negozio, estrazione e acquisto (12c-1): `services/shop_draw.py` (una carta alla volta, probabilità per copia ricalcolata dopo ogni estrazione, filtro per nome, "terminato") e `services/shop_purchase.py` (controlli, saldo, estrazione, pool, inventari e storico in un solo commit; tetto di 100 copie per carta con errore 409). Serializzazione con lock di processo più `BEGIN IMMEDIATE` su SQLite (`_lock_database`); con altri database il blocco non è attivo.
- Negozio, accesso e vista (`services/shop_view.py`): il giocatore entra con un proprio pilota iscritto e solo a campionato attivo; l'admin entra sempre (sola lettura senza pilota o a campionato chiuso, come un giocatore con un pilota iscritto). Con una gara in corso gli acquisti sono bloccati; l'autore ha confermato il 2026-10-13 che il blocco vale anche con la gara in revisione.
- Negozio, elenco dei negozi dell'utente: `GET /api/me/shops` (`api/shop_me.py`, `services/shop_list.py`).
- Negozio, storico e inventario (12c-2): `services/shop_history.py` e `services/shop_inventory.py`. Il giocatore non vede gli acquisti di un pilota che ha eliminato; l'admin sì.
- Carte sponsor giocate (13a): tabella `card_play` (modello `CardPlay`, migrazione `c3e7a1d5b9f2`) con gara, pilota, nome e percorso della carta, stato (`giocata`, `annullata`, `consumata`) e data della giocata (`played_at`); non esiste una data di annullamento. `services/card_play.py` gestisce giocata, annullamento e stato; le copie disponibili sono quelle dell'inventario sponsor meno le giocate attive della gara in corso, e l'inventario non cambia durante la gara. Gli annullamenti consecutivi sono le giocate annullate dopo l'ultima ancora attiva (massimo 5, si azzera giocando una nuova carta); non c'è una colonna dedicata. Il pilota deve essere del giocatore, non eliminato e iscritto; serve una gara in corso in un campionato attivo. Le righe del registro non si cancellano mai durante il gioco: l'eliminazione logica del pilota (`deleted_at`) le lascia, e solo l'eliminazione definitiva del pilota (`_purge_pilot` in `services/cleanup.py`) le rimuove. Le gare non si eliminano a mano, quindi nessuna riga segue la sorte di una gara.
- Carte sponsor, chiusura della gara (13a): `services/card_play_close.py` (`consume_plays`), richiamato da `set_results` in `services/races.py` solo alla prima chiusura della gara e nella stessa transazione. Le giocate attive passano a `consumata`, escono dall'inventario sponsor del pilota e tornano nella pool sponsor del campionato; le annullate restano in inventario. Le correzioni dell'admin non toccano le carte. Senza pool sponsor sul campionato le carte escono dall'inventario ma non tornano in nessuna pool; se una carta giocata non è più in inventario la chiusura si ferma con un errore.
- Stato "in revisione" (13b): colonne `Race.review_started_at` (migrazione `d4f8b2e6a0c3`) e `Race.review_started_by_user_id` (migrazione `a9c3e7b1d5f0`), con `services/race_review.py` e `api/race_review.py`. La revisione si avvia con "termina gara" e chi la avvia diventa il revisore unico: ogni altro utente, giudici e admin compresi, riceve 409. Durante la revisione giocata, annullamento del giocatore e tasto S sono bloccati (409). La scadenza è di 15 minuti dall'inizio: `settle_expired_reviews` conferma la revisione così com'è alla prima richiesta successiva (lettura dello stato o creazione di una nuova gara), senza processi in background. Il revisore può rinunciare (le giocate non cambiano) o confermare; con la revisione scaduta o mai aperta può confermare solo l'admin. L'admin può riaprire con `reopen_review` la revisione confermata dell'ultima gara del campionato (`is_last_race`): diventa il revisore con altri 15 minuti. Per chi non è admin la riapertura dà 403; per gara non ultima o revisione non confermata dà 409.
- Tasto S e notifica (13b): tabella `card_gift` (modello `CardGift`, migrazione `e7a3c9d1f5b2`) con gara, pilota, nome e percorso della carta, `created_at` e `seen_at` (vuoto finché il giocatore non ha visto la notifica). `services/card_gift.py` (`draw_gift`) estrae una carta dalla pool sponsor del campionato con probabilità proporzionale alle copie, ne toglie una dalla pool (riga rimossa a zero), la aggiunge all'inventario sponsor del pilota (riga nuova se mancava) e crea la notifica, in un solo commit. Il pilota deve essere iscritto: admin e giudice agiscono su qualsiasi pilota non eliminato (`_load_gift_pilot` e `_authorize_gift`), il giocatore solo sui propri (`get_own_pilot`); la notifica va al proprietario del pilota. Serve una gara in corso non in revisione e almeno una copia in pool (409 se la pool è vuota o assente). La carta regalata è subito giocabile nella stessa gara. `list_unseen_gifts` e `mark_gifts_seen` leggono e chiudono le notifiche non viste del pilota nel campionato.
- Riepilogo e correzioni del revisore (13b): `services/card_judge.py`, con le rotte in `api/race_review.py`. Tutte le azioni passano da `_reviewed_race` (revisione attiva aperta dall'utente che agisce, altrimenti rifiuto). `get_card_summary` elenca le giocate di tutti i piloti della gara, raggruppate per pilota. `cancel_play` porta una giocata a `annullata` (resta nel registro), anche già consumata: in quel caso la carta torna al pilota dalla pool sponsor, solo se la pool ha ancora una copia uguale, altrimenti 409. `grant_bonus` sposta una copia dalla pool all'inventario del pilota, senza creare notifiche; 409 se la carta non è in pool o se il campionato è chiuso. `remove_card` sposta una copia dall'inventario sponsor del pilota alla pool sponsor del campionato, in un solo commit: 409 se il campionato non ha una pool sponsor, se la carta non è nell'inventario o se tutte le copie sono impegnate in giocate attive; 404 per pilota inesistente o eliminato, 403 per pilota non iscritto. `_without_one_copy` (in `services/card_gift.py`) confronta le carte per identità, quindi `remove_card` le passa lo stesso oggetto della lista dell'inventario.
- Intervallo di controllo delle notifiche (13c-1): colonna `card_poll_seconds` su `championship_defaults` (migrazione `f8a4d2c6e0b1`, valore 5 per la riga esistente). Sta solo sul modello `ChampionshipDefaults` e non nel mixin dell'oro, quindi non viene copiata nei campionati e vale per tutti, anche per quelli già creati. `get_card_poll_seconds` e `set_card_poll_seconds` in `services/gold.py`: limiti da 1 a 10, predefinito 5, un valore fuori dai limiti dà `ValueError` e non scrive nulla. Schema `schemas/card_poll.py` (campo `seconds` tra 1 e 10, altrimenti 422). Rotte in `api/admin.py`: `GET /api/admin/card-poll` (ogni utente collegato, 401 se anonimo) e `PUT /api/admin/card-poll` (solo admin, 403 agli altri).
- Amministrazione delle carte (13e): i commit `358297a`, `cb934d8`, `3a79199`, `e26801e` e `14557ab` (2026-10-13) aggiungono il servizio di caricamento delle carte, l'eliminazione delle carte caricate con la pulizia dei file orfani, la cancellazione dei file delle carte rimasti senza uso in `delete_championship` e le rotte admin per caricare ed eliminare le carte, con i test relativi. I nomi dei file, delle funzioni e delle rotte, i limiti di formato e dimensione e l'eventuale migrazione per l'origine "caricata" non sono stati riletti per questo documento: vanno presi dal codice e descritti qui e in `PHASE_13_SPEC.md` alla prossima lettura.

## Frontend

- Pagine: login, registrazione, home, team, dettaglio pilota, campionati, dettaglio campionato, dettaglio gara, elenco `/shop`, negozio del campionato, storico, pannello admin (utenti e ruoli, pool, campionati, nascosti, impostazioni generali, gestione negozio).
- Dettaglio pilota (13c): il riquadro "Inventario" ha due sezioni a scomparsa, chiuse all'apertura della pagina: "Modifiche (N)" e "Sponsor (N)" (`routes/pilots/[id]/+page.svelte`, dati da `sponsor_inventory` in `lib/types.ts`). Le carte modifica si cliccano per metterle nel mazzo da gioco; le carte sponsor sono in sola lettura.
- Elenco `/shop`: un riquadro per campionato con i propri piloti e il saldo (oro e punti sponsor); un clic apre il negozio con quel pilota.
- Negozio (12d): in alto a destra il pilota con oro e punti sponsor; pulsanti Inventario (popup), Storico (pagina separata), scelta del pilota, impostazioni (admin). Aree modifiche (oro) e sponsor (punti sponsor), con ricerca per nome e ordinamento (`lib/shop-sort.ts`, test in `shop-sort.spec.ts`); le scelte non vengono salvate.
- Apertura dei pacchetti (`components/pack-reveal.svelte`, fasi in `lib/pack-reveal-phases.ts`): busta con l'immagine del pacchetto come texture, strappo della striscia, busta tagliata che scorre in basso, poi le carte una alla volta (un tocco, Invio o Spazio mostra la seguente). Dopo l'ultima, il tocco successivo apre il riepilogo: griglia con le carte ottenute, ciascuna con immagine ed etichetta "Modifica" o "Sponsor"; le copie uguali sono raggruppate con "x N" (`lib/pack-summary.ts`, funzione `groupByCard`, test in `pack-summary.spec.ts`), e il testo "Hai ottenuto N carte" conta tutte le estrazioni. "Salta" porta al riepilogo da qualsiasi fase.
- Chiusura della finestra di apertura: fino al riepilogo solo con la X; il tasto Esc e il clic fuori non chiudono (`modal.svelte` li gestisce con `closeOnOutside`, collegato a `done` di `pack-reveal.svelte`); dal riepilogo si chiude in ogni modo. Con il movimento ridotto del sistema si parte dalle carte.
- Admin del negozio (12e): pagina "Gestione negozio" (template di pacchetto e di negozio), scelta del template nella creazione del campionato, ingranaggio con pacchetti, pool completa e storico. Il pulsante "Storico" delle impostazioni, anche aperte dal negozio (`shopOnly`), mostra la cronologia completa di tutti i piloti (`championship-history-panel.svelte`, `fetchAllHistory`).
- Popup propri al posto di `dialog` e `confirm` nativi; impostazioni del campionato in un popup aperto dall'ingranaggio (solo admin).
- Modulo dei pacchetti: costo iniziale 10; cambiando valuta passa a 2 sponsor (e torna a 10 oro) solo se il costo non è stato modificato a mano.
- Pagina admin delle pool: «Ricarica» chiede l'anteprima e, se vanno tolte carte, apre un popup di conferma con i nomi e l'avviso "in uso in un campionato attivo".
- Dettaglio campionato: gare dalla più recente, con stato "in corso" o "terminata"; dettaglio gara con classifica, "Da assegnare" e "Non partecipano"; popup "Esci / Rimani" se si lascia una gara in corso non salvata.
- Carte sponsor in gara, giocatore (13c): nel dettaglio del campionato il blocco "Le tue carte sponsor" compare solo con una gara in corso, campionato attivo e almeno un proprio pilota iscritto (`routes/championships/[id]/+page.svelte`). Ogni pilota ha una sezione a scomparsa (`components/pilot-card-plays.svelte`) con le carte giocabili e le copie ancora disponibili, conferma prima di giocare, "Annulla ultima" con gli annullamenti rimasti, l'elenco delle giocate attive e, in fondo, il riepilogo con immagini del mazzo da gioco in uso (aggiunto il 2026-10-18: intestazione "Mazzo da gioco", griglia di `CardTile` in sola lettura con le copie nel mazzo, dati da `lib/pilot-deck-api.ts` che legge `game_deck` di `GET /api/pilots/{id}`; con la gara in revisione i comandi sono bloccati, il riepilogo resta visibile). Il componente non ha più il tasto S né il parametro `ongift`, e la pagina non ha più `showGift`. I tipi stanno in `lib/card-play-types.ts` (con `CardGroup` e `CardPollSetting`, già usati da `card-play-api.ts` e `card-play-groups.ts`). Il popup "Hai ottenuto una carta sponsor" (`components/card-gift-popup.svelte`) si chiude solo con la X e, chiudendosi, segna le notifiche come viste.
- Tasto S, giudice e admin (13d): nella pagina della gara (`routes/championships/[id]/races/[raceId]/+page.svelte`) la scheda "Piloti iscritti" compare solo se l'utente può gestire le gare, la gara è in corso e il campionato è aperto (`canGift`). Elenca tutti i piloti di `race.results`, compresi quelli che poi risulteranno non partecipanti, ciascuno con il tasto S (`components/pilot-gift-button.svelte`). Il tasto apre una conferma e poi chiama `giveRandomCard`; chi assegna vede solo "Carta assegnata a [nome]", non la carta, che compare nel popup del giocatore. Il tasto resta sempre attivo e un errore del backend (per esempio pool vuota) si mostra sotto la riga del pilota.
- Controllo periodico delle notifiche (`lib/card-poll.svelte.ts`): `loadPollIntervalMs` legge l'intervallo con `fetchCardPoll` (`GET /api/admin/card-poll`) e accetta solo interi da 1 a 10 secondi; se la lettura fallisce o il valore è fuori dai limiti usa 5 secondi. La pagina del dettaglio campionato legge l'intervallo prima di avviare `startGiftPolling` (predefinito 5 secondi) e un indicatore `cancelled` impedisce l'avvio se la pagina cambia nel frattempo. Il controllo parte solo con campionato attivo e almeno un proprio pilota iscritto e non fa nulla mentre il popup è aperto. L'intervallo si legge una volta all'apertura della pagina: se l'admin lo cambia, il giocatore lo usa dopo aver ricaricato la pagina. I 15 secondi fissi non esistono più.
- Campo dell'intervallo nelle impostazioni generali (13c): `lib/card-poll-form.ts` (logica) con il suo test, il componente del form e il suo inserimento nelle impostazioni generali (commit `1ac7d77`, `3064a3b`, `5ff3694`, `c09825d`, `eed811a`). I file del form non sono stati riletti in questa sessione; le validazioni di `lib/card-poll-validation.ts` (`CARD_POLL_MIN`, `CARD_POLL_MAX`, `CARD_POLL_DEFAULT`) sono usate dal controllo periodico. Il pulsante Indietro della specifica esiste con l'etichetta "Annulla ultima", collegato all'annullamento del backend (`POST .../card-plays/undo`, disattivato senza giocate attive o annullamenti rimasti; verificato nel codice il 2026-10-18), e la revisione nella pagina della gara è stata fatta (13d, `race-review-panel.svelte`, confermata dall'autore il 2026-10-13 in `PHASE_13_SPEC.md`).
- Caricamento delle carte, admin (13f): `lib/card-crop.ts` (calcolo di vista, spostamento e zoom del ritaglio, con `CARD_WIDTH` 560 e `CARD_HEIGHT` 870, `MAX_ZOOM`, `initialView`, `panView`, `zoomView`, `sourceRect`) e il client `lib/card-admin-api.ts` (`uploadCard`, `deleteCard`), entrambi con i test `card-crop.spec.ts` e `card-admin-api.spec.ts`. Componenti: `components/card-crop-editor.svelte` (area 560x870 in cui l'immagine si sposta trascinando e si ingrandisce con il cursore dello zoom; produce un WebP, qualità 0,9, a fine trascinamento e a fine zoom), `components/card-upload-form.svelte` (nome, copie, scelta del file e anteprima del ritaglio; mostra gli errori del backend 409, 413 e 422 nel modulo), `components/pool-card-picker.svelte` (elenco delle carte della pool di base: le carte caricate a mano hanno il nome arancione e la dicitura "caricata a mano", così il colore non è l'unico segnale, e il tasto "Elimina"). La pagina `routes/admin/pools/+page.svelte` usa l'elenco nuovo e ha in fondo la card "Carica una carta", che usa il tipo scelto in "Nuova pool"; dopo un caricamento o un'eliminazione ricarica pool e carte. I colori arancioni stanno nel CSS locale del componente, in modalità chiara e scura, e non in classi Tailwind. Il ritaglio si sposta solo con mouse o dito: lo zoom funziona anche con la tastiera. `card-crop-editor.svelte` ha una riga `eslint-disable-next-line no-useless-assignment` sulla dichiarazione delle proprietà, perché `blob` è una proprietà bindable che il componente scrive e legge solo il genitore. Non sono stati riletti `card-upload-form.svelte`, `pool-card-picker.svelte` e la pagina delle pool dopo la scrittura; i limiti su copie e nome sono solo "copie almeno 1" nel modulo, il resto lo valida il backend.
- Tasti di esclusione e riepilogo del mazzo (2026-10-18): `lib/pool-exclusion.ts` (`excludeCardGroup`, con `CardGroup` "caricate" o "base", e il test `pool-exclusion.spec.ts`) azzera le copie scelte di tutte le carte caricate a mano o di tutte quelle di base nel modulo "Nuova pool", senza mutare la mappa passata e senza toccare il database; le carte del gruppo assenti dalle scelte entrano con 0, il che non cambia nulla perché la creazione tiene solo le copie maggiori di zero. `isBaseCard` in `lib/card-origin.ts` riconosce il percorso `cards/base/` (come `reload_base_pool` in `services/pools.py`); le carte di partenza (`cards/starter/`) non appartengono a nessuno dei due gruppi e non si toccano. I due tasti "Escludi tutte le carte caricate" ed "Escludi tutte le carte di base" (`type="button"`, quindi non inviano il modulo) stanno sopra l'elenco di `PoolCardPicker` in `routes/admin/pools/+page.svelte`. Il riepilogo del mazzo sta in `pilot-card-plays.svelte` con `lib/pilot-deck-api.ts` e `pilot-deck-api.spec.ts`.

## Qualità verificata

- Test backend in locale (2026-10-13): l'autore ha eseguito `python -m pytest -q` e ha riferito `447 passed in 58.39s`, senza errori né test saltati. L'esito riguarda lo stato del ramo `phase-13a-card-plays` al momento dell'esecuzione, prima dei commit della 13e (`358297a`-`14557ab`, che aggiungono anche test). Dopo la 13e l'autore ha riferito 474 test del backend passati in 60,54 secondi (13 ottobre 2026, esito riferito e riportato anche in `PHASE_13_SPEC.md`; non letto dalla CI di quel commit); i comandi frontend e migrazioni eseguiti in locale non sono stati comunicati. Per frontend e migrazioni vale la CI.
- CI su ogni pull request: test backend, controlli frontend con lint, test e build, migrazioni su un database creato da zero (upgrade, verifica, downgrade, nuovo upgrade). Sulla pull request #5 i tre controlli erano verdi sull'ultimo commit `24388ea` prima dell'unione in `main`.
- Riallineamento dei documenti (2026-10-13): la CI della pull request #9 è risultata verde, con i tre controlli (Migrazioni, Frontend, Backend pytest) completati con successo, sull'esecuzione 38321458934 partita alle 23:18:46 UTC del 2026-10-12, subito dopo il commit `9405c97` (`PHASE_13_SPEC.md`, solo documenti); l'elenco dei controlli non riporta lo SHA, che si deduce dall'orario. Il controllo Backend (pytest) è terminato alle 23:20:11 UTC; una prima lettura lo aveva trovato ancora in corso. L'autore ha segnalato lo stesso esito. I commit successivi (`SHOP_DESIGN.md` e questo file) fanno partire nuove esecuzioni, non ancora lette. I commit del 2026-10-13 che aggiungono `DATABASE.md`, `SETUP.md` e `SCRIPTS.md` e aggiornano questo file toccano solo documenti; la CI su di essi non è stata letta.
- Pull request #9 (fase 13, per ora 13a, 13b, 13c-1, parte della 13c e il tasto S della 13d): dopo il commit `605a51b` (tasto S nella pagina della gara) i tre controlli (Backend pytest, Migrazioni, Frontend con check, lint, test e build) sono partiti tra le 19:19 e le 19:20 UTC del 2026-10-12 e sono tutti completati con successo (letti alle 21:21 CEST); l'elenco dei controlli non riporta il commit, che si deduce dall'orario. Il commit precedente `b1e202a` da solo non supera il type-check, perché la pagina del campionato passava ancora `ongift`: se la CI gira su ogni commit, quel commit risulta rosso, mentre la testa del ramo è verde. Erano verdi anche dopo `f2235ed` (18:23 UTC), `eed811a` (17:39 UTC), sulla testa precedente `45ba64c` e sui commit `e1de642` (ultimo commit di codice e di test della 13c-1), `a087855`, `c5c45e0` (modello e migrazione di `card_gift`), `ede7aba` (tasto S) e `f71cb19` (ultimo commit di codice della 13b). I test non sono stati eseguiti in locale da chi ha scritto il codice di backend: l'esito viene dalla CI di GitHub.
- Revisione con revisore unico, riapertura e rimozione (13b): la CI della pull request #9 è risultata verde (Backend pytest, Migrazioni, Frontend) sull'esecuzione partita alle 22:47:16 UTC del 2026-10-12, subito dopo il commit dei test `55fbcea` (22:47:08 UTC); l'elenco dei controlli non riporta lo SHA, che si deduce dall'orario.
- Pull request #11 (`phase-13a-judge-guard-tests`, unita nel ramo `phase-13a-card-plays` con il merge `f733886`, 23:10 UTC del 2026-10-12): il commit dei test `2f12768` aggiunge test sulla scadenza della revisione e sul secondo giudice, su bonus e annullo. L'esito della CI su quel commit non è stato letto; l'esecuzione locale del 2026-10-13 (447 test passati) comprende anche questi test. Il ramo `phase-13a-judge-guard-tests` non compare più nell'elenco dei rami.
- Tasto S per giudice e admin (13d, backend): il commit `0f9c9b1` (19:31 UTC del 2026-10-12) porta `_load_gift_pilot` e `_authorize_gift` in `services/card_gift.py` e i test relativi; i tre controlli della pull request #9 (Backend pytest, Migrazioni, Frontend) sono partiti alle 19:31:51 UTC e risultano completati con successo (letti alle 21:34 CEST; l'elenco non riporta lo SHA, che si deduce dall'orario).
- Lint del form dell'intervallo: `prettier --check` aveva segnalato `src/lib/card-poll-form.ts`; l'autore ha riscritto il file con righe più brevi (commit `1ac7d77`) e ha tolto un apostrofo da un titolo nei test (commit `5ff3694`); dopo `eed811a` il controllo frontend della CI è verde.
- Frontend della 13c (commit `6fdcad1` e `678fe65`): un primo `npm run check` ha dato 9 errori, causati da `card-play-types.ts` riscritto senza `CardGroup` e `CardPollSetting` (poi ripristinati dal commit `d3dc8ee`) e da una variabile locale chiamata `state` che nascondeva la rune `$state` (ora `cardState`). Dopo la correzione l'autore ha riferito, il 2026-10-12, che i controlli sono andati a buon fine in locale; la CI di GitHub ha poi confermato il controllo frontend verde. Il componente `pilot-gift-button.svelte` (13d) e il blocco "Piloti iscritti" non hanno test dedicati: la CI conferma solo type-check, lint e build. Non esistono test dedicati agli altri nuovi componenti né al legame tra pagina e intervallo letto; il form dell'intervallo ha un test sulla sola logica. Anche l'inventario in due sezioni del dettaglio pilota non ha test frontend.
- File della 13c e della 13d riscritti per intero: `card-poll.svelte.ts`, `card-gift-popup.svelte`, `pilot-card-plays.svelte`, la pagina del dettaglio campionato e la pagina della gara. Per le ultime tre le versioni esistenti erano state lette prima; per le prime due no. Se il commit `d3dc8ee` conteneva funzioni in più (per esempio nelle versioni di `card-play-api.ts` e `card-play-groups.ts`, che i nuovi componenti non usano), vanno confrontate e riprese.
- Test backend dell'inventario sponsor (`backend/tests/test_pilot_deck_api.py`, 3 test aggiunti nel commit `f2235ed`): inventario sponsor vuoto, carte sponsor separate da inventario modifiche e mazzo da gioco, nessuna carta sponsor spostabile nel mazzo da gioco (404). Esito noto dalla CI e dall'esecuzione locale del 2026-10-13.
- Test backend delle carte giocate (`backend/tests/test_card_plays.py`, 14 test): giocata e copie disponibili fino a esaurimento, inventario invariato durante la gara, carta inesistente, annullamento (copia liberata e registro conservato), annullamento senza giocate, cinque annullamenti e limite, azzeramento giocando una nuova carta, nessuna giocata a gara chiusa, pilota di un altro utente (404), pilota eliminato (404 in giocata e annullamento), consumo alla chiusura, annullate non consumate, ultima copia rimossa dall'inventario.
- Test backend del tasto S (`backend/tests/test_card_gifts.py`, 13 test): spostamento di una copia dalla pool all'inventario, riga nuova se la carta non era posseduta, pool vuota (409), nessuna gara in corso (409), giocatore su un pilota di un altro utente (404), admin e giudice su un pilota iscritto altrui (201), notifica al proprietario del pilota dopo il regalo del giudice, giudice su pilota non iscritto (403), su pilota inesistente (404) e con pool vuota (409), carta regalata giocabile nella stessa gara, notifiche non viste elencate e poi segnate come viste (204). Non c'è un test del giudice con la gara in revisione.
- Test backend del revisore (13b): `backend/tests/test_card_judge.py` (riepilogo, annullo, bonus e 13 test della rimozione), `backend/tests/test_race_review.py` (apertura, rinuncia, conferma e consumo delle carte, revisore unico), `backend/tests/test_race_review_reopen.py` (lettura dello stato con `is_last_race`, scadenza con conferma automatica, riapertura dell'admin: 403 al giudice e al giocatore, 409 se non confermata, prima dei risultati o su gara non ultima, 404 per gara o campionato inesistenti, nessun doppio consumo dopo la riconferma) e `backend/tests/test_card_judge_reopen.py` (6 test dell'annullo di giocate già consumate dopo la riapertura: carta che torna dalla pool, doppio annullo, 409 se la pool ha perso la carta, 409 senza revisione attiva, 409 per un altro revisore, nuova conferma che consuma solo la giocata rimasta). La scadenza è provata portando la data di apertura a 20 minuti prima direttamente nel database, senza orologio finto. Le funzioni di supporto sono in `test_race_review.py` e gli altri file le importano; in `test_card_judge.py` e nei file più vecchi alcune sono ancora ricopiate e la duplicazione si può ripulire. I test della pull request #11 (commit `2f12768`) non sono stati riletti per questo documento: non si sa in quale file stiano né quanti siano.
- Test backend dell'intervallo di controllo (`backend/tests/test_card_poll_settings.py`, 8 test): predefinito 5 per admin, giocatore e giudice, 401 senza login, modifica visibile a tutti, limiti 1 e 10 accettati, valori fuori dai limiti o non numerici o mancanti rifiutati con 422 senza cambiare il valore salvato, 403 a giocatore e giudice e 401 all'anonimo sulla modifica, nessun effetto sulle regole dell'oro delle impostazioni generali (e viceversa), valore valido anche per i campionati già esistenti. Le funzioni di supporto sono importate da `test_races_api`.
- Test backend della 13e: il commit `14557ab` ("test(13e): caricamento, eliminazione e pulizia dei file delle carte") aggiunge i test di caricamento, eliminazione e pulizia dei file delle carte. I nomi dei file di test e il numero dei test non sono stati riletti per questo documento.
- Frontend della 13f (2026-10-14): `prettier --check` aveva segnalato `card-admin-api.spec.ts`, `card-crop.spec.ts` e `card-crop.ts`, sistemati con il commit `254b015`. Dopo i componenti (`e5cf313`), `eslint` aveva segnalato in `card-crop-editor.svelte` un'assegnazione inutile su `blob` (`no-useless-assignment`) e due `svelte-ignore` non necessari: i commit `062629f` (ignore tolti e azzeramento di `blob` in una funzione) e `1391a70` (default `$bindable()` senza `null`) non hanno eliminato l'errore sulla riga 21, che è sparito con `8dbd7c2` (riga `eslint-disable-next-line`). Dopo `8dbd7c2` l'autore ha riferito "ora funziona tutto"; i singoli comandi (`lint`, `test`, `check`, `build`) e la prova a mano del caricamento e dell'eliminazione di una carta non sono stati descritti uno per uno. Il 2026-10-18 l'autore ha riferito che test e CI sono passati tutti e la CI è stata letta: verde sul commit `9f3b517` (esecuzione 38480483060, partita alle 22:50:49 UTC del 2026-10-13; Backend pytest, Migrazioni e Frontend con successo). L'assistente non ha eseguito nulla in locale: non risultano test dedicati ai componenti della 13f (solo la logica di `card-crop.ts` e di `card-admin-api.ts` ha i test).
- Frontend della 13f, chiusura (2026-10-18): aggiunti i due tasti di esclusione delle pool personalizzate e il riepilogo con immagini del mazzo da gioco nella sezione per pilota. Controlli eseguiti in locale dall'assistente il 2026-10-18: `npm ci`, `npm run check` (0 errori, resta il solo warning preesistente del canvas in `card-crop-editor.svelte`), `npm run lint` (Prettier ed ESLint puliti), `npm test` (110 test passati su 110: base misurata 101 prima delle aggiunte, i 9 nuovi sono 7 di `pool-exclusion.spec.ts` e 2 di `pilot-deck-api.spec.ts`) e `npm run build` (riuscito). Backend non toccato: nessun test locale, vale la CI.
- Verifica nel browser del 2026-10-18 (assistente, Chromium headless con Playwright su un'installazione locale: backend con `heat.db` creato dalle migrazioni, admin, pool di base ricaricate, una carta caricata a mano, campionato con un pilota iscritto e una gara in corso): i due tasti di esclusione azzerano solo il gruppo previsto, conservano le quantità dell'altro gruppo, non inviano il modulo e la pool creata dopo l'esclusione contiene solo le carte non escluse (verificato anche via API); la sezione del pilota nasce aperta con un solo iscritto e il riepilogo "Mazzo da gioco" mostra le immagini con le copie in sola lettura. Nessuno sforamento orizzontale a 375 px nelle aree modificate; lo sforamento che resta a 375 px è del menu a tendina dell'intestazione (navigazione admin, `ul.absolute` del `details` nella `nav`), preesistente e non toccato dalla 13f: da sistemare nella fase 14.
- Il test `backend/tests/test_migrations.py` applica tutte le migrazioni a un database vuoto e confronta tabelle e colonne con i modelli: non cita l'elenco delle migrazioni, quindi le nuove `f8a4d2c6e0b1` e `a9c3e7b1d5f0` non richiedono modifiche.
- Non coperti dai test (elenco della 13a, da verificare contro i file di test più recenti): correzione dei risultati da parte dell'admin dopo la chiusura (le carte non devono cambiare), campionato senza pool sponsor in chiusura, campionato chiuso nella giocata, estrazione casuale con più carte diverse in pool. Non ho riletto tutti i file per stabilire quali altre voci di prima siano ora coperte da `test_race_review.py`, dai test del revisore e dai test della pull request #11.
- Test frontend del Negozio: 9 in `shop-sort.spec.ts`, 7 in `pack-reveal-phases.spec.ts`, 3 in `pack-summary.spec.ts`. Il componente grafico `pack-reveal.svelte` (taglio della busta, scorrimento, riepilogo) non ha test dedicati e si verifica a mano; l'autore ha verificato a mano riepilogo, elenco `/shop`, storico e storico completo dell'admin. Il numero totale di test frontend non è stato aggiornato qui.
- Non hanno test dedicati: costo predefinito dei pacchetti, ordine delle gare, anteprima della ricarica, lock sul database. `cardDelayMs` in `pack-reveal-phases.ts` non è più usato dal componente ed è rimasto solo per il suo test.
- Non letti: `shop-api.ts` (si presume che `fetchAllHistory` chiami `GET .../shop/history/all`) e `shop-history-list.svelte` (non si sa se raggruppi per pilota).
- Migrazioni Alembic: oro per gara (`c9f3a1b6d8e4`), tabelle del Negozio (`a1c5e9b3d7f2`), unione delle teste (`b2d6f0a4c8e1`), tabella `card_play` (`c3e7a1d5b9f2`), stato "in revisione" (`d4f8b2e6a0c3`), tabella `card_gift` (`e7a3c9d1f5b2`), intervallo di controllo (`f8a4d2c6e0b1`), revisore unico con `review_started_by_user_id` (`a9c3e7b1d5f0`). Dopo un'unione di teste `alembic downgrade -1` dà "Ambiguous walk": si usa la revisione precisa. I commit `f2235ed`, `b1e202a`, `605a51b` e `0f9c9b1` non aggiungono migrazioni. Non è stato letto se i commit della 13e aggiungano una migrazione.
- Documenti da riallineare (dopo la 13d, su richiesta dell'autore): `PROJECT_SPEC.md` è stato riallineato alla fase 13 nel commit `bc0fbfb` (revisione, intervallo di controllo, tasto S, migrazioni); `PHASE_13_SPEC.md` è stato aggiornato il 2026-10-13 (commit `9405c97`) con l'intervallo di controllo, il permesso del tasto S per giudice e admin, la sottofase 13c-1 e la pull request #11; `SHOP_DESIGN.md` è stato riallineato il 2026-10-13 (commit `8947c43` e `c7fbe7f`): intestazione, blocco del negozio anche in revisione e uso delle carte sponsor in gara nella sezione 7. Resta `PROJECT_NOTES.md` (non elenca ancora i file della 13a, della 13b, della 13c-1, della 13c e del tasto S della 13d). Il contenuto di `PROJECT_SPEC.md` dopo `bc0fbfb` non è stato riletto qui, quindi non si sa se il refuso "varà" e la sezione 14 siano già a posto. Di `SHOP_DESIGN.md` resta da verificare se le sezioni 4 e 6 descrivano ancora ogni estrazione come carta separata (nel testo riscritto la sezione 6 raggruppa le copie uguali nel riepilogo). `DATABASE.md`, `SCRIPTS.md` e `SETUP.md`, richiesti dalle istruzioni del progetto, sono stati creati il 2026-10-13 in `docs/`; `DATABASE.md` descrive anche lo schema di `card_play`, `card_gift`, `card_poll_seconds`, `review_started_at` e `review_started_by_user_id`, letto dai modelli. Il campo `sponsor_inventory` è solo nello schema API e non cambia il database. Dopo la 13e e la 13f, `PROJECT_SPEC.md`, `PHASE_13_SPEC.md` e `PROJECT_NOTES.md` vanno riletti per controllare che descrivano il caricamento e l'eliminazione delle carte e il ritaglio (l'autore ha riferito che sono allineati all'ultimo commit; non verificato).

## API principali

| Area | Prefisso |
|---|---|
| Autenticazione | `/api/auth` |
| Team | `/api/teams` |
| Piloti | `/api/pilots` |
| Pool (anche anteprima e ricarica) | `/api/pools` |
| Campionati, iscrizioni, gare e classifica | `/api/championships` |
| Negozio del giocatore (vista, acquisto, inventario, storico) | `/api/championships/{id}/shop` |
| Carte sponsor giocate (giocata, annullamento, stato) | `/api/championships/{id}/card-plays` |
| Tasto S e notifiche di carta ottenuta | `/api/championships/{id}/card-gifts` |
| Revisione, riepilogo, correzioni, bonus, rimozione e riapertura | `/api/championships/{id}/races/{race_id}` |
| Negozi dell'utente (campionati con pilota iscritto) | `/api/me` |
| Amministrazione e pulizia (anche intervallo di controllo delle notifiche) | `/api/admin` |
| Template e immagini del Negozio (admin) | `/api/shop` |
| Salute del servizio | `/health` |

Rotte del Negozio per il giocatore: `GET /{id}/shop?pilot_id=`, `POST /{id}/shop/purchases`, `GET /{id}/shop/inventory?pilot_id=`, `GET /{id}/shop/history`, `GET /{id}/shop/history/all` (solo admin). Elenco dei negozi dell'utente: `GET /api/me/shops`.

Rotte delle carte sponsor giocate (13a): `GET /{id}/card-plays?pilot_id=` (giocate, copie disponibili, annullamenti rimasti), `POST /{id}/card-plays` (giocata, 201), `POST /{id}/card-plays/undo` (annullamento). Errori: 404 campionato o pilota inesistenti o eliminati, 403 pilota non iscritto, 409 campionato chiuso, nessuna gara in corso, gara in revisione, carta non disponibile, niente da annullare, limite di 5 annullamenti.

Rotte del tasto S (13b, descritte come per il giocatore): `POST /{id}/card-gifts` (corpo `pilot_id`, 201 con la carta ottenuta), `GET /{id}/card-gifts?pilot_id=` (notifiche non viste), `POST /{id}/card-gifts/seen` (corpo `pilot_id`, 204). Errori: 404 campionato o pilota, 403 pilota non iscritto, 409 campionato chiuso, nessuna gara in corso, gara in revisione, pool sponsor vuota. Admin e giudice possono usarla su qualsiasi pilota iscritto non eliminato, il giocatore solo sui propri (404 per i piloti di altri utenti); il frontend della 13d la chiama dalla scheda "Piloti iscritti". Le notifiche (`GET` e `seen`) si leggono solo per i propri piloti.

Rotte della revisione (13b), tutte sotto `/api/championships/{id}/races/{race_id}`: `GET /review` (qualsiasi utente collegato; prima conferma le revisioni scadute del campionato; risposta con `in_review`, `reviewer_user_id`, `review_expires_at`, `review_closed_at`, `is_last_race`), `POST /review` (giudice o admin, apre la revisione o riprende la propria), `DELETE /review` (revisore, rinuncia), `POST /review/confirm` (revisore, oppure admin se scaduta o mai aperta), `POST /review/reopen` (solo admin, solo ultima gara confermata), `GET /card-plays` (riepilogo per pilota), `POST /card-plays/{play_id}/cancel` (annulla una giocata, anche già consumata), `POST /card-bonus` (corpo `pilot_id` e `card_name`, 201, senza notifica) e `POST /card-removal` (una copia dall'inventario del pilota alla pool). Le azioni sulle carte sono del solo revisore con la revisione attiva. Errori: 404 campionato, gara, pilota o giocata inesistenti, 403 pilota non iscritto o riapertura di chi non è admin, 409 revisione di un altro utente o non attiva, campionato chiuso, giocata non più annullabile, carta non in pool o non in inventario, gara non ultima o revisione non confermata nella riapertura.

Rotte dell'intervallo di controllo (13c-1): `GET /api/admin/card-poll` (risposta `{"seconds": N}`, ogni utente collegato) e `PUT /api/admin/card-poll` (corpo `{"seconds": N}` con N da 1 a 10, solo admin). Errori: 401 senza login, 403 al giocatore e al giudice sulla modifica, 422 per valori fuori dai limiti, non numerici o mancanti.

Rotte admin delle carte (13e): il commit `e26801e` aggiunge le rotte per caricare ed eliminare le carte sotto l'area di amministrazione; percorsi esatti, corpi, limiti ed errori non sono stati riletti e vanno aggiunti qui dopo la lettura del codice. Il frontend della 13f le chiama da `lib/card-admin-api.ts` (`uploadCard`, `deleteCard`) e distingue gli errori 409, 413 e 422, ma i percorsi non sono stati riletti nemmeno da lì.

Dettaglio pilota (13c): le risposte di `GET /api/pilots/{id}`, `deck/add` e `deck/remove` portano anche `sponsor_inventory` (elenco delle carte sponsor del pilota).

## Decisioni e questioni aperte

Decisioni dell'autore (2026-10-08): tetto di 100 copie per carta (409); l'admin con un pilota iscritto è un normale giocatore, con in più il tasto delle impostazioni del negozio; un pilota eliminato non può comprare durante un campionato attivo; il giocatore non vede lo storico di un pilota eliminato.

Decisioni dell'autore (2026-10-10): la 12c è approvata; la ricarica delle pool chiede conferma elencando le carte da togliere; per il deploy online gli acquisti si serializzano con un blocco sul database; la pool sponsor è usata dai pacchetti; i pacchetti nuovi costano 10 oro o 2 sponsor; lo storico resta una pagina separata e l'inventario un solo pulsante.

Decisioni dell'autore (2026-10-11): la busta usa come texture l'immagine del pacchetto acquistato; la striscia strappata se ne va e la busta resta tagliata; le carte si vedono una alla volta e ogni tocco le fa scorrere a sinistra; alla fine compare un riepilogo con tutte le carte; "Salta" porta al riepilogo; fino al riepilogo la finestra si chiude solo con la X, dal riepilogo in ogni modo. Le copie uguali nel riepilogo sono raggruppate con il numero di copie; Esc non chiude prima del riepilogo. L'elenco `/shop` e lo storico sono considerati a posto, come lo storico completo dell'admin dalle impostazioni del negozio. La pull request #5 è stata unita in `main` (merge `6dd5619`).

Decisioni dell'autore (2026-10-12): lo spareggio sportivo non serve; le pool di base esistono e funzionano; l'uso online è rinviato a dopo la fase 14; la fase 13 realizza le carte sponsor in gara (uso con conferma, annullamento fino a 5, stato "in revisione", tasto S, restituzione alla pool alla chiusura) e l'amministrazione delle carte (caricamento con ritaglio e zoom, nome e quantità, nomi in arancione, esclusione di caricate o di base nelle pool personalizzate); la fase 14 è di sistemazione generale e miglioramenti; i documenti si riallineano dopo la 13d, ma le correzioni rese necessarie da un cambiamento si fanno subito. I dettagli sono in `PHASE_13_SPEC.md`. La pull request #9 raccoglie tutta la fase 13 e non solo la 13a. Gli annullamenti consecutivi si calcolano dal registro, senza colonna dedicata (`cancelled_at` non si aggiunge). Le gare non si eliminano a mano. Il bonus che il giudice dà alla fine non crea notifiche e serve solo a correggere errori; la notifica "Hai ottenuto una carta sponsor" nasce solo dal tasto S. L'intervallo con cui il giocatore controlla le nuove notifiche è un'impostazione generale dell'admin, da 1 a 10 secondi con predefinito 5, valida per tutti i campionati. Tutto il lavoro della fase 13 resta nel ramo `phase-13a-card-plays`: non si creano rami separati per le sottofasi (il ramo `phase-13c-card-ui`, creato per errore, è stato cancellato dall'autore; il ramo `phase-13a-judge-guard-tests` è stato unito con la pull request #11 e non compare più tra i rami; restano altri rami di sottofase creati per errore, come `phase-13a-sponsor-play`, `phase-13a-sponsor-play-v2`, `phase-13b-card-removal` e `phase-13b-review-ui`, da eliminare a cura dell'autore dopo l'unione in `main`). Il nome di una sottofase non è vincolante: quando si passa alla sottofase successiva si usa il nome di quella (i commit dal `1ac7d77` all'`eed811a` portano "13e" ma appartengono alla 13c).

Decisioni dell'autore (2026-10-12, 13d): il tasto S sta nella pagina della gara accanto a ogni pilota, visibile solo a giudice e admin con la gara in corso; apre una conferma; chi lo preme non vede la carta ottenuta, che vede solo il giocatore nel popup; il giocatore non ha più il tasto S. Giudice e admin lo vedono per tutti i piloti iscritti, ogni giocatore vede la carta ottenuta per i propri piloti nella sua sessione; ogni utente ha un ruolo.

Decisioni dell'autore (2026-10-13, revisione): un solo revisore, chi preme "termina gara"; nessun altro, nemmeno l'admin, vi accede durante la revisione (409); scadenza di 15 minuti dall'inizio, con conferma automatica così com'è alla prima richiesta successiva; il revisore può annullare giocate, dare bonus e rimuovere carte dall'inventario dei piloti (la carta torna nella pool); l'admin può riaprire la revisione confermata solo dell'ultima gara del campionato, con altri 15 minuti. Il dettaglio è in `PHASE_13_SPEC.md`.

Decisione dell'autore (2026-10-13, negozio): il negozio resta bloccato (nessun acquisto) anche mentre la gara è in revisione. L'autore ha inoltre eseguito `python -m pytest -q` in locale (447 test passati) e ha riferito che i test sono a posto, dato che le uniche modifiche successive riguardano i documenti.

Decisione dell'autore (2026-10-13, documenti): i documenti si riallineano alla fine di ogni sottofase quando i test vanno a buon fine (quindi alla fine della 13e, non solo alla fine della 13); un messaggio vuoto dell'autore vale come "ok" a procedere. Dopo la 13e l'autore ha riferito che tutto funziona e che i documenti sono allineati all'ultimo commit.

Scelte della 13a da confermare (dell'assistente, non ancora approvate): il consumo alla chiusura sta in un modulo separato (`card_play_close.py`) per evitare un import circolare; con una pool sponsor assente le carte consumate non tornano in nessuna pool.

Scelte della 13b da confermare (dell'assistente, non ancora approvate): il tasto S estrae con probabilità proporzionale alle copie in pool; l'annullamento della giocata da parte del revisore usa lo stato `annullata`, quindi il conteggio degli annullamenti consecutivi non distingue chi ha annullato e può ridurre quelli rimasti al giocatore (per evitarlo serve un nuovo stato o una colonna); il bonus non si dà a campionato chiuso; `services/card_gift.py` e `services/card_judge.py` importano funzioni private (`_authorize`, `_ensure_not_in_review`, `_open_race`, `_lock_database`) da altri servizi.

Scelte della 13c-1 da confermare (dell'assistente, non ancora approvate): la lettura dell'intervallo per i giocatori sta nel router admin (`GET /api/admin/card-poll`) perché la restrizione ad admin è per rotta e non si è letto dove sono montati gli altri router; se si preferisce un percorso più pulito, per esempio sotto `/api/me`, si sposta. Il valore sta su `championship_defaults` e non viene copiato nei campionati.

Scelte della 13c da confermare (dell'assistente, non ancora approvate): il controllo periodico ora usa l'intervallo di `GET /api/admin/card-poll` (risolto il contrasto con i 15 secondi fissi), ma lo legge una sola volta all'apertura della pagina, quindi una modifica dell'admin vale dopo il ricaricamento; le funzioni di rete del popup e della sezione per pilota vanno ririviste rispetto a `card-play-api.ts` (il controllo periodico lo usa già per l'intervallo e le notifiche); l'immagine nel popup della carta ottenuta usa il percorso `/media/{card_path}`, da verificare con quello usato dal resto del frontend; la sezione per pilota usa `CardTile` con le copie ancora giocabili. L'inventario del dettaglio pilota è diviso in "Modifiche" e "Sponsor" a sezioni chiuse all'apertura, con gli sponsor in sola lettura: scelta dell'assistente, da confermare.

Scelte della 13d da confermare (dell'assistente, non ancora approvate): il tasto S resta sempre attivo anche con la pool sponsor vuota e l'avviso arriva dal backend (la specifica prevedeva il tasto disabilitato in anticipo con un avviso; il frontend non può leggere lo stato della pool, quindi servirebbe una rotta nuova); la scheda "Piloti iscritti" elenca anche i piloti che saranno dichiarati non partecipanti; il backend lascia al giocatore l'uso di `POST /{id}/card-gifts` sul proprio pilota, anche se l'interfaccia non mostra più il tasto S ai giocatori; se si vuole rifiutarlo anche via API basta restringere `_load_gift_pilot`, e un test che oggi dà il regalo come giocatore va riscritto.

Scelte della 13f da confermare (dell'assistente, non ancora approvate): il tasto "Elimina" compare sulle sole carte caricate a mano, nell'elenco della pool di base; il modulo di caricamento usa il tipo scelto in "Nuova pool" invece di averne uno proprio; la qualità del WebP del ritaglio è 0,9 e l'area di lavoro è 560x870; il modulo non limita nome e copie oltre a "copie almeno 1"; l'immagine si sposta solo con il puntatore (nessun comando da tastiera per lo spostamento); la riga `eslint-disable-next-line no-useless-assignment` su `blob` si può sostituire con una funzione di ritorno passata dal genitore al posto di `bind:blob`, ma servirebbe modificare `card-upload-form.svelte`.

Correzione del 2026-10-10: una versione precedente di questo file e di `SHOP_SCHEMA.md` dava per non necessaria `GET /api/me/shops`; la rotta esiste ed è usata dal frontend.

Questioni rinviate:

- Per il deploy online: un solo server con pochi worker, perché SQLite accetta una sola scrittura alla volta; con un altro database serve un blocco sulla riga del pilota (`SELECT ... FOR UPDATE`).
- Documenti di schema e di script: `DATABASE.md`, `SETUP.md` e `SCRIPTS.md` sono stati creati il 2026-10-13. `SETUP.md` e `SCRIPTS.md` sono stati scritti da `heat.py` e `config.py` e vanno riletti rispetto al codice (comandi, porte, versioni); `DATABASE.md` non descrive le eventuali migrazioni e i percorsi della 13e. Le istruzioni del progetto chiedono anche `setup.py`, `setup.bat`, `setup.sh` e `scripts/`, che non esistono nella radice del ramo (il loro ruolo è oggi di `heat.py`): da decidere con l'autore.

## Documenti

- `PROJECT_SPEC.md`: specifiche funzionali (fonte delle regole).
- `PROJECT_NOTES.md`: mappa del codice, comandi, convenzioni e contesto di lavoro.
- `OPEN_QUESTIONS.md`: decisioni ancora rinviate.
- `PHASE_13_SPEC.md`: decisioni e sottofasi della fase 13 (carte sponsor e amministrazione delle carte).
- `SHOP_DESIGN.md`: funzionamento del Negozio spiegato dall'autore.
- `SHOP_SCHEMA.md`: schema, servizi, rotte e sottofasi del Negozio.
- `DATABASE.md`: schema completo del database, letto dai modelli SQLAlchemy (creato il 2026-10-13).
- `SETUP.md`: installazione e avvio (creato il 2026-10-13, da `heat.py` e `config.py`).
- `SCRIPTS.md`: comandi di `heat.py` (creato il 2026-10-13).
- Documenti storici (fotografie di una fase): `DATABASE_ANALYSIS.md`, `BACKEND_BOOTSTRAP.md`, `BACKEND_AUTH.md`, `FRONTEND_BOOTSTRAP.md`, `FRONTEND_AUTH.md`.

## Prossimi passi

1. Fase 13 conclusa: pull request #9 unita in `main` il 2026-10-18 (merge `cdea876`). Con l'autore: definire la fase 14 (sistemazione generale, modifiche di vivibilità e miglioramenti, compreso il menu dell'intestazione che a 375 px sfora, trovato il 2026-10-18).
2. Unione del ramo `phase-12f-docs` (solo documenti) in `main`, a cura dell'autore.
3. Riallineamento dei documenti ancora indietro: rileggere `SETUP.md` e `SCRIPTS.md` rispetto a `heat.py`; decidere con l'autore il destino di `setup.py`, `setup.bat`, `setup.sh` e `scripts/`. Il riallineamento della sezione 14 di `PROJECT_SPEC.md` alla 13e e alla 13f è stato fatto in questa seduta (commit su `main`); resta da rileggere il refuso "varà" dopo `bc0fbfb` se presente.
4. Dopo l'unione in `main`: eliminare i rami di sottofase creati per errore (a cura dell'autore).

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
