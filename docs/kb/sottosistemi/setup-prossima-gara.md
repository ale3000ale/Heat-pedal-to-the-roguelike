# Preparazione della prossima gara: SETUP GARA → AVVIA GARA

Questa scheda è una **mappa delle fonti**, non un requisito approvato: non sostituisce
specifiche, codice, database o lo stato verificato del progetto. Ogni affermazione riporta la
fonte letta; ciò che non è stato verificato è indicato esplicitamente.

## Documenti canonici

- [Indice della knowledge base](../INDICE.md)
- [Specifiche di gioco](../../PROJECT_SPEC.md) — fonte autorevole delle regole.
- [Mappa del codice e regole di lavoro](../../PROJECT_NOTES.md)
- [Stato del progetto](../../PROJECT_STATUS.md)
- [ChangeLog](../../CHANGELOG.md) — versioni e date.

Non è stata trovata in `docs/` una specifica approvata dedicata a questo sottosistema: il
comportamento descritto sotto è evidenza da codice e test, non un requisito.

## Perimetro ed esclusioni

**Incluso:** estrazione di mappa ed evento dalle pool del campionato (catalogo in
`backend/JSON/maps.json` e `events.json`), persistenza dei due percorsi sul campionato,
segnale `championship.setup_changed`, pulsante `SETUP GARA` / `AVVIA GARA`, sezione
“PROSSIMA GARA”, annullamento del setup e consumo delle due carte dalla pool alla prima
registrazione dei risultati o alla chiusura del campionato.

**Escluso:** regole interne della draft, creazione ed esecuzione della gara, regole dei mazzi
e delle carte, strumento di importazione immagini, eventi live non pertinenti, dati reali e
migrazioni eseguite.

## Aggiornamento del 24 novembre 2026

La sezione “PROSSIMA GARA” mostra anche i dati della mappa estratta, senza nuove colonne:
l'immagine conserva le dimensioni originali e, nella barra del nome, un mini tachimetro
`speedometer` contiene il numero di curve mentre un quadratino accanto contiene quello delle
caselle. Le miniature `backend/media/cards/generics/stress.webp` e
`backend/media/cards/generics/heat.webp` mostrano il conteggio al centro con `text-2xl`: su
telefono stanno a destra del nome, su desktop in una colonna assoluta più interna
(`sm:right-12`). Un conteggio non disponibile è reso con `—`.

I valori sono derivati a ogni lettura: `map_stats`
(`backend/app/services/championship/race_setup.py:58-88`) cerca in `backend/JSON/maps.json`
l'elemento il cui `image` coincide con il path della mappa estratta, normalizzando separatori e
maiuscole, e restituisce stress, heat, curve e caselle come interi non negativi. File
mancante/corrotto, mappa non trovata o valore non valido restituiscono `None`. I campi
`next_map_stress`, `next_map_heat`, `next_map_curve` e `next_map_caselle` sono nello schema
`backend/app/schemas/championship/championship.py:45-54` e vengono popolati in
`backend/app/api/championship/championships.py:56-68`.

Punti frontend correnti: helper in `frontend/src/lib/championship/next-race-setup.ts:24-34`,
tipo in `frontend/src/lib/types.ts:78-81`, valori derivati in
`frontend/src/routes/championships/[id]/+page.svelte:68-77` e layout in `:451-499`. Test
aggiornati: `backend/tests/test_championship_race_setup.py:70-71,96-124,153-154`,
`frontend/src/lib/championship/next-race-setup.spec.ts:31-41` e
`frontend/src/lib/championship/championship-live.spec.ts:65-66`.

Gli esiti già osservati prima degli ultimi ritocchi (9 test backend mirati, 938 test backend
completi con 1 warning e 14 subtest, check frontend senza errori, 723 test e build riuscita,
lint fermo su 19 file preesistenti) si riferiscono allo stato precedente. Curve/caselle, layout
responsive e numeri più grandi non sono ancora stati verificati: su indicazione dell'autore
test, Prettier, lint, build e `git diff --check` sono rinviati al merge. Nessuna migrazione,
dipendenza, modifica di `maps.json` o delle immagini, prova browser, CI od operazione VCS. Le
citazioni di riga delle sezioni storiche seguenti si riferiscono alla revisione
`21e17e637b43528d7320e88f0af5623db7158ee9` e non sono state riscritte.

## Pool di mappe ed eventi (24 novembre 2026)

- Modello: `backend/app/db/models/championship.py` — `map_pool_ids` ed `event_pool_ids`,
  testo JSON nullable; `NULL` significa pool mai inizializzata, `[]` pool esaurita.
- Migrazione `c1d5e9f3a7b2`
  (`backend/alembic/versions/c1d5e9f3a7b2_pool_mappe_eventi.py`): crea le colonne e
  inizializza i campionati esistenti con gli ID dei due JSON.
- Servizio `backend/app/services/championship/board_pools.py`: catalogo dai JSON,
  inizializzazione, estrazione, consumo e vista; la vista non scrive sul campionato.
- Creazione: `backend/app/services/championship/championships.py` chiama `initialize_pools`.
- Setup: `prepare_next_race` estrae dalle pool; `cancel_next_race` svuota i percorsi senza
  toccare le pool.
- Consumo: `backend/app/services/race/races.py` chiama `consume_setup` alla prima
  registrazione dei risultati, prima di azzerare i percorsi.
- API: `DELETE /api/championships/{id}/setup` per admin e giudici in
  `backend/app/api/championship/championships.py`; `GET /api/championships/{id}/board-pools/{kind}`
  per il solo admin in `backend/app/api/championship/board_pools.py`, registrato in
  `backend/app/main.py`.
- Frontend: helper `frontend/src/lib/championship/board-pool-api.ts`, pannello
  `frontend/src/lib/components/championship/championship-board-pool-panel.svelte`, sezione
  Pool in `championship-settings.svelte`, cestino in
  `frontend/src/routes/championships/[id]/+page.svelte`, icone `trash` e `deck_export` in
  `frontend/src/lib/components/shared/racing-icon.svelte`.
- Test: `backend/tests/test_championship_race_setup.py` (estrazione senza consumo, consumo
  ai risultati, annullamento, vista pool, creazione, campionato legacy) e
  `frontend/src/lib/championship/board-pool-api.spec.ts`.

## Revisione e stato del worktree esaminati

- Revisione: `21e17e637b43528d7320e88f0af5623db7158ee9`
  (`feat: prepara la prossima gara con mappa ed evento`).
- Branch: `feat/0.9-mappe-eventi`, in tracking con `origin/feat/0.9-mappe-eventi`.
- Stato iniziale letto prima di questa scheda: nessuna modifica tracciata; solo le directory
  non tracciate `.agents/skills/codebase-knowledge-builder/` e `docs/kb/`; `git diff --check`
  senza output.
- Durante questa fase documentale vengono aggiunti la scheda e modificati `AGENTS.md`,
  `docs/kb/INDICE.md`, `docs/PROJECT_NOTES.md` e `docs/PROJECT_STATUS.md`.
- Non sono stati ri-eseguiti test, né avviati `setup`, `start` o migrazioni, né scritto sul
  database reale.

## Punti d'ingresso e flusso

### Frontend

- Stati di conferma separati per setup e avvio:
  `frontend/src/routes/championships/[id]/+page.svelte:40-41`.
- Nome, URL e disponibilità del setup derivati dai due percorsi:
  `frontend/src/routes/championships/[id]/+page.svelte:63-69`;
  helper `frontend/src/lib/championship/next-race-setup.ts:6-18`;
  tipi `frontend/src/lib/types.ts:75-76`.
- Il pulsante mostra `SETUP GARA` o `AVVIA GARA` e apre la conferma corrispondente:
  `frontend/src/routes/championships/[id]/+page.svelte:651-667`.
- Testi esatti delle due conferme: `Vuoi preparare la prossima gara?` e
  `Vuoi iniziare la gara?`: `frontend/src/routes/championships/[id]/+page.svelte:741-755`.
- La conferma di setup chiama `POST /championships/{id}/setup` e poi aggiorna la pagina:
  `frontend/src/routes/championships/[id]/+page.svelte:200-224`.
- La conferma di avvio apre la preparazione nel registro globale, senza creare direttamente
  una gara: `frontend/src/routes/championships/[id]/+page.svelte:226-265`.
- Sezione “PROSSIMA GARA” con mappa ed evento, visibile quando il setup è pronto e il
  campionato non è chiuso: `frontend/src/routes/championships/[id]/+page.svelte:414-466`.

### API

- Prefisso del router: `backend/app/main.py:69`.
- `POST /api/championships/{championship_id}/setup`, solo admin e giudice, con traduzione
  degli errori di dominio in 404/409/503:
  `backend/app/api/championship/championships.py:106-127`;
  dipendenza `JudgeUser`: `backend/app/api/deps.py:58-65`.
- I due percorsi sono esposti nel dettaglio del campionato:
  `backend/app/schemas/championship/championship.py:45-49`;
  populate in `backend/app/api/championship/championships.py:60-61`.

### Servizio e persistenza

- Cartelle, suffisso e funzione di scelta sostituibile nei test:
  `backend/app/services/championship/race_setup.py:16-19`, `:34-53`.
- Transazione protetta: lock SQLite, controlli su campionato chiuso, gara in corso, draft e
  setup già presente, scrittura dei percorsi, evento e commit; rollback su errore senza retry:
  `backend/app/services/championship/race_setup.py:56-96`.
- Colonne del modello: `backend/app/db/models/championship.py:46-47`.
- Migrazione `b8f4e2a1c7d9`, aggiunta e rimozione delle colonne:
  `backend/alembic/versions/b8f4e2a1c7d9_next_race_setup.py:5-20`.
- Pulizia dei percorsi alla chiusura del campionato:
  `backend/app/services/championship/championships.py:164-165`.
- Pulizia alla prima registrazione dei risultati di una gara:
  `backend/app/services/race/races.py:209-213`.

### Segnale live

- Tipo e validazione del segnale pubblico senza payload né piloti:
  `backend/app/schemas/core/events.py:6-11` e `:37-43`;
  `frontend/src/lib/events/event-types.ts:1-3`;
  `frontend/src/lib/events/event-validation.ts:55-59`.

## Test individuati (non eseguiti in questa fase)

- `backend/tests/test_championship_race_setup.py:53,74,84,101,115,129`: estrazione e
  pubblicazione, autorizzazioni, blocchi di gara/draft/campionato chiuso, assenza di immagini
  e pulizia dopo i risultati.
- `backend/tests/test_event_schemas.py:17-23`: segnale di setup pubblico e senza payload.
- `frontend/src/lib/championship/next-race-setup.spec.ts:4-25`: nome senza estensione,
  URL `/media` e valori nulli.
- `frontend/src/lib/events/event-validation.spec.ts:62-71`: rifiuto di piloti e payload sul
  segnale di setup.
- `frontend/src/lib/championship/championship-live.spec.ts:52-63`: snapshot con i due
  percorsi presenti nel tipo frontend.

Nessuno di questi test è stato eseguito durante la generazione della scheda. I conteggi e gli
esiti della fase precedente sono **riferiti, non ri-osservati**: non vengono qui dichiarati
come superati.

## Osservato, dedotto e non verificato

- **Osservato:** righe di codice e test citate sopra; testi delle due conferme; presenza dei
  due percorsi in modello, schema, migrazione e tipo frontend; validazione del segnale.
- **Dedotto dal codice:** il pulsante cambia funzione in base alla completezza dei due
  percorsi; il setup è pensato per una sola gara successiva alla volta; “AVVIA GARA” apre la
  preparazione, non la gara.
- **Non verificato in questa fase:** comportamento nel browser, contenuto attuale di
  `backend/media/board`, stato del database reale, esecuzione dei test, risultati CI e
  collaudo visivo dell'autore riportato nella fase precedente.

## Fonti da ricontrollare quando la funzionalità cambia

Rivalutare la scheda quando cambia una delle fonti pertinenti, non a ogni commit:

- `backend/app/services/championship/race_setup.py`, `backend/app/services/race/races.py`,
  `backend/app/services/championship/championships.py`,
  `backend/app/services/championship/board_pools.py`.
- `backend/app/api/championship/championships.py`, `backend/app/api/championship/board_pools.py`,
  `backend/app/api/deps.py`, `backend/app/schemas/championship/championship.py`,
  `backend/app/schemas/core/events.py`.
- `backend/app/db/models/championship.py`,
  `backend/alembic/versions/b8f4e2a1c7d9_next_race_setup.py`,
  `backend/alembic/versions/c1d5e9f3a7b2_pool_mappe_eventi.py`.
- `frontend/src/routes/championships/[id]/+page.svelte`,
  `frontend/src/lib/championship/next-race-setup.ts`,
  `frontend/src/lib/championship/board-pool-api.ts`,
  `frontend/src/lib/components/championship/championship-board-pool-panel.svelte`,
  `frontend/src/lib/components/championship/championship-settings.svelte`,
  `frontend/src/lib/components/shared/racing-icon.svelte`,
  `frontend/src/lib/types.ts`,
  `frontend/src/lib/events/event-types.ts`, `frontend/src/lib/events/event-validation.ts`.
- I test elencati nella sezione precedente e i documenti canonici linkati all'inizio.
