# Draft e preparazione della prima gara

Mappa delle fonti, non requisito approvato: le regole autorevoli sono in `PROJECT_SPEC.md` e nelle
specifiche dedicate indicate sotto.

## Documenti canonici

- [Indice della KB](../INDICE.md)
- [Specifiche di gioco](../../PROJECT_SPEC.md) — blocchi di stato correnti del flusso draft.
- [Specifiche draft](../../DRAFT_SPEC.md) — regole funzionali: presenze, ordine, soglia pool,
  scelte, tavolo, READY, annullamento e percorsi iniziali.
- [Validazione draft](../../DRAFT_VALIDATION.md) — evidenze e limiti riportati, non esecuzioni
  locali di questa fase.
- [Stato frontend draft](../../DRAFT_FRONTEND_STATUS.md) — lifecycle UI e correzioni storiche.
- [Mappa del codice](../../PROJECT_NOTES.md) — sezioni su draft, gare e live.
- [Stato del progetto](../../PROJECT_STATUS.md) — avanzamento e risultati riferiti.
- [Database](../../DATABASE.md) — schema descritto, non database reale.
- Nota storica: [UI draft fase 16](../../PHASE_16_DRAFT_UI.md).

Schede collegate esistenti: [Campionati e iscrizioni](campionati-e-iscrizioni.md),
[Gare, risultati e classifica](gare-risultati-e-classifica.md),
[Team, piloti e mazzi](team-piloti-e-mazzi.md),
[Eventi live e SSE](eventi-live-e-sse.md),
[Database, migrazioni e concorrenza](database-migrazioni-e-concorrenza.md),
[Autenticazione, sessioni e ruoli](autenticazione-e-sessioni.md),
[Preparazione della prossima gara](setup-prossima-gara.md).

Allineamento controllato: soglia `4N+5` alla prima gara e `N+3` dopo, tavolo da cinque, quattro
scelte per pilota con giro a serpentina e copia nuova dopo ogni scelta, restituzione del tavolo a
fine giro, controllo delle 15 copie dopo la modifica dei mazzi (massimo 15 sempre, esatto 15 dalle
gare successive), creazione della gara solo a tutti pronti, annullo con ripristino, X riservata al
creatore ed Escape bloccato corrispondono a `DRAFT_SPEC.md`. Non è emersa una discrepanza irrisolta
tra regole e codice. Una docstring interna
(`backend/app/services/draft/draft_preparation.py:32-38`) dice ancora che l'integrazione dei blocchi
alle altre scritture «resta necessaria prima dell'API»: il router è registrato
(`backend/app/main.py:62-84`) e le mutazioni usano lock, versioni e commit transazionali
(`backend/app/services/draft/draft_transaction.py:65-116`). Segnalazione senza modifica: il
commento è potenzialmente obsoleto.

## Perimetro ed esclusioni

**Incluso:** apertura e annullamento della preparazione, presenze, ordine, soglie della pool, turni
di scelta della prima gara e delle successive, spostamento carte nei mazzi, READY, creazione finale
della gara, percorso «Gara già disputata», DTO pubblici e interni, snapshot di ripristino, segnali
`draft.changed`, registro/host UI, recupero live e policy di chiusura del modal.

**Escluso:** regole di punteggio, risultati e revisione delle gare (scheda
[Gare, risultati e classifica](gare-risultati-e-classifica.md)); dettaglio di pacchetti enegozio
riusato per `draw_cards` (futura scheda); trasporto SSE generale (scheda
[Eventi live e SSE](eventi-live-e-sse.md)); database SQLite reale, test, CI e browser.

Questa scheda è proprietaria di: `draft_preparation`, del suo stato JSON e snapshot, dei comandi
draft e delle loro transazioni, del modal host lato client. La gara prodotta alla fine è solo
l'esito del flusso: le sue regole restano nella scheda delle gare.

## Revisione e stato del worktree esaminati

- Revisione: `21e17e637b43528d7320e88f0af5623db7158ee9`; branch
  `feat/0.9-mappe-eventi` in tracking con `origin/feat/0.9-mappe-eventi`.
- Worktree invariato rispetto alle schede precedenti: tre file tracciati modificati in fasi
  documentali precedenti e due directory non tracciate. Qui si aggiungono solo scheda e link.
- Non sono stati eseguiti test, né ispezionato il database reale o usato il browser.

## Punti d'ingresso e flusso

### API e contratto

- Router draft registrato con prefisso `/api`, con handler 409 dedicato per i blocchi:
  `backend/app/main.py:28-30`, `backend/app/main.py:62-84`.
- Il modal elenca le preparazioni pertinenti da qualsiasi pagina; l'apertura è solo admin/giudice,
  elabora revisioni scadute e non crea la gara:
  `backend/app/api/draft/draft.py:23-38`.
- Dettaglio e lettura del mazzo autorizzato; quest'ultima riguarda solo il proprio presente in fase
  `decks`, senza sponsor: `backend/app/api/draft/draft.py:41-50`.
- Comandi versionati: presenze e conferma, ordine e avvio scelte, anteprima e scelta, spostamento
  mazzo, READY, «Gara già disputata», annullo 204:
  `backend/app/api/draft/draft.py:59-140`.
- Ogni servizio è avvolto da `draft_request`, che fa rollback e traduce solo errori noti in
  403/404/409/422 senza esporre SQL, carte o snapshot; il commit resta al servizio:
  `backend/app/api/draft/draft_errors.py:28-61`,
  `backend/app/api/draft/draft_errors.py:64-66`.
- DTO pubblico con fase, versione, piloti propri, ordine, slot, prese, anteprima, pronti e turno
  corrente; i comandi usano `extra="forbid"` e tipi stretti:
  `backend/app/schemas/draft/draft.py:19-34`,
  `backend/app/schemas/draft/draft.py:48-85`.
- Stato interno formato 2 con validazione di duplicati, riferimenti, numero di prese, tavolo da
  cinque alla prima gara e coerenza del turno; lo snapshot conserva originali e versioni correnti
  monotone: `backend/app/schemas/draft/draft_state.py:11-28`,
  `backend/app/schemas/draft/draft_state.py:31-116`,
  `backend/app/schemas/draft/draft_snapshot.py:7-25`,
  `backend/app/schemas/draft/draft_snapshot.py:35-47`.

### Servizi e persistenza descritta

- Una preparazione per campionato, con `state_json`, `snapshot_json` e `version` come
  `version_id_col`; vincoli su fase e versione:
  `backend/app/db/models/draft.py:7-32`.
- Blocco draft letto senza scritture da `has_draft`; i router esistenti lo traducono in 409:
  `backend/app/services/draft/draft_guards.py:9-23`.
- Apertura: lock, ruolo admin/giudice, campionato aperto, nessuna gara non conclusa, nessuna
  preparazione esistente; snapshot di pool, inventari e mazzi; stato iniziale `attendance` con
  tutti gli iscritti presenti; `first_race` dedotto dall'assenza di gare; commit unico ed evento:
  `backend/app/services/draft/draft_preparation.py:23-70`.
- Presenze: solo creatore ancora gestore, versione attesa, fase `attendance`; nessuna modifica di
  mazzi o pool: `backend/app/services/draft/draft_preparation.py:73-115`.
- Transazione condivisa: lock, autorizzazione per fase, rilettura iscrizioni e versioni, flush,
  aggiornamento delle versioni tracciate, segnale e commit; qualsiasi errore fa rollback:
  `backend/app/services/draft/draft_transaction.py:20-31`,
  `backend/app/services/draft/draft_transaction.py:34-62`,
  `backend/app/services/draft/draft_transaction.py:65-116`.
- Regole pure: ordine inverso dell'arrivo precedente con nuovi presenti in coda; 4 scelte e 5 copie
  di tavolo alla prima gara, `N+3` e una scelta dopo; turno a serpentina:
  `backend/app/services/draft/draft_order.py:8-33`,
  `backend/app/services/draft/draft_order.py:36-57`,
  `backend/app/services/draft/draft_order.py:60-89`.
- Transizioni: passaggio a ordine oppure direttamente a mazzi se la pool non basta; estrazione
  senza filtri; turno e disponibilità lato server; anteprima condivisa solo del proprietario di
  turno; scelta singola o a quattro giri con restituzione e nuovo tavolo; READY con massimo 15 e
  esatto 15 solo dalle gare successive:
  `backend/app/services/draft/draft_transitions.py:34-86`,
  `backend/app/services/draft/draft_transitions.py:89-144`,
  `backend/app/services/draft/draft_transitions.py:147-218`,
  `backend/app/services/draft/draft_transitions.py:221-252`.
- Comandi: verifiche di pool, pilota, proprietario e riferimenti; conferma presenze, ordine, avvio,
  anteprima, scelta con trasferimento all'inventario e spostamento del mazzo nella stessa
  transazione:
  `backend/app/services/draft/draft_commands.py:16-42`,
  `backend/app/services/draft/draft_commands.py:45-139`,
  `backend/app/services/draft/draft_commands.py:142-165`.
- READY: ricontrollo di tutti i presenti nello stesso lock, creazione della gara con numero e
  `race.started`, rimozione della preparazione; «Gara già disputata» crea una gara normale dalla
  fase iniziale, senza draft, READY o vincolo delle 15 copie:
  `backend/app/services/draft/draft_completion.py:26-40`,
  `backend/app/services/draft/draft_completion.py:43-84`.
- Snapshot: cattura di originali e versioni con sessione pulita; ripristino solo dopo verifica di
  tutte le versioni attese, senza mai decrementarle:
  `backend/app/services/draft/draft_snapshot.py:11-40`,
  `backend/app/services/draft/draft_snapshot.py:43-72`.
- Annullo: solo creatore, «non Pronto» prima se i propri presenti sono pronti, ripristino e
  rimozione della riga in un solo commit; segnali per destinatario senza carte né snapshot:
  `backend/app/services/draft/draft_transaction.py:119-132`,
  `backend/app/services/draft/draft_notifications.py:10-26`.
- Letture autorizzate: il DTO pubblico omette `state_json` e `snapshot_json`; creatore gestore e
  proprietari presenti nelle fasi condivise; errore di JSON non diventa stato vuoto:
  `backend/app/services/draft/draft_view.py:27-75`,
  `backend/app/services/draft/draft_view.py:78-113`.
- **Schema SQLite effettivo non verificato**: colonne e vincoli derivano dal modello; il database
  reale non è stato ispezionato.

### Frontend

- Il registro è fornito dal layout e il componente `DraftHost` avvolge tutte le pagine; il ciclo
  segue sessione, utente e ruolo, non la versione dei DTO:
  `frontend/src/routes/+layout.svelte:23-31`,
  `frontend/src/routes/+layout.svelte:87-88`,
  `frontend/src/routes/+layout.svelte:282-282`.
- Registro a istanze: riusa store per ID, scarta risposte di altre generazioni, non ritenta POST,
  distingue completamenti reali dalla sparizione REST:
  `frontend/src/lib/draft/host/draft-host.ts:50-55`,
  `frontend/src/lib/draft/host/draft-host.ts:125-150`,
  `frontend/src/lib/draft/host/draft-host.ts:202-273`,
  `frontend/src/lib/draft/host/draft-host.ts:275-371`.
- Host UI: coda ordinata, dialog con chiave `sessione:ID`, blocco di Escape e `inert` sul resto
  della pagina, avvisi di completamento, rilettura manuale senza reinvio:
  `frontend/src/lib/draft/host/draft-host-view.ts:4-37`,
  `frontend/src/lib/draft/host/draft-host-view.ts:47-55`,
  `frontend/src/lib/components/draft/draft-host.svelte:55-127`,
  `frontend/src/lib/components/draft/draft-host.svelte:143-190`.
- Live: un solo stream condiviso, accorpamento dei segnali durante GET/POST e letture di dettaglio,
  nessun timer, polling o seconda connessione:
  `frontend/src/lib/draft/draft-live.ts:13-19`,
  `frontend/src/lib/draft/draft-live.ts:20-106`.
- Lancio dalla pagina campionato con guardie locali su sessione, permessi, chiusura e gara non
  conclusa; il risultato è verificato prima di applicare messaggi dopo `await`:
  `frontend/src/lib/championship/championship-draft-launch.ts:5-41`,
  `frontend/src/routes/championships/[id]/+page.svelte:238-267`.
- API client: campi esatti per comando, ID e versioni validati prima della rete, nessun retry e
  nessuna rilettura automatica; risposte discordanti rifiutate:
  `frontend/src/lib/draft/draft-api.ts:16-58`,
  `frontend/src/lib/draft/draft-api.ts:65-141`.
- Tipi e parsing: fasi, DTO, mazzo e comandi; il parsing verifica forma e tipi ma non ricostruisce
  regole o permessi: `frontend/src/lib/draft/draft-types.ts:3-69`,
  `frontend/src/lib/draft/draft-validation.ts:4-59`,
  `frontend/src/lib/draft/draft-validation.ts:62-132`.
- Controller di sessione: generazione legata al contesto, rifiuto di snapshot obsoleti,
  classificazione 401/403, 409 e 422, esito incerto conservato dopo scritture non classificabili:
  `frontend/src/lib/draft/draft-session.ts:31-37`,
  `frontend/src/lib/draft/draft-session.ts:90-129`,
  `frontend/src/lib/draft/draft-session.ts:137-205`.
- Store reattivo con zoom locale e copie della vista; la versione non entra nella chiave di
  lifecycle del coordinator: `frontend/src/lib/stores/draft.svelte.ts:10-19`,
  `frontend/src/lib/stores/draft.svelte.ts:47-90`,
  `frontend/src/lib/stores/draft.svelte.ts:112-123`.
- Chiusura: X solo per il creatore e non in READY, proposta fissata su snapshot utilizzabile,
  conferma rivista al clic; la navigazione ignora i clic dentro il dialog:
  `frontend/src/lib/draft/draft-close-policy.ts:7-23`,
  `frontend/src/lib/draft/draft-close-policy.ts:25-57`,
  `frontend/src/lib/components/shared/nav-menu.svelte:55-55`.
- Schermata derivata dallo stato senza dedurre la gara da tutti READY; il coordinator del mazzo
  sopravvive al solo rimontaggio della vista: `frontend/src/lib/draft/draft-flow.ts:6-56`.

## Test individuati (non eseguiti in questa fase)

- `backend/tests/test_draft_api.py:30-72` — ruoli, apertura/annullo/recupero, READY e prima gara.
- `backend/tests/test_draft_preparation.py`, `backend/tests/test_draft_commands.py`,
  `backend/tests/test_draft_completion.py` — servizi transazionali e finalizzazione.
- `backend/tests/test_draft_transitions.py`, `backend/tests/test_draft_order.py`,
  `backend/tests/test_draft_state.py` — regole pure, turni e validazione stato.
- `backend/tests/test_draft_snapshot.py`, `backend/tests/test_draft_snapshot_service.py`,
  `backend/tests/test_draft_snapshot_tracking.py` — originali, ripristino e versioni.
- `backend/tests/test_draft_transaction.py`, `backend/tests/test_draft_guards.py`,
  `backend/tests/test_draft_notifications.py`, `backend/tests/test_draft_view.py`,
  `backend/tests/test_draft_models.py` — lock, blocchi, segnali e letture.
- `frontend/src/lib/draft/draft-api.spec.ts`, `frontend/src/lib/draft/draft-session.spec.ts`,
  `frontend/src/lib/draft/draft-validation.spec.ts` — client, controller e parsing.
- `frontend/src/lib/draft/host/`, `frontend/src/lib/draft/deck/`,
  `frontend/src/lib/draft/attendance/`, `frontend/src/lib/draft/order/` e
  `frontend/src/lib/draft/picking/` — prove UI delle singole fasi.

Nessun test è stato eseguito durante la generazione della scheda. I conteggi riportati in
`docs/DRAFT_SPEC.md:98`, `docs/DRAFT_VALIDATION.md:42` e `docs/PROJECT_STATUS.md:58-64` sono
risultati riferiti in documenti, relativi a fasi diverse e non qui ri-osservati.

## Osservato, dedotto e non verificato

- **Osservato:** router, DTO, modello, servizi, componenti e test citati; documenti canonici e
  blocchi di stato.
- **Dedotto dal codice:** la gara non esiste prima che tutti i presenti siano pronti; lo snapshot
  di ripristino non è mai serializzato nelle risposte pubbliche; il recupero live usa il client di
  eventi condiviso; un segnale viene emesso per destinatario, con carte assenti dal payload.
- **Non verificato:** database SQLite reale, esecuzione test, browser, CI, pubblicazione degli
  eventi in runtime e la portata effettiva della docstring obsoleta segnalata all'inizio.

## Fonti da ricontrollare quando cambiano le fonti pertinenti

- `backend/app/main.py`, `backend/app/api/draft/`, `backend/app/schemas/draft/`,
  `backend/app/db/models/draft.py`.
- `backend/app/services/draft/` e i servizi da esso richiamati in `race`, `cards`, `shop`,
  `championship` e `core`.
- `frontend/src/routes/+layout.svelte`, `frontend/src/routes/championships/[id]/+page.svelte`,
  `frontend/src/lib/draft/`, `frontend/src/lib/championship/championship-draft-launch.ts`,
  `frontend/src/lib/stores/draft.svelte.ts`.
- I test elencati sopra e i documenti canonici linkati all'inizio. Se cambiano soglie, turni,
  READY, annullo o blocchi di stato, aggiornare qui i rimandi a `DRAFT_SPEC.md`.
