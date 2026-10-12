# Stato del progetto — Heat

Ultimo aggiornamento: 2026-10-12

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
| 13 | Carte sponsor in gara e amministrazione delle carte (decisioni in `PHASE_13_SPEC.md`); la pull request #9 raccoglie tutta la fase | In corso |
| 13a | Backend carte sponsor: registro delle carte giocate, stack da 5 annullamenti, uso e annullamento, restituzione alla pool alla chiusura | Completata nel ramo `phase-13a-card-plays` (pull request #9 in bozza, CI verde sul commit dei test `a087855`) |
| 13b | Backend: stato "in revisione", riepilogo, correzione e bonus, tasto S, notifica di carta ottenuta | Completata nel ramo `phase-13a-card-plays` (CI verde sul commit `f71cb19`: test backend, migrazioni e frontend) |
| 13c | Frontend giocatore: sezioni per pilota, uso delle carte, Indietro, inventario in due sezioni, popup "Hai ottenuto una carta sponsor" | Da fare |
| 13d | Frontend giudice e admin: elenco piloti con tasto S, riepilogo con immagini, correzioni | Da fare |
| 13d+ | Riallineamento di tutti i documenti (richiesto dall'autore) | Da fare |
| 13e | Backend amministrazione carte: caricamento, conversione, eliminazione, origine "caricata" | Da fare |
| 13f | Frontend: ritaglio con zoom, nome e quantità, nomi in arancione, tasti di esclusione nelle pool personalizzate | Da fare |
| 13g | Documenti e test finali, unione in `main` | Da fare |
| 14 | Sistemazione generale, modifiche di vivibilità e miglioramenti | Da definire a fine fase 13 |

## Backend

- FastAPI, SQLAlchemy 2.0, Alembic e SQLite in `backend/`.
- Autenticazione con password hashate e cookie di sessione httpOnly; ruoli `admin`, `judge` e `player`; primo admin creato con setup.
- Team e piloti con nomi unici senza distinguere maiuscole, rinomina ed eliminazione logica. Un pilota può non avere un team, ma deve averne uno per iscriversi a un campionato.
- Ogni pilota possiede tre mazzi: inventario delle modifiche, inventario sponsor (vuoto alla creazione) e mazzo da gioco; blocco ottimistico con numero di versione (409 in caso di conflitto).
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
- Negozio, accesso e vista (`services/shop_view.py`): il giocatore entra con un proprio pilota iscritto e solo a campionato attivo; l'admin entra sempre (sola lettura senza pilota o a campionato chiuso, come un giocatore con un pilota iscritto). Con una gara in corso gli acquisti sono bloccati.
- Negozio, elenco dei negozi dell'utente: `GET /api/me/shops` (`api/shop_me.py`, `services/shop_list.py`).
- Negozio, storico e inventario (12c-2): `services/shop_history.py` e `services/shop_inventory.py`. Il giocatore non vede gli acquisti di un pilota che ha eliminato; l'admin sì.
- Carte sponsor giocate (13a): tabella `card_play` (modello `CardPlay`, migrazione `c3e7a1d5b9f2`) con gara, pilota, nome e percorso della carta, stato (`giocata`, `annullata`, `consumata`) e data della giocata (`played_at`); non esiste una data di annullamento. `services/card_play.py` gestisce giocata, annullamento e stato; le copie disponibili sono quelle dell'inventario sponsor meno le giocate attive della gara in corso, e l'inventario non cambia durante la gara. Gli annullamenti consecutivi sono le giocate annullate dopo l'ultima ancora attiva (massimo 5, si azzera giocando una nuova carta); non c'è una colonna dedicata. Il pilota deve essere del giocatore, non eliminato e iscritto; serve una gara in corso in un campionato attivo. Le righe del registro non si cancellano mai durante il gioco: l'eliminazione logica del pilota (`deleted_at`) le lascia, e solo l'eliminazione definitiva del pilota (`_purge_pilot` in `services/cleanup.py`) le rimuove. Le gare non si eliminano a mano, quindi nessuna riga segue la sorte di una gara.
- Carte sponsor, chiusura della gara (13a): `services/card_play_close.py` (`consume_plays`), richiamato da `set_results` in `services/races.py` solo alla prima chiusura della gara e nella stessa transazione. Le giocate attive passano a `consumata`, escono dall'inventario sponsor del pilota e tornano nella pool sponsor del campionato; le annullate restano in inventario. Le correzioni dell'admin non toccano le carte. Senza pool sponsor sul campionato le carte escono dall'inventario ma non tornano in nessuna pool; se una carta giocata non è più in inventario la chiusura si ferma con un errore.
- Stato "in revisione" (13b): colonna `Race.review_started_at` (migrazione `d4f8b2e6a0c3`), con `services/race_review.py` e `api/race_review.py`. Durante la revisione giocata, annullamento e tasto S sono bloccati (409); il giudice e l'admin possono ancora correggere e dare il bonus.
- Tasto S e notifica (13b): tabella `card_gift` (modello `CardGift`, migrazione `e7a3c9d1f5b2`) con gara, pilota, nome e percorso della carta, `created_at` e `seen_at` (vuoto finché il giocatore non ha visto la notifica). `services/card_gift.py` (`draw_gift`) estrae una carta dalla pool sponsor del campionato con probabilità proporzionale alle copie, ne toglie una dalla pool (riga rimossa a zero), la aggiunge all'inventario sponsor del pilota (riga nuova se mancava) e crea la notifica, in un solo commit. Serve il proprio pilota iscritto, una gara in corso non in revisione e almeno una copia in pool (409 se la pool è vuota o assente). La carta regalata è subito giocabile nella stessa gara. `list_unseen_gifts` e `mark_gifts_seen` leggono e chiudono le notifiche non viste del pilota nel campionato.
- Riepilogo, correzione e bonus del giudice (13b): `services/card_judge.py`, con le rotte in `api/race_review.py` (giudice o admin). `get_card_summary` elenca le giocate di tutti i piloti della gara, raggruppate per pilota. `cancel_play` porta una giocata attiva a `annullata` (resta nel registro) solo finché la gara non ha risultati. `grant_bonus` sposta una copia dalla pool all'inventario del pilota per correggere errori, senza creare notifiche; funziona su qualsiasi gara di un campionato attivo e dà 409 se la carta non è in pool o se il campionato è chiuso.

## Frontend

- Pagine: login, registrazione, home, team, dettaglio pilota, campionati, dettaglio campionato, dettaglio gara, elenco `/shop`, negozio del campionato, storico, pannello admin (utenti e ruoli, pool, campionati, nascosti, impostazioni generali, gestione negozio).
- Elenco `/shop`: un riquadro per campionato con i propri piloti e il saldo (oro e punti sponsor); un clic apre il negozio con quel pilota.
- Negozio (12d): in alto a destra il pilota con oro e punti sponsor; pulsanti Inventario (popup), Storico (pagina separata), scelta del pilota, impostazioni (admin). Aree modifiche (oro) e sponsor (punti sponsor), con ricerca per nome e ordinamento (`lib/shop-sort.ts`, test in `shop-sort.spec.ts`); le scelte non vengono salvate.
- Apertura dei pacchetti (`components/pack-reveal.svelte`, fasi in `lib/pack-reveal-phases.ts`): busta con l'immagine del pacchetto come texture, strappo della striscia, busta tagliata che scorre in basso, poi le carte una alla volta (un tocco, Invio o Spazio mostra la seguente). Dopo l'ultima, il tocco successivo apre il riepilogo: griglia con le carte ottenute, ciascuna con immagine ed etichetta "Modifica" o "Sponsor"; le copie uguali sono raggruppate con "x N" (`lib/pack-summary.ts`, funzione `groupByCard`, test in `pack-summary.spec.ts`), e il testo "Hai ottenuto N carte" conta tutte le estrazioni. "Salta" porta al riepilogo da qualsiasi fase.
- Chiusura della finestra di apertura: fino al riepilogo solo con la X; il tasto Esc e il clic fuori non chiudono (`modal.svelte` li gestisce con `closeOnOutside`, collegato a `done` di `pack-reveal.svelte`); dal riepilogo si chiude in ogni modo. Con il movimento ridotto del sistema si parte dalle carte.
- Admin del negozio (12e): pagina "Gestione negozio" (template di pacchetto e di negozio), scelta del template nella creazione del campionato, ingranaggio con pacchetti, pool completa e storico. Il pulsante "Storico" delle impostazioni, anche aperte dal negozio (`shopOnly`), mostra la cronologia completa di tutti i piloti (`championship-history-panel.svelte`, `fetchAllHistory`).
- Popup propri al posto di `dialog` e `confirm` nativi; impostazioni del campionato in un popup aperto dall'ingranaggio (solo admin).
- Modulo dei pacchetti: costo iniziale 10; cambiando valuta passa a 2 sponsor (e torna a 10 oro) solo se il costo non è stato modificato a mano.
- Pagina admin delle pool: «Ricarica» chiede l'anteprima e, se vanno tolte carte, apre un popup di conferma con i nomi e l'avviso "in uso in un campionato attivo".
- Dettaglio campionato: gare dalla più recente, con stato "in corso" o "terminata"; dettaglio gara con classifica, "Da assegnare" e "Non partecipano"; popup "Esci / Rimani" se si lascia una gara in corso non salvata.
- Carte sponsor in gara (13a e 13b): nessuna interfaccia ancora, arriva con la 13c (giocatore) e la 13d (giudice e admin).

## Qualità verificata

- CI su ogni pull request: test backend, controlli frontend con lint, test e build, migrazioni su un database creato da zero (upgrade, verifica, downgrade, nuovo upgrade). Sulla pull request #5 i tre controlli erano verdi sull'ultimo commit `24388ea` prima dell'unione in `main`.
- Pull request #9 (fase 13, per ora 13a e 13b): i tre controlli (test backend, migrazioni, frontend) sono verdi sul commit `f71cb19` (ultimo commit di codice della 13b), secondo l'elenco dei controlli letto il 2026-10-12. Erano verdi anche sui commit `a087855`, `c5c45e0` (modello e migrazione di `card_gift`) e `ede7aba` (tasto S). I test non sono stati eseguiti in locale da chi ha scritto il codice: l'esito viene dalla CI di GitHub.
- Test backend delle carte giocate (`backend/tests/test_card_plays.py`, 14 test): giocata e copie disponibili fino a esaurimento, inventario invariato durante la gara, carta inesistente, annullamento (copia liberata e registro conservato), annullamento senza giocate, cinque annullamenti e limite, azzeramento giocando una nuova carta, nessuna giocata a gara chiusa, pilota di un altro utente (404), pilota eliminato (404 in giocata e annullamento), consumo alla chiusura, annullate non consumate, ultima copia rimossa dall'inventario.
- Test backend del tasto S (`backend/tests/test_card_gifts.py`, 7 test): spostamento di una copia dalla pool all'inventario, riga nuova se la carta non era posseduta, pool vuota (409), nessuna gara in corso (409), pilota di un altro utente (404), carta regalata giocabile nella stessa gara, notifiche non viste elencate e poi segnate come viste (204).
- Test backend del giudice (`backend/tests/test_card_judge.py`, 6 test): riepilogo di tutti i piloti, giocatore escluso dal riepilogo (401 o 403, la dipendenza `JudgeUser` non è stata letta), annullamento del giudice (registro conservato, copia liberata), annullamento rifiutato due volte e a gara chiusa, bonus senza notifica, bonus per una carta fuori pool (409), giocata e tasto S bloccati in revisione con il bonus ancora possibile. Le funzioni di supporto sono ricopiate in ciascun file di test perché non si sa se `tests` sia un pacchetto importabile: duplicazione da ripulire.
- Non coperti dai test: correzione dei risultati da parte dell'admin dopo la chiusura (le carte non devono cambiare), campionato senza pool sponsor in chiusura, carta giocata sparita dall'inventario, campionato chiuso nella giocata, pilota non iscritto nel bonus, estrazione casuale con più carte diverse in pool. Da verificare se `test_race_review.py` ne copre alcuni.
- Test frontend del Negozio: 9 in `shop-sort.spec.ts`, 7 in `pack-reveal-phases.spec.ts`, 3 in `pack-summary.spec.ts`. Il componente grafico `pack-reveal.svelte` (taglio della busta, scorrimento, riepilogo) non ha test dedicati e si verifica a mano; l'autore ha verificato a mano riepilogo, elenco `/shop`, storico e storico completo dell'admin. Il numero totale di test non è stato aggiornato qui.
- Non hanno test dedicati: costo predefinito dei pacchetti, ordine delle gare, anteprima della ricarica, lock sul database. `cardDelayMs` in `pack-reveal-phases.ts` non è più usato dal componente ed è rimasto solo per il suo test.
- Non letti: `shop-api.ts` (si presume che `fetchAllHistory` chiami `GET .../shop/history/all`) e `shop-history-list.svelte` (non si sa se raggruppi per pilota).
- Migrazioni Alembic: oro per gara (`c9f3a1b6d8e4`), tabelle del Negozio (`a1c5e9b3d7f2`), unione delle teste (`b2d6f0a4c8e1`), tabella `card_play` (`c3e7a1d5b9f2`), stato "in revisione" (`d4f8b2e6a0c3`), tabella `card_gift` (`e7a3c9d1f5b2`). Dopo un'unione di teste `alembic downgrade -1` dà "Ambiguous walk": si usa la revisione precisa.
- Documenti ancora da riallineare (dopo la 13d, su richiesta dell'autore): `PROJECT_SPEC.md` (refuso "varà", righe su spareggio e carte sponsor rinviate, nuova sezione 14; nella sezione 14 vanno anche tolti l'annullamento con data e ora e la rimozione delle righe alla cancellazione di una gara, e aggiunte le migrazioni `c3e7a1d5b9f2`, `d4f8b2e6a0c3` ed `e7a3c9d1f5b2` alla tabella della sezione 11, più la tabella `card_gift`), `SHOP_DESIGN.md` e `PROJECT_NOTES.md` (descrivono ancora ogni estrazione come carta separata e Esc come non vincolato; `PROJECT_NOTES.md` non elenca ancora i file della 13a e della 13b). `PHASE_13_SPEC.md` non è stato riletto in questa sessione: da confrontare con la 13b (bonus senza notifica, annullamento del giudice).

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
| Revisione, riepilogo, correzione e bonus (giudice o admin) | `/api/championships/{id}/races/{race_id}` |
| Negozi dell'utente (campionati con pilota iscritto) | `/api/me` |
| Amministrazione e pulizia | `/api/admin` |
| Template e immagini del Negozio (admin) | `/api/shop` |
| Salute del servizio | `/health` |

Rotte del Negozio per il giocatore: `GET /{id}/shop?pilot_id=`, `POST /{id}/shop/purchases`, `GET /{id}/shop/inventory?pilot_id=`, `GET /{id}/shop/history`, `GET /{id}/shop/history/all` (solo admin). Elenco dei negozi dell'utente: `GET /api/me/shops`.

Rotte delle carte sponsor giocate (13a): `GET /{id}/card-plays?pilot_id=` (giocate, copie disponibili, annullamenti rimasti), `POST /{id}/card-plays` (giocata, 201), `POST /{id}/card-plays/undo` (annullamento). Errori: 404 campionato o pilota inesistenti o eliminati, 403 pilota non iscritto, 409 campionato chiuso, nessuna gara in corso, gara in revisione, carta non disponibile, niente da annullare, limite di 5 annullamenti.

Rotte del tasto S (13b, giocatore): `POST /{id}/card-gifts` (corpo `pilot_id`, 201 con la carta ottenuta), `GET /{id}/card-gifts?pilot_id=` (notifiche non viste), `POST /{id}/card-gifts/seen` (corpo `pilot_id`, 204). Errori: 404 campionato o pilota, 403 pilota non iscritto, 409 campionato chiuso, nessuna gara in corso, gara in revisione, pool sponsor vuota.

Rotte della revisione, del riepilogo e della correzione (13b, giudice o admin): `POST` e `DELETE /{id}/races/{race_id}/review` (apre e chiude la revisione), `GET /{id}/races/{race_id}/card-plays` (riepilogo per pilota), `POST /{id}/races/{race_id}/card-plays/{play_id}/cancel` (annulla una giocata attiva), `POST /{id}/races/{race_id}/card-bonus` (corpo `pilot_id` e `card_name`, 201, senza notifica). Errori: 404 campionato, gara, pilota o giocata inesistenti, 403 pilota non iscritto, 409 campionato chiuso, gara già chiusa, giocata non più attiva, carta non in pool.

## Decisioni e questioni aperte

Decisioni dell'autore (2026-10-08): tetto di 100 copie per carta (409); l'admin con un pilota iscritto è un normale giocatore, con in più il tasto delle impostazioni del negozio; un pilota eliminato non può comprare durante un campionato attivo; il giocatore non vede lo storico di un pilota eliminato.

Decisioni dell'autore (2026-10-10): la 12c è approvata; la ricarica delle pool chiede conferma elencando le carte da togliere; per il deploy online gli acquisti si serializzano con un blocco sul database; la pool sponsor è usata dai pacchetti; i pacchetti nuovi costano 10 oro o 2 sponsor; lo storico resta una pagina separata e l'inventario un solo pulsante.

Decisioni dell'autore (2026-10-11): la busta usa come texture l'immagine del pacchetto acquistato; la striscia strappata se ne va e la busta resta tagliata; le carte si vedono una alla volta e ogni tocco le fa scorrere a sinistra; alla fine compare un riepilogo con tutte le carte; "Salta" porta al riepilogo; fino al riepilogo la finestra si chiude solo con la X, dal riepilogo in ogni modo. Le copie uguali nel riepilogo sono raggruppate con il numero di copie; Esc non chiude prima del riepilogo. L'elenco `/shop` e lo storico sono considerati a posto, come lo storico completo dell'admin dalle impostazioni del negozio. La pull request #5 è stata unita in `main` (merge `6dd5619`).

Decisioni dell'autore (2026-10-12): lo spareggio sportivo non serve; le pool di base esistono e funzionano; l'uso online è rinviato a dopo la fase 14; la fase 13 realizza le carte sponsor in gara (uso con conferma, annullamento fino a 5, stato "in revisione", tasto S, restituzione alla pool alla chiusura) e l'amministrazione delle carte (caricamento con ritaglio e zoom, nome e quantità, nomi in arancione, esclusione di caricate o di base nelle pool personalizzate); la fase 14 è di sistemazione generale e miglioramenti; i documenti si riallineano dopo la 13d, ma le correzioni rese necessarie da un cambiamento si fanno subito. I dettagli sono in `PHASE_13_SPEC.md`. La pull request #9 raccoglie tutta la fase 13 e non solo la 13a. Gli annullamenti consecutivi si calcolano dal registro, senza colonna dedicata (`cancelled_at` non si aggiunge). Le gare non si eliminano a mano. Il bonus che il giudice dà alla fine non crea notifiche e serve solo a correggere errori; la notifica "Hai ottenuto una carta sponsor" nasce solo dal tasto S.

Scelte della 13a da confermare (dell'assistente, non ancora approvate): il consumo alla chiusura sta in un modulo separato (`card_play_close.py`) per evitare un import circolare; con una pool sponsor assente le carte consumate non tornano in nessuna pool.

Scelte della 13b da confermare (dell'assistente, non ancora approvate): il tasto S estrae con probabilità proporzionale alle copie in pool; l'annullamento della giocata da parte del giudice usa lo stato `annullata`, quindi il conteggio degli annullamenti consecutivi non distingue chi ha annullato e può ridurre quelli rimasti al giocatore (per evitarlo serve un nuovo stato o una colonna); il bonus non si dà a campionato chiuso; `services/card_gift.py` e `services/card_judge.py` importano funzioni private (`_authorize`, `_ensure_not_in_review`, `_open_race`, `_lock_database`) da altri servizi.

Correzione del 2026-10-10: una versione precedente di questo file e di `SHOP_SCHEMA.md` dava per non necessaria `GET /api/me/shops`; la rotta esiste ed è usata dal frontend.

Questioni rinviate:

- Per il deploy online: un solo server con pochi worker, perché SQLite accetta una sola scrittura alla volta; con un altro database serve un blocco sulla riga del pilota (`SELECT ... FOR UPDATE`).

## Documenti

- `PROJECT_SPEC.md`: specifiche funzionali (fonte delle regole).
- `PROJECT_NOTES.md`: mappa del codice, comandi, convenzioni e contesto di lavoro.
- `OPEN_QUESTIONS.md`: decisioni ancora rinviate.
- `PHASE_13_SPEC.md`: decisioni e sottofasi della fase 13 (carte sponsor e amministrazione delle carte).
- `SHOP_DESIGN.md`: funzionamento del Negozio spiegato dall'autore.
- `SHOP_SCHEMA.md`: schema, servizi, rotte e sottofasi del Negozio.
- Documenti storici (fotografie di una fase): `DATABASE_ANALYSIS.md`, `BACKEND_BOOTSTRAP.md`, `BACKEND_AUTH.md`, `FRONTEND_BOOTSTRAP.md`, `FRONTEND_AUTH.md`.

## Prossimi passi

1. Fase 13c nel ramo `phase-13a-card-plays` (frontend giocatore: sezioni per pilota, uso delle carte, Indietro, inventario in due sezioni, popup "Hai ottenuto una carta sponsor"), con l'elenco dei file da approvare prima di iniziare.
2. Proseguire con 13d, 13e, 13f e 13g nella stessa pull request #9; uscita dalla bozza e unione in `main` solo alla 13g, a cura dell'autore.
3. Unione del ramo `phase-12f-docs` (solo documenti) in `main`, a cura dell'autore.
4. Dopo la 13d: riallineamento di tutti i documenti, correzione del refuso "varà" e nuova sezione 14 in `PROJECT_SPEC.md`, con le correzioni elencate sopra.
