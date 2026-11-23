# Eventi live e SSE

Mappa delle fonti, non requisito approvato: il contratto degli eventi e il trasporto non sono
specifiche di gioco e non sostituiscono i documenti di fase.

## Documenti canonici

- [Indice della KB](../INDICE.md)
- [Mappa del codice](../../PROJECT_NOTES.md) — sezione “Live e lifecycle” e cronologia fase 15.
- [Stato del progetto](../../PROJECT_STATUS.md) — chiusura fase 15 e precedenza dell'appendice
  della specifica.
- [Fase 15](../../PHASE_15.md), [Implementazione fase 15](../../PHASE_15_IMPLEMENTATION.md),
  [Frontend live](../../PHASE_15_FRONTEND_LIVE.md),
  [Eventi di stato](../../PHASE_15_STATE_EVENTS.md) — cronologia, non requisiti.

Allineamento controllato: `PROJECT_NOTES.md` vieta un secondo `EventSource` e il polling nel
pannello admin carte; il fallback a intervallo di `startLiveRefresh` riguarda altre risorse e non
contraddice quella sezione. I documenti di fase 15 sono marcati come storici.

## Perimetro ed esclusioni

**Incluso:** tipi e validazione degli eventi, registro persistente, autorizzazione delle letture,
endpoint `/api/events/stream`, cursore/risincronizzazione, codifica SSE, client frontend condiviso
e coordinamento delle riletture REST.

**Escluso:** chi emette ciascun evento e le regole che lo generano (schede funzionali), contenuto
delle riletture REST, database SQLite reale, esecuzione test, browser.

Questa scheda è proprietaria di: contratto `EventType`/`EventCreate`, registro `event_log`,
protocollo SSE, `eventClient` e `startLiveRefresh`. Le altre schede elencano i segnali che emettono
senza ridefinirne il formato.

## Revisione e stato del worktree esaminati

- Revisione: `21e17e637b43528d7320e88f0af5623db7158ee9`; branch
  `feat/0.9-mappe-eventi` in tracking con `origin/feat/0.9-mappe-eventi`.
- Worktree: invariato rispetto alle schede precedenti (tre file tracciati modificati in fasi
  documentali precedenti, due directory non tracciate); qui si aggiungono solo scheda e link.
- Non sono stati eseguiti test, né aperto stream o browser, né ispezionato il database reale.

## Punti d'ingresso e flusso

### Contratto e registro

- Tipi ammessi e validazione con `extra="forbid"`; segnali pubblici vuoti per iscrizioni e setup,
  segnale draft privato con solo `preparation_id`:
  `backend/app/schemas/core/events.py:6-11`, `backend/app/schemas/core/events.py:14-25`,
  `backend/app/schemas/core/events.py:27-54`.
- Elenco frontend dei tipi di dominio: `frontend/src/lib/events/event-types.ts:1-14`.
- `append_event` accoda nella transazione del chiamante, senza commit:
  `backend/app/services/core/event_log.py:15-27`.
- `read_events` separa eventi privati dell'utente da pubblici dei campionati accessibili;
  admin/giudice vedono tutti i pubblici, non quelli privati altrui; l'eccezione osservatore
  vale solo per il segnale iscrizioni vuoto: `backend/app/services/core/event_log.py:30-71`.
- Modello `event_log` con indici e `sqlite_autoincrement` (schema descritto, non database
  effettivo): `backend/app/db/models/event_log.py:8-26`.
- Retenzione 24 ore e purge nella transazione del chiamante:
  `backend/app/services/core/event_log.py:74-85`; chiamata dal timer di revisione:
  `backend/app/services/race/review_timer.py:55`.

### Endpoint e stream

- Prefisso del router: `backend/app/main.py:82`.
- `GET /api/events/stream`: 401 senza cookie o sessione non valida, 422 per cursore non valido,
  intestazioni no-cache e no-buffering: `backend/app/api/events.py:19-40`.
- Factory di sessioni brevi sostituibile nei test: `backend/app/api/events.py:14-16`.
- Parsing di `Last-Event-ID` come int64: `backend/app/services/core/event_stream.py:14-23`.
- Snapshot iniziale `resync` (`initial` o `cursor_unavailable`), rilettura da `event_log` e
  codifica dei frame: `backend/app/services/core/event_stream.py:32-62`.
- Polling interno ogni secondo, keep-alive a 15 s, `auth.expired` su sessione revocata; le query
  girano in thread pool e la sessione si chiude prima di ogni attesa:
  `backend/app/services/core/event_stream.py:65-90`.

### Client frontend

- Un solo `EventSource` per sessione, creato nel layout autenticato e chiuso a logout/cambio
  utente: `frontend/src/routes/+layout.svelte:45-54`, `frontend/src/routes/+layout.svelte:72-78`,
  `frontend/src/lib/events/event-client.ts:28-31`, `frontend/src/lib/events/event-client.ts:109-111`.
- Connessione con `generation`, retry a 3 s, stati `connecting/open/retrying/unsupported/expired`,
  validazione dei frame e publish dei soli tipi attesi:
  `frontend/src/lib/events/event-client.ts:33-60`, `frontend/src/lib/events/event-client.ts:113-187`.
- Validazione difensiva del protocollo: cursore int64 come stringa, `auth.expired` senza dati,
  rifiuto di piloti/payload sui segnali vuoti e del segnale draft non conforme:
  `frontend/src/lib/events/event-validation.ts:18-78`.
- `startLiveRefresh` coordina riletture REST, usa il polling solo quando lo stream non è `open`,
  si ferma su 401/`auth.expired` e restituisce `dispose`:
  `frontend/src/lib/events/live-refresh.svelte.ts:14-21`,
  `frontend/src/lib/events/live-refresh.svelte.ts:49-99`.

## Test individuati (non eseguiti in questa fase)

- `backend/tests/test_event_schemas.py:8-40` — contratto DTO e segnali vuoti.
- `backend/tests/test_events_stream.py:30-75` — cursore, frame, replay iniziale, revoca,
  ri-sincronizzazione, autorizzazione e intestazioni della rotta.
- `backend/tests/test_event_log_service.py:34-89` — privacy, accesso pubblico, cursore, purge e
  rollback.
- `backend/tests/test_event_log_model.py:7-47` — indici, rollback, ID non riutilizzati, cascade.
- `frontend/src/lib/events/event-client.spec.ts`, `frontend/src/lib/events/event-validation.spec.ts`,
  `frontend/src/lib/events/live-refresh.spec.ts`, `frontend/src/lib/events/refresh-coalescer.spec.ts`
  — client, validazione, coordinamento riletture.

Nessun test è stato eseguito durante la generazione della scheda.

## Osservato, dedotto e non verificato

- **Osservato:** contratto, registro, endpoint, codifica, client, validazione e test citati.
- **Dedotto dal codice:** il cursore è un ID del registro, non un timestamp; la riconnessione
  pubblica un `resync` locale; `auth.expired` chiude il client senza dati privati.
- **Non verificato:** comportamento in browser, connessioni reali, database SQLite effettivo,
  esecuzione test e CI.

## Fonti da ricontrollare quando cambiano le fonti pertinenti

- `backend/app/schemas/core/events.py`, `backend/app/services/core/event_log.py`,
  `backend/app/services/core/event_stream.py`, `backend/app/api/events.py`,
  `backend/app/db/models/event_log.py`, `backend/app/services/race/review_timer.py`.
- `frontend/src/lib/events/`, `frontend/src/routes/+layout.svelte` e i consumatori di
  `eventClient` nelle schede funzionali.
- I test elencati sopra e i documenti canonici linkati all'inizio. Se cambia un tipo di evento,
  aggiornare qui la lista e verificare che mittente e frontend siano ancora allineati.
