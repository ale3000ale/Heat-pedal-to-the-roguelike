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
| 12b | Template di pacchetto e di negozio, pacchetti del campionato, creazione del campionato con template | Completata (12b-1, 12b-2, 12b-3) |
| 12c | Estrazione, acquisto, storico e riepilogo inventario (backend) | Completata e approvata (12c-1, 12c-2) |
| 12d-12f | Frontend giocatore, frontend admin, documenti | In corso: la pagina del negozio ha ordinamento, ricerca per nome, saldo in alto a destra e l'apertura animata dei pacchetti con taglio della busta e carte mostrate una alla volta; restano da verificare a mano l'aspetto dell'animazione e le altre pagine sottofase per sottofase |

## Backend

- FastAPI, SQLAlchemy 2.0, Alembic e SQLite in `backend/`.
- Autenticazione con password hashate e cookie di sessione httpOnly.
- Ruoli `admin`, `judge` e `player`; registrazione libera e primo admin creato con setup.
- Team e piloti con nomi unici senza distinguere maiuscole, rinomina ed eliminazione logica.
- Un pilota può non avere un team, ma deve averne uno per iscriversi a un campionato.
- Ogni pilota possiede tre mazzi indipendenti: inventario delle modifiche, inventario sponsor (vuoto alla creazione) e mazzo da gioco; i mazzi hanno un numero di versione (blocco ottimistico, 409 in caso di conflitto).
- Elenco piloti paginato (`limit`/`offset`), con ricerca per nome, filtro per team e campionato attivo accanto a ogni pilota.
- Gestione e validazione delle carte JSON, inclusa la preparazione e il ridimensionamento delle immagini; rinomina delle carte nelle pool.
- Immagini dei pacchetti (`services/pack_images.py`): caricamento di png, jpg/jpeg e webp fino a 5 MB, conversione in WebP dentro la scatola 560x870 px, elenco delle immagini (predefinita in `media/pack/defaultIllustration`, caricamenti in `media/pack/illustration`), controllo dei percorsi.
- Script `python -m app.scripts.resize_cards`: porta in WebP, dentro la scatola massima, le immagini di `media/cards` e `media/pack`; idempotente, non cancella gli originali, con `--dry-run`.
- Due pool di base (modifiche `default` e sponsor `sponsor`), pool derivate create dall'admin, due copie di pool per ogni campionato.
- Ricarica delle pool di base: aggiunge le carte nuove e toglie dal database quelle il cui file non esiste più (se la cartella è vuota o manca non toglie nulla). Prima della ricarica l'admin vede un'anteprima, `GET /api/pools/base/{kind}/reload/preview`, che non scrive nulla ed elenca le carte da togliere indicando se sono nella copia di pool di un campionato attivo; `POST /api/pools/base/{kind}/reload` applica la ricarica. Le copie di pool dei campionati già creati non cambiano.
- Iscrizione ai campionati con reset di inventario (iniziale), inventario sponsor (vuoto), mazzo da gioco, gold, sponsor e punti; il reset dei piloti iscritti si ripete alla chiusura del campionato.
- Gare numerate automaticamente, datate alla creazione; una sola gara in corso per campionato (errore se se ne crea un'altra). L'elenco delle gare nell'API resta in ordine di numero; la pagina del campionato le mostra dalla più recente (data decrescente, poi numero decrescente).
- Chiusura della gara con ordine di arrivo, punti sponsor e lista esplicita degli assenti; correzione dei risultati solo per l'admin; punti 9-6-4-3-2-1, poi 0.
- Oro per gara: regole per campionato (base più modificatore per posizione 1-6 e per "altre"), copiate dalle impostazioni generali alla creazione del campionato e assegnate a tutti gli iscritti alla prima chiusura di ogni gara.
- Classifica live per i campionati attivi e classifica congelata per quelli chiusi.
- Cancellazione di un campionato chiuso con gare, risultati, iscrizioni, classifica finale e copia delle pool.
- Admin: gestione degli elementi nascosti, eliminazione definitiva manuale e pulizia automatica dopo 365 giorni.
- Negozio, parte admin (12b): template di pacchetto e di negozio, rotte delle immagini, pacchetti del campionato, creazione del campionato con un template, cancellazione di pacchetti e storico insieme al campionato. Un pacchetto senza valuta e senza costo vale 10 oro; se la valuta è gli sponsor e il costo manca vale 2 sponsor. I pacchetti già creati non cambiano.
- Negozio, estrazione e acquisto (12c-1): `services/shop_draw.py` (una carta alla volta, probabilità per copia ricalcolata dopo ogni estrazione, filtro per nome senza distinguere le maiuscole, "terminato" se una pool ha meno copie estraibili di quelle richieste) e `services/shop_purchase.py` (controlli, saldo, estrazione, pool, inventari e storico in un solo commit; un acquisto alla volta; tetto di 100 copie per carta nell'inventario, con errore 409). Le carte sponsor di un pacchetto (`sponsor_count`) sono estratte dalla copia della pool sponsor del campionato.
- Serializzazione degli acquisti: lock di processo più `BEGIN IMMEDIATE` su SQLite (`_lock_database`), così due acquisti di processi o worker diversi non consumano la stessa copia. Con un database diverso da SQLite il blocco sul database non è attivo.
- Negozio, accesso e vista (12c-1): `services/shop_view.py`. Il giocatore entra con un proprio pilota iscritto e solo a campionato attivo; l'admin entra sempre, in sola lettura senza pilota o a campionato chiuso; l'admin con un pilota iscritto si comporta come un giocatore. Con una gara in corso gli acquisti sono bloccati.
- Negozio, elenco dei negozi dell'utente: `GET /api/me/shops` (`api/shop_me.py`, `services/shop_list.py`, `schemas/shop_list.py`) restituisce i campionati attivi a cui l'utente partecipa con un pilota, con i piloti iscritti; serve alla voce "Negozio" della barra di navigazione e alla scelta del pilota.
- Negozio, storico e inventario (12c-2): `services/shop_history.py` (storico dei propri piloti, cronologia completa per l'admin, raggruppamento per pilota) e `services/shop_inventory.py` (inventari modifiche e sponsor senza Velocità 1-4). Il giocatore non vede gli acquisti di un pilota che ha eliminato; l'admin sì.

## Frontend

- Pagine: login, registrazione, home, team (con ricerca e filtro piloti), dettaglio pilota (carte cliccabili tra inventario e mazzo da gioco), campionati, dettaglio campionato, dettaglio gara, negozio del campionato, pannello admin (utenti e ruoli, pool, campionati, nascosti, impostazioni generali, negozio).
- Pagina del negozio (12d): in alto a destra il pilota scelto con oro e punti sponsor, sotto i pulsanti Inventario (popup), Storico (pagina separata), scelta del pilota e impostazioni (admin). Due pulsanti scelgono l'area modifiche (pacchetti in oro) o sponsor (punti sponsor). In ogni area una barra cerca i pacchetti per nome e un menu li ordina (predefinito dal meno caro al più caro, poi dal più caro, alfabetico, alfabetico inverso); ricerca e ordinamento sono scelte del giocatore e non vengono salvate. La logica sta in `frontend/src/lib/shop-sort.ts` con test in `shop-sort.spec.ts`.
- Apertura animata dei pacchetti (12d): `components/pack-reveal.svelte`, con fasi e tempi in `lib/pack-reveal-phases.ts` (test in `pack-reveal-phases.spec.ts`). La busta ha come texture l'immagine del pacchetto acquistato; la striscia in alto si stacca e se ne va, e la busta resta tagliata in alto (la parte alta, il 14%, viene tolta con un bordo leggermente irregolare tramite `clip-path`; l'ombra segue la forma con `drop-shadow`); poi la busta tagliata scorre verso il basso. Le carte escono una alla volta, già scoperte: la prima compare al centro e ogni tocco (o Invio, o Spazio) la fa scorrere a sinistra mostrando la seguente; sull'ultima il tocco non fa nulla. Sotto la carta c'è il contatore "Carta N di M" e il tasto "Salta", che durante la busta salta le animazioni e durante le carte porta all'ultima; con il movimento ridotto del sistema si parte direttamente dalle carte e lo scorrimento dura 0. `components/modal.svelte` ha le opzioni `blur` (sfondo sfocato) e `wide` (finestra più larga), spente di default.
- Popup propri al posto di `dialog` e `confirm` nativi; impostazioni del campionato in un popup aperto dall'ingranaggio (solo admin). Nel negozio lo stesso popup si apre in modalità "solo negozio" (`shopOnly`): mostra soltanto pacchetti, pool completa e storico, senza oro per gara e senza chiusura o eliminazione del campionato.
- Pool completa: le miniature delle carte usano il prefisso `/media/` come le altre carte.
- Pagina admin delle pool: «Ricarica» chiede l'anteprima e, se vanno tolte carte, apre un popup di conferma con i nomi delle carte e l'avviso "in uso in un campionato attivo"; senza carte da togliere la ricarica parte subito.
- Modulo dei pacchetti: costo iniziale 10; cambiando valuta passa a 2 sponsor (e torna a 10 oro) solo se il costo non è stato modificato a mano.
- Dettaglio campionato: gare dalla più recente, con stato "in corso" (rosso) o "terminata" (verde); "Nuova gara" resta premibile ma con una gara in corso mostra solo l'avviso.
- Dettaglio gara: classifica, elenco "Da assegnare" e "Non partecipano"; "Termina" attivo solo con almeno un pilota in classifica e tutti gli iscritti assegnati; popup "Esci / Rimani" se si lascia una gara in corso con classifica non salvata.

## Qualità verificata

- CI su ogni pull request (pull request #5, in bozza): test backend, controlli frontend con build, migrazioni su un database di test creato da zero (upgrade, verifica di tabelle, colonne e indici, downgrade, nuovo upgrade). L'11 ottobre i tre controlli (backend, frontend, migrazioni) sono risultati verdi dopo il commit che taglia la busta dopo lo strappo (`707df16`); l'orario di avvio dei controlli coincide con quel commit. Gli stessi controlli erano verdi anche dopo il commit dell'apertura animata e dopo quelli di ordinamento, ricerca e posizione del saldo (il 10 ottobre una prima esecuzione frontend aveva segnalato un problema di formattazione Prettier in `shop-sort.ts`, corretto subito).
- Carte una alla volta (11 ottobre): `pack-reveal.svelte` è stato riscritto (commit `0cd0fee`) perché mostrava tutte le carte coperte in fila, contro `SHOP_DESIGN.md`. La prima esecuzione di `npm run lint` ha segnalato un problema di formattazione Prettier nello stesso file (riga troppo lunga), corretto nel commit `c83b114`. L'autore ha poi detto che gli sembra tutto a posto; l'esito della CI sui due commit non è stato letto da chi scrive il codice.
- Test nuovi: 9 test per ordinamento e ricerca dei pacchetti (`shop-sort.spec.ts`) e 7 test sulle fasi dell'animazione di apertura (`pack-reveal-phases.spec.ts`). Non sono stati scritti test nuovi per il costo predefinito dei pacchetti e per l'ordine delle gare (scelta dell'autore). L'anteprima della ricarica, il lock sul database e il componente grafico `pack-reveal.svelte` (compreso il taglio della busta, che è solo CSS, e lo scorrimento delle carte) non hanno test dedicati; il numero totale di test non è stato aggiornato qui. `cardDelayMs` in `pack-reveal-phases.ts` non è più usato dal componente ed è rimasto solo per il suo test.
- Aspetto dell'animazione: non verificabile da CI. L'autore ha detto che, salvo segnalazioni, va considerata a posto; il taglio della busta dopo lo strappo è stato scritto su sua richiesta e non è stato visto a schermo da chi ha scritto il codice. Restano non letti `CardTile.svelte` dentro la carta mostrata e i nomi delle variabili CSS del tema (`--muted`, `--border`, `--primary`), usati senza controllo.
- Migrazioni Alembic: oro per gara (`c9f3a1b6d8e4`), tabelle del Negozio (`a1c5e9b3d7f2`) e unione delle due teste (`b2d6f0a4c8e1`), oltre a quelle elencate nella sezione 11 della specifica. Dopo un'unione di teste, `alembic downgrade -1` dà "Ambiguous walk": si usa la revisione precisa.
- Documenti: gli interventi di sola documentazione dell'11 ottobre (`SHOP_DESIGN.md`, `SHOP_SCHEMA.md`, `OPEN_QUESTIONS.md`, `PROJECT_SPEC.md`, questo file) non hanno test da eseguire; per `PROJECT_SPEC.md` il file è stato riscritto per intero, da ricontrollare nel diff.

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

Rotte del Negozio per il giocatore (12c): `GET /{id}/shop?pilot_id=`, `POST /{id}/shop/purchases`, `GET /{id}/shop/inventory?pilot_id=`, `GET /{id}/shop/history`, `GET /{id}/shop/history/all` (solo admin). Elenco dei negozi dell'utente: `GET /api/me/shops`.

## Decisioni e questioni aperte

Decisioni dell'autore (2026-10-08): tetto di 100 copie per carta, rifiuto dell'acquisto con 409; l'admin con un pilota iscritto è un normale giocatore, con in più il tasto delle impostazioni del negozio; durante un campionato attivo un pilota eliminato non può comprare; il giocatore non vede lo storico di un pilota eliminato.

Decisioni dell'autore (2026-10-10): la 12c è approvata; la ricarica delle pool chiede conferma elencando le carte da togliere, con l'indicazione "presente nella copia di pool di un campionato attivo"; per il deploy online gli acquisti si serializzano con un blocco sul database; la pool sponsor è usata dai pacchetti; i pacchetti nuovi costano 10 oro o 2 sponsor; nel negozio lo storico resta una pagina separata e l'inventario un solo pulsante (invece del popup con sezioni espandibili e del pulsante in ogni area previsti in `SHOP_DESIGN.md`).

Decisioni dell'autore (2026-10-11): nell'apertura del pacchetto la busta usa come texture l'immagine del pacchetto acquistato (non una busta grafica uguale per tutti); la striscia strappata se ne va e sotto resta la busta senza la parte alta; dopo la busta le carte si vedono una alla volta e ogni tocco la fa scorrere a sinistra (come in `SHOP_DESIGN.md`, sezione 6), non in fila e coperte.

Correzione del 2026-10-10: una versione precedente di questo file e di `SHOP_SCHEMA.md` diceva che l'elenco dei campionati con negozio (`GET /api/me/shops`) non serviva. La rotta invece esiste nel backend (`shop_me.py`, montata con prefisso `/api/me` in `main.py`) ed è usata dal frontend; i documenti sono stati corretti dopo la lettura del codice.

Questioni aperte:

- Per il deploy: un solo server con pochi worker, perché SQLite accetta una sola scrittura alla volta; con un altro database serve un blocco sulla riga del pilota (`SELECT ... FOR UPDATE`).
- Avviso quando un template di negozio non contiene pacchetti (da riportare in `SHOP_SCHEMA.md` a fine 12c).
- Verifica sottofase per sottofase del frontend del Negozio (12d, 12e) rispetto a `SHOP_SCHEMA.md`; per la 12d restano l'elenco `/shop` e la pagina dello storico, non ancora letti.
- Blocco della finestra durante l'apertura: la vecchia descrizione in `SHOP_SCHEMA.md` diceva che la finestra restava bloccata finché le carte non erano girate; con le carte una alla volta non è deciso se vada mantenuto (da chiedere all'autore o da verificare in `pack-reveal.svelte`).

## Documenti

- `PROJECT_SPEC.md`: specifiche funzionali (fonte delle regole).
- `PROJECT_NOTES.md`: mappa del codice, comandi, convenzioni e contesto di lavoro.
- `OPEN_QUESTIONS.md`: decisioni ancora rinviate.
- `SHOP_DESIGN.md`: funzionamento del Negozio spiegato dall'autore.
- `SHOP_SCHEMA.md`: schema, servizi, rotte e sottofasi del Negozio.
- Documenti storici (fotografie di una fase, non lo stato attuale): `DATABASE_ANALYSIS.md`, `BACKEND_BOOTSTRAP.md`, `BACKEND_AUTH.md`, `FRONTEND_BOOTSTRAP.md`, `FRONTEND_AUTH.md`.

## Prossimi passi

1. Allineare `PROJECT_NOTES.md` sull'apertura animata dei pacchetti (busta con l'immagine come texture, striscia che se ne va, busta tagliata, carte una alla volta che scorrono a sinistra): `PROJECT_SPEC.md`, `SHOP_SCHEMA.md`, `OPEN_QUESTIONS.md` e questo file sono già aggiornati. Il file `SHOP_DESIGN.md` descrive già le carte una alla volta.
2. Sottofase 12d: verificare le altre pagine del negozio (elenco `/shop`, pagina dello storico, popup di inventario) e, se l'autore lo segnala, correggere l'aspetto dell'animazione.
3. Sottofase 12e: frontend admin (impostazioni del negozio, pacchetti, template, cronologia).
4. Sottofase 12f: documenti finali e verifica complessiva, poi unione di `phase-12-shop` in `main`.
