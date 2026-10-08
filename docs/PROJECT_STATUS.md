# Stato del progetto — Heat

Ultimo aggiornamento: 2026-10-08

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
| 12c | Estrazione, acquisto, storico e riepilogo inventario (backend) | Completata sul backend (12c-1, 12c-2); in attesa di approvazione |
| 12d-12f | Frontend giocatore, frontend admin, documenti | Da iniziare |

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
- Due pool di base (modifiche `default` e sponsor `sponsor`) con ricarica che aggiunge soltanto, pool derivate create dall'admin, due copie di pool per ogni campionato.
- Iscrizione ai campionati con reset di inventario (iniziale), inventario sponsor (vuoto), mazzo da gioco, gold, sponsor e punti; il reset dei piloti iscritti si ripete alla chiusura del campionato.
- Gare numerate automaticamente, datate alla creazione; una sola gara in corso per campionato (errore se se ne crea un'altra).
- Chiusura della gara con ordine di arrivo, punti sponsor e lista esplicita degli assenti; correzione dei risultati solo per l'admin; punti 9-6-4-3-2-1, poi 0.
- Oro per gara: regole per campionato (base più modificatore per posizione 1-6 e per "altre"), copiate dalle impostazioni generali alla creazione del campionato e assegnate a tutti gli iscritti alla prima chiusura di ogni gara.
- Classifica live per i campionati attivi e classifica congelata per quelli chiusi.
- Cancellazione di un campionato chiuso con gare, risultati, iscrizioni, classifica finale e copia delle pool.
- Admin: gestione degli elementi nascosti, eliminazione definitiva manuale e pulizia automatica dopo 365 giorni.
- Negozio, parte admin (12b): template di pacchetto e di negozio, rotte delle immagini, pacchetti del campionato, creazione del campionato con un template, cancellazione di pacchetti e storico insieme al campionato.
- Negozio, estrazione e acquisto (12c-1): `services/shop_draw.py` (una carta alla volta, probabilità per copia ricalcolata dopo ogni estrazione, filtro per nome senza distinguere le maiuscole, "terminato" se una pool ha meno copie estraibili di quelle richieste) e `services/shop_purchase.py` (controlli, saldo, estrazione, pool, inventari e storico in un solo commit; un acquisto alla volta con un lock di processo; tetto di 100 copie per carta nell'inventario, con errore 409).
- Negozio, accesso e vista (12c-1): `services/shop_view.py`. Il giocatore entra con un proprio pilota iscritto e solo a campionato attivo; l'admin entra sempre, in sola lettura senza pilota o a campionato chiuso; l'admin con un pilota iscritto si comporta come un giocatore. Con una gara in corso gli acquisti sono bloccati.
- Negozio, storico e inventario (12c-2): `services/shop_history.py` (storico dei propri piloti, cronologia completa per l'admin, raggruppamento per pilota) e `services/shop_inventory.py` (inventari modifiche e sponsor senza Velocità 1-4). Il giocatore non vede gli acquisti di un pilota che ha eliminato; l'admin sì.

## Frontend

- Pagine: login, registrazione, home, team (con ricerca e filtro piloti), dettaglio pilota (carte cliccabili tra inventario e mazzo da gioco), campionati, dettaglio campionato, dettaglio gara, pannello admin (utenti e ruoli, pool, campionati, nascosti, impostazioni generali).
- Popup propri al posto di `dialog` e `confirm` nativi; impostazioni del campionato in un popup aperto dall'ingranaggio (solo admin).
- Dettaglio campionato: gare con stato "in corso" (rosso) o "terminata" (verde); "Nuova gara" resta premibile ma con una gara in corso mostra solo l'avviso.
- Dettaglio gara: classifica, elenco "Da assegnare" e "Non partecipano"; "Termina" attivo solo con almeno un pilota in classifica e tutti gli iscritti assegnati; popup "Esci / Rimani" se si lascia una gara in corso con classifica non salvata.
- Il Negozio non ha ancora pagine (previste nelle sottofasi 12d e 12e).

## Qualità verificata

- CI su ogni pull request (pull request #5, in bozza): test backend, controlli frontend con build, migrazioni su un database di test creato da zero (upgrade, verifica di tabelle, colonne e indici, downgrade, nuovo upgrade). Letti dai check sul commit `898771c`: Backend (pytest), Frontend e Migrazioni tutti in successo.
- I test delle rotte del Negozio (`tests/test_shop_routes.py`) sono nel commit di questo aggiornamento: l'esito va letto dai check di quel commit. Il numero totale di test non è stato aggiornato qui.
- Migrazioni Alembic: oro per gara (`c9f3a1b6d8e4`), tabelle del Negozio (`a1c5e9b3d7f2`) e unione delle due teste (`b2d6f0a4c8e1`), oltre a quelle elencate nella sezione 11 della specifica. Dopo un'unione di teste, `alembic downgrade -1` dà "Ambiguous walk": si usa la revisione precisa.

## API principali

| Area | Prefisso |
|---|---|
| Autenticazione | `/api/auth` |
| Team | `/api/teams` |
| Piloti | `/api/pilots` |
| Pool | `/api/pools` |
| Campionati, iscrizioni, gare e classifica | `/api/championships` |
| Negozio del giocatore (vista, acquisto, inventario, storico) | `/api/championships/{id}/shop` |
| Amministrazione e pulizia | `/api/admin` |
| Template e immagini del Negozio (admin) | `/api/shop` |
| Salute del servizio | `/health` |

Rotte del Negozio per il giocatore (12c): `GET /{id}/shop?pilot_id=`, `POST /{id}/shop/purchases`, `GET /{id}/shop/inventory?pilot_id=`, `GET /{id}/shop/history`, `GET /{id}/shop/history/all` (solo admin). L'elenco dei campionati con negozio per la barra di navigazione (`/api/me/shops` nella proposta) non è ancora implementato.

## Decisioni e questioni aperte

Decisioni dell'autore (2026-10-08): tetto di 100 copie per carta, rifiuto dell'acquisto con 409; l'admin con un pilota iscritto è un normale giocatore, con in più il tasto delle impostazioni del negozio; durante un campionato attivo un pilota eliminato non può comprare; il giocatore non vede lo storico di un pilota eliminato.

Questioni aperte:

- Il lock degli acquisti vale per un solo processo del backend (uso locale); con più worker servirebbe un blocco sul database.
- Elenco dei campionati con negozio per la barra di navigazione (backend da scrivere con la 12d).
- Come usare la pool degli sponsor nel gioco (predisposta, non ancora usata).
- Avviso quando un template di negozio non contiene pacchetti (da riportare in `SHOP_SCHEMA.md` a fine 12c).

## Documenti

- `PROJECT_SPEC.md`: specifiche funzionali (fonte delle regole).
- `PROJECT_NOTES.md`: mappa del codice, comandi, convenzioni e contesto di lavoro.
- `OPEN_QUESTIONS.md`: decisioni ancora rinviate.
- `SHOP_DESIGN.md`: funzionamento del Negozio spiegato dall'autore.
- `SHOP_SCHEMA.md`: schema, servizi, rotte e sottofasi del Negozio.
- Documenti storici (fotografie di una fase, non lo stato attuale): `DATABASE_ANALYSIS.md`, `BACKEND_BOOTSTRAP.md`, `BACKEND_AUTH.md`, `FRONTEND_BOOTSTRAP.md`, `FRONTEND_AUTH.md`.

## Prossimi passi

1. Approvazione della 12c, poi sottofase 12d: frontend del giocatore (barra di navigazione, scelta del pilota, pagina del negozio, popup di inventario e storico, animazione delle carte).
2. Sottofase 12e: frontend admin (impostazioni del negozio, pacchetti, template, cronologia).
3. Sottofase 12f: documenti finali e verifica complessiva.
