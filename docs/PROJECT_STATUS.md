# Stato del progetto — Heat

Ultimo aggiornamento: 2026-10-11

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
| 12 | Negozio e pacchetti di carte | In corso sul ramo `phase-12-shop` (sottofasi in `SHOP_SCHEMA.md`) |
| 12a | Tabelle del Negozio, inventario sponsor del pilota e reset, servizio e script delle immagini | Completata |
| 12b | Template di pacchetto e di negozio, pacchetti del campionato, creazione del campionato con template | Completata |
| 12c | Estrazione, acquisto, storico e riepilogo inventario (backend) | Completata e approvata |
| 12d | Frontend giocatore: elenco `/shop`, negozio con ordinamento e ricerca, inventario, storico, apertura animata dei pacchetti, riepilogo finale con copie raggruppate | Completata (verifica a mano dell'autore) |
| 12e | Frontend admin: gestione negozio, template, pacchetti del campionato, storico completo di tutti i piloti dalle impostazioni del negozio | Completata (verifica a mano dell'autore) |
| 12f | Documenti finali, verifica complessiva, unione di `phase-12-shop` in `main` | In corso |

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
- Gare numerate automaticamente; una sola gara in corso per campionato. Chiusura con ordine di arrivo, punti sponsor e assenti espliciti; correzione dei risultati solo per l'admin; punti 9-6-4-3-2-1, poi 0.
- Oro per gara: regole per campionato (base più modificatore per posizione 1-6 e per "altre"), copiate dalle impostazioni generali alla creazione e assegnate a tutti gli iscritti alla prima chiusura di ogni gara.
- Classifica live per i campionati attivi, congelata per quelli chiusi; cancellazione di un campionato chiuso con tutti i suoi dati.
- Admin: gestione degli elementi nascosti, eliminazione definitiva manuale e pulizia automatica dopo 365 giorni.
- Negozio, parte admin (12b): template di pacchetto e di negozio, rotte delle immagini, pacchetti del campionato, creazione del campionato con template. Un pacchetto senza valuta e senza costo vale 10 oro; con valuta sponsor e costo mancante vale 2 sponsor.
- Negozio, estrazione e acquisto (12c-1): `services/shop_draw.py` (una carta alla volta, probabilità per copia ricalcolata dopo ogni estrazione, filtro per nome, "terminato") e `services/shop_purchase.py` (controlli, saldo, estrazione, pool, inventari e storico in un solo commit; tetto di 100 copie per carta con errore 409). Serializzazione con lock di processo più `BEGIN IMMEDIATE` su SQLite (`_lock_database`); con altri database il blocco non è attivo.
- Negozio, accesso e vista (`services/shop_view.py`): il giocatore entra con un proprio pilota iscritto e solo a campionato attivo; l'admin entra sempre (sola lettura senza pilota o a campionato chiuso, come un giocatore con un pilota iscritto). Con una gara in corso gli acquisti sono bloccati.
- Negozio, elenco dei negozi dell'utente: `GET /api/me/shops` (`api/shop_me.py`, `services/shop_list.py`).
- Negozio, storico e inventario (12c-2): `services/shop_history.py` e `services/shop_inventory.py`. Il giocatore non vede gli acquisti di un pilota che ha eliminato; l'admin sì.

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

## Qualità verificata

- CI su ogni pull request (pull request #5, in bozza): test backend, controlli frontend con lint, test e build, migrazioni su un database creato da zero (upgrade, verifica, downgrade, nuovo upgrade). Sono stati letti come verdi gli esiti fino al commit `ccf23e8` (riepilogo finale).
- Commit successivi: `06ac748` (copie raggruppate nel riepilogo) ha fatto segnalare a `npm run lint` un problema di formato Prettier in `pack-summary.spec.ts`, corretto in `58ca7d3`; l'autore ha confermato che ora è a posto. Gli esiti della CI di questi due commit non sono stati letti.
- Test frontend del Negozio: 9 in `shop-sort.spec.ts`, 7 in `pack-reveal-phases.spec.ts`, 3 in `pack-summary.spec.ts`. Il componente grafico `pack-reveal.svelte` (taglio della busta, scorrimento, riepilogo) non ha test dedicati e si verifica a mano; l'autore ha verificato a mano riepilogo, elenco `/shop`, storico e storico completo dell'admin. Il numero totale di test non è stato aggiornato qui.
- Non hanno test dedicati: costo predefinito dei pacchetti, ordine delle gare, anteprima della ricarica, lock sul database. `cardDelayMs` in `pack-reveal-phases.ts` non è più usato dal componente ed è rimasto solo per il suo test.
- Non letti: `shop-api.ts` (si presume che `fetchAllHistory` chiami `GET .../shop/history/all`) e `shop-history-list.svelte` (non si sa se raggruppi per pilota).
- Migrazioni Alembic: oro per gara (`c9f3a1b6d8e4`), tabelle del Negozio (`a1c5e9b3d7f2`), unione delle teste (`b2d6f0a4c8e1`). Dopo un'unione di teste `alembic downgrade -1` dà "Ambiguous walk": si usa la revisione precisa.
- Documenti: `PROJECT_STATUS.md` e `SHOP_SCHEMA.md` sono riallineati dopo 12d e 12e. Restano da riallineare `PROJECT_SPEC.md`, `SHOP_DESIGN.md`, `PROJECT_NOTES.md` e `OPEN_QUESTIONS.md`, che descrivono ancora ogni estrazione come carta separata.

## API principali

| Area | Prefisso |
|---|---|
| Autenticazione | `/api/auth` |
| Team | `/api/teams` |
| Piloti | `/api/pilots` |
| Pool (anche anteprima e ricarica) | `/api/pools` |
| Campionati, iscrizioni, gare e classifica | `/api/championships` |
| Negozio del giocatore (vista, acquisto, inventario, storico) | `/api/championships/{id}/shop` |
| Negozi dell'utente (campionati con pilota iscritto) | `/api/me` |
| Amministrazione e pulizia | `/api/admin` |
| Template e immagini del Negozio (admin) | `/api/shop` |
| Salute del servizio | `/health` |

Rotte del Negozio per il giocatore: `GET /{id}/shop?pilot_id=`, `POST /{id}/shop/purchases`, `GET /{id}/shop/inventory?pilot_id=`, `GET /{id}/shop/history`, `GET /{id}/shop/history/all` (solo admin). Elenco dei negozi dell'utente: `GET /api/me/shops`.

## Decisioni e questioni aperte

Decisioni dell'autore (2026-10-08): tetto di 100 copie per carta (409); l'admin con un pilota iscritto è un normale giocatore, con in più il tasto delle impostazioni del negozio; un pilota eliminato non può comprare durante un campionato attivo; il giocatore non vede lo storico di un pilota eliminato.

Decisioni dell'autore (2026-10-10): la 12c è approvata; la ricarica delle pool chiede conferma elencando le carte da togliere; per il deploy online gli acquisti si serializzano con un blocco sul database; la pool sponsor è usata dai pacchetti; i pacchetti nuovi costano 10 oro o 2 sponsor; lo storico resta una pagina separata e l'inventario un solo pulsante.

Decisioni dell'autore (2026-10-11): la busta usa come texture l'immagine del pacchetto acquistato; la striscia strappata se ne va e la busta resta tagliata; le carte si vedono una alla volta e ogni tocco le fa scorrere a sinistra; alla fine compare un riepilogo con tutte le carte; "Salta" porta al riepilogo; fino al riepilogo la finestra si chiude solo con la X, dal riepilogo in ogni modo. Le copie uguali nel riepilogo sono raggruppate con il numero di copie; Esc non chiude prima del riepilogo. L'elenco `/shop` e lo storico sono considerati a posto, come lo storico completo dell'admin dalle impostazioni del negozio.

Correzione del 2026-10-10: una versione precedente di questo file e di `SHOP_SCHEMA.md` dava per non necessaria `GET /api/me/shops`; la rotta esiste ed è usata dal frontend.

Questioni aperte:

- Per il deploy: un solo server con pochi worker, perché SQLite accetta una sola scrittura alla volta; con un altro database serve un blocco sulla riga del pilota (`SELECT ... FOR UPDATE`).
- Avviso quando un template di negozio non contiene pacchetti (da riportare in `SHOP_SCHEMA.md` a fine 12c).

## Documenti

- `PROJECT_SPEC.md`: specifiche funzionali (fonte delle regole).
- `PROJECT_NOTES.md`: mappa del codice, comandi, convenzioni e contesto di lavoro.
- `OPEN_QUESTIONS.md`: decisioni ancora rinviate.
- `SHOP_DESIGN.md`: funzionamento del Negozio spiegato dall'autore.
- `SHOP_SCHEMA.md`: schema, servizi, rotte e sottofasi del Negozio.
- Documenti storici (fotografie di una fase): `DATABASE_ANALYSIS.md`, `BACKEND_BOOTSTRAP.md`, `BACKEND_AUTH.md`, `FRONTEND_BOOTSTRAP.md`, `FRONTEND_AUTH.md`.

## Prossimi passi

1. Sottofase 12f: riallineare `PROJECT_SPEC.md`, `SHOP_DESIGN.md`, `PROJECT_NOTES.md` e `OPEN_QUESTIONS.md` (copie raggruppate, Esc, 12d e 12e chiuse).
2. Leggere gli esiti della CI della pull request #5 sugli ultimi commit e fare la verifica complessiva.
3. Togliere la bozza dalla pull request #5 e unire `phase-12-shop` in `main`.
