# Team, piloti e mazzi

Mappa delle fonti, non requisito approvato: le regole di gioco restano in `PROJECT_SPEC.md`.

## Documenti canonici

- [Indice della KB](../INDICE.md)
- [Specifiche di gioco](../../PROJECT_SPEC.md) — fonte autorevole per regole e limiti.
- [Mappa del codice](../../PROJECT_NOTES.md)
- [Stato del progetto](../../PROJECT_STATUS.md)
- [Database](../../DATABASE.md) — schema descritto dei modelli, non database reale.

## Perimetro ed esclusioni

**Incluso:** team e piloti dell'utente, unicità e normalizzazione dei nomi, eliminazione logica,
assegnazione al team, tre mazzi per pilota e spostamento delle copie tra inventario e mazzo da
gioco.

**Escluso:** iscrizioni e classifiche (scheda campionati), avvio e risultati di gara (scheda gare),
giocate/regali/sponsor (scheda carte in gara), pool e caricamento carte (scheda amministrazione),
meccanica del lock (scheda database), formato del contratto SSE (scheda eventi), database SQLite
reale, esecuzione test.

Questa scheda è proprietaria di: team, piloti, tre mazzi e regole di spostamento delle copie.
`services/cards/cards.py` è letto qui solo come interfaccia (`parse_cards`, `dump_cards`,
`STARTER_INVENTORY`, limite 15); il suo contenuto e le pool sono della scheda amministrazione.

## Revisione e stato del worktree esaminati

- Revisione: `21e17e637b43528d7320e88f0af5623db7158ee9`; branch
  `feat/0.9-mappe-eventi` in tracking con `origin/feat/0.9-mappe-eventi`.
- Worktree invariato rispetto alle schede precedenti; qui si aggiungono solo scheda e link
  all'indice.
- Non sono stati eseguiti test, né ispezionato il database reale o usato il browser.

## Punti d'ingresso e flusso

### API

- Prefissi dei router: `backend/app/main.py:66-67`.
- Team: elenco, creazione 201/409, rename 404/409, delete 204/404/409 se un pilota è in
  campionato attivo: `backend/app/api/pilots/teams.py:20-57`.
- Piloti: elenco paginato con ricerca e filtro team, creazione con tre mazzi, dettaglio con
  `deck_locked`, spostamenti, rename, cambio team e delete:
  `backend/app/api/pilots/pilots.py:117-137`, `backend/app/api/pilots/pilots.py:140-172`,
  `backend/app/api/pilots/pilots.py:175-207`.
- Traduzione degli errori di dominio in 404/409 nello spostamento carte:
  `backend/app/api/pilots/pilots.py:96-114`.

### Servizi e persistenza descritta

- Nomi: spazi normalizzati e chiave `casefold` per l'unicità:
  `backend/app/services/pilots/names.py:1-9`.
- Team: proprietario, visibilità solo ai propri, nome unico anche tra i nascosti, eliminazione
  logica che nasconde anche i piloti e la blocca se sono in campionati attivi:
  `backend/app/services/pilots/teams.py:44-63`, `backend/app/services/pilots/teams.py:74-89`,
  `backend/app/services/pilots/teams.py:111-124`.
- Piloti: creazione con inventario iniziale, inventario sponsor vuoto e mazzo da gioco vuoto;
  rename consentito anche se iscritto; cambio team e cancellazione bloccati con campionato
  attivo: `backend/app/services/pilots/pilots.py:75-107`,
  `backend/app/services/pilots/pilots.py:110-126`,
  `backend/app/services/pilots/pilots.py:129-150`.
- Ricerca con `autoescape` e ordinamento stabile per nome e id:
  `backend/app/services/pilots/pilots.py:40-60`.
- Modelli con `name_key`, tre FK ai mazzi e `deleted_at`:
  `backend/app/db/models/team.py:6-19`, `backend/app/db/models/pilot.py:6-26`.
- Interfacce delle carte: limite 15, inventario iniziale di quattro velocità da 3 copie,
  JSON `{name, path, copies}` e validazione:
  `backend/app/services/cards/cards.py:6`, `backend/app/services/cards/cards.py:12-16`,
  `backend/app/services/cards/cards.py:27-32`, `backend/app/services/cards/cards.py:35-52`.
- Spostamento di una copia con lock prima delle letture, massimo 15 e blocco gara/revisione;
  solo `StaleDataError` viene ritentato: `backend/app/services/pilots/pilot_deck.py:107-152`.
- **Schema SQLite effettivo non verificato**: le colonne elencate derivano dai modelli; il
  database reale è fuori perimetro e non è stato ispezionato.

### Frontend

- Pagina Team e piloti: creazione/modifica/eliminazione e cambio team tramite API:
  `frontend/src/routes/team/+page.svelte:46-57`, `frontend/src/routes/team/+page.svelte:90-130`.
- Pagina pilota: lettura del dettaglio, mazzo bloccato, spostamento e ricarica dopo un rifiuto:
  `frontend/src/routes/pilots/[id]/+page.svelte:20-31`,
  `frontend/src/routes/pilots/[id]/+page.svelte:40-65`.

## Test individuati (non eseguiti in questa fase)

- `backend/tests/test_pilots_api.py:171,197` — team bloccato in campionato attivo e delete
  rifiutato.
- `backend/tests/test_pilots_service.py:178,210` — stesse regole a livello servizio.
- `backend/tests/test_pilot_deck_locked.py:33-99` — mazzo modificabile, bloccato in gara e fino
  alla conferma della revisione, non bloccato in altri campionati.
- `backend/tests/test_deck_versioning.py:12` — conflitto di versione.

Nessun test è stato eseguito durante la generazione della scheda.

## Osservato, dedotto e non verificato

- **Osservato:** router, servizi, modelli, interfacce delle carte, lock, pagine e test citati.
- **Dedotto dal codice:** i nomi sono unici globalmente per tipo anche tra elementi nascosti;
  eliminare un team nasconde i suoi piloti; la revisione non confermata mantiene il mazzo in
  sola lettura.
- **Non verificato:** database SQLite reale, browser, esecuzione test, CI e regole approvate
  oltre a quanto scritto in `PROJECT_SPEC.md`.

## Fonti da ricontrollare quando cambiano le fonti pertinenti

- `backend/app/api/pilots/`, `backend/app/services/pilots/`, `backend/app/db/models/team.py`,
  `backend/app/db/models/pilot.py`, `backend/app/db/models/deck.py`.
- Per le sole interfacce usate qui: `backend/app/services/cards/cards.py`.
- `frontend/src/routes/team/+page.svelte`, `frontend/src/routes/pilots/[id]/+page.svelte`.
- I test elencati sopra e i documenti canonici linkati all'inizio.
