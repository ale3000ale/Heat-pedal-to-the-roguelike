# Carte sponsor in gara e revisione

Mappa delle fonti, non requisito approvato: le regole autorevoli sono in `PROJECT_SPEC.md`
(sezione 14) e nelle note di fase indicate sotto.

## Documenti canonici

- [Indice della KB](../INDICE.md)
- [Specifiche di gioco, sezione 14](../../PROJECT_SPEC.md) — regole approvate: giocate, annullo,
  chiusura, revisione, tasto S e notifiche.
- [Specifiche fase 13](../../PHASE_13_SPEC.md) — decisioni storiche e dettaglio delle sottofasi
  13a-13g.
- [API dei conteggi, fase 14](../../PHASE_14_REVIEW_API.md) — rotte `/draft` e `/counts/confirm`.
- [Fase 15](../../PHASE_15.md) — stato corrente di eventi, client e timer.
- [Eventi di giocata](../../PHASE_15_CARD_PLAY_EVENTS.md) — invalidazioni private e pubbliche.
- [Eventi di stato della revisione](../../PHASE_15_STATE_EVENTS.md) — azioni e payload senza carte.
- [Modulo timer](../../PHASE_15_TIMER.md) — nota storica del modulo prima del collegamento.
- [Conferma selettiva delle notifiche regalo](../../PHASE_15_GIFT_SEEN_SELECTED.md) — contratto
  `seen-selected`.
- [Riconciliazione inventario revisione](../../PHASE_15_REVIEW_INVENTORY_RECONCILE.md) —
  riconciliazione lato client.
- [Mappa del codice](../../PROJECT_NOTES.md) — sezioni su carte, gare ed eventi.
- [Stato del progetto](../../PROJECT_STATUS.md) — avanzamento e risultati riferiti.
- [Database](../../DATABASE.md) — schema descritto, non database reale.

Schede collegate esistenti: [Team, piloti e mazzi](team-piloti-e-mazzi.md),
[Gare, risultati e classifica](gare-risultati-e-classifica.md),
[Draft e preparazione della prima gara](draft-prima-gara.md),
[Eventi live e SSE](eventi-live-e-sse.md),
[Database, migrazioni e concorrenza](database-migrazioni-e-concorrenza.md),
[Autenticazione, sessioni e ruoli](autenticazione-e-sessioni.md),
[Preparazione della prossima gara](setup-prossima-gara.md).

Allineamento controllato: si gioca solo dall'inventario sponsor con gara in corso, senza limite di
giocate; l'inventario non cambia durante la giocata e le copie disponibili sono quelle dell'inventario
meno le giocate non annullate; annullo solo dell'ultima giocata, massimo 5 consecutivi calcolati nel
backend; alla chiusura le giocate non annullate diventano `consumata` ed escono dall'inventario
tornando nella pool; revisione a revisore unico con scadenza di 15 minuti, rinuncia, conferma
dell'admin se scaduta o mai aperta e riapertura admin solo dell'ultima gara; bonus e rimozione senza
notifica; tasto S con estrazione ponderata sulle copie, riga `card_gift`, 1 punto sponsor e annullo
entro 60 secondi — corrispondono a `docs/PROJECT_SPEC.md:366-423` e `docs/PHASE_13_SPEC.md:9-51`.

**Discrepanza segnalata senza modifica:** `docs/PROJECT_SPEC.md:405` e `docs/PHASE_13_SPEC.md:34` affermano
che la revisione scaduta si conferma «alla prima richiesta successiva … senza processi in
background». Il codice registra invece un timer nel lifespan (`backend/app/main.py:32`,
`backend/app/main.py:37-58`), descritto come attivo in `docs/PHASE_15.md:88-89` e
`docs/PHASE_15_CARD_PLAY_EVENTS.md:9`; restano anche le chiusure su richiesta
(`backend/app/api/race/race_review.py:138-146`,
`backend/app/api/draft/draft.py:29-38`). La regola di gioco dei 15 minuti e della conferma così
com'è resta invariata: è il meccanismo descritto nei documenti a essere disallineato.
`docs/PHASE_15_TIMER.md:1-15` e alcune note di fase precedenti riportano ancora il timer «non attivo» e
vanno lette come storico superato. Nessun documento o codice è stato modificato per risolvere il
conflitto.

## Perimetro ed esclusioni

**Incluso:** giocate e annullamento del giocatore, tasto S e relative notifiche, chiusura delle
giocate, revisore unico, scadenza e timer, conteggi del revisore con bozza e conferma, riepilogo,
annullo di giocata, bonus e rimozione, inventario per la revisione, eventi di invalidazione, client
e store frontend delle carte e della revisione.

**Escluso:** acquisto di pacchetti e negozio (futura scheda); amministrazione delle immagini e delle
pool (futura scheda); punti sponsor e classifica (scheda
[Gare, risultati e classifica](gare-risultati-e-classifica.md)); trasporto SSE generale (scheda
[Eventi live e SSE](eventi-live-e-sse.md)); database SQLite reale, test, CI e browser.

Questa scheda è proprietaria di: `card_play`, `card_gift`, `card_judge`, `card_play_close`, del
registro `card_play`/`card_gift`, di `race_review` e dei moduli `review_*`, dei client `cards` e
`race/review` e degli store `review-counts`/`race-review`. La revisione come stato della gara e
l'effetto dei primi risultati sono già descritti nella scheda delle gare.

## Revisione e stato del worktree esaminati

- Revisione: `21e17e637b43528d7320e88f0af5623db7158ee9`; branch
  `feat/0.9-mappe-eventi` in tracking con `origin/feat/0.9-mappe-eventi`.
- Worktree invariato rispetto alle schede precedenti: tre file tracciati modificati in fasi
  documentali precedenti e due directory non tracciate. Qui si aggiungono solo scheda e link.
- Non sono stati eseguiti test, né ispezionato il database reale o usato il browser.

## Punti d'ingresso e flusso

### API e contratto

- Router registrati con prefisso `/api/championships`: giocate/regali, conferma selettiva,
  revisione e conteggi; il timer è avviato nel lifespan:
  `backend/app/main.py:21-25`, `backend/app/main.py:37-58`,
  `backend/app/main.py:71-76`.
- Lettura stato giocate, giocata, annullo, tasto S, annullo regalo, notifiche e `seen`: una sola
  traduzione centralizzata degli errori di dominio in 403/404/409:
  `backend/app/api/cards/card_play.py:41-49`,
  `backend/app/api/cards/card_play.py:52-108`,
  `backend/app/api/cards/card_play.py:111-191`.
- `seen-selected` accetta solo ID positivi int64, almeno 1 e al massimo 100 per richiesta, senza
  campi extra: `backend/app/api/cards/card_gift_seen.py:15-31`,
  `backend/app/schemas/cards/card_gift_seen.py:9-15`.
- DTO: richieste di giocata/annullo/regalo, stato con giocate, copie disponibili, annulli rimasti e
  `in_review`; inventario del revisore con `total`, `remaining`, `gifted`, `start`, `pool_now` e
  `pool_max`: `backend/app/schemas/cards/card_play.py:6-41`,
  `backend/app/schemas/cards/card_gift.py:6-18`,
  `backend/app/schemas/cards/card_judge.py:6-41`,
  `backend/app/schemas/race/review_inventory.py:4-30`.
- Stato revisione con revisore e scadenza solo se attiva, data di chiusura e `is_last_race`:
  `backend/app/schemas/race/race_review.py:6-19`.
- Conteggi: `extra="forbid"`, quantità intere non negative, nomi ripuliti e senza duplicati per
  pilota; conversione in coppie `(pilota, nome normalizzato) -> quantità`:
  `backend/app/schemas/race/review_counts.py:6-58`.
- Rotte revisione: GET (prima chiude le scadute), POST/DELETE, conferma legacy, riapertura,
  inventario, riepilogo, annullo giocata, bonus e rimozione:
  `backend/app/api/race/race_review.py:76-90`,
  `backend/app/api/race/race_review.py:93-135`,
  `backend/app/api/race/race_review.py:138-224`,
  `backend/app/api/race/race_review.py:227-291`.
- Rotte conteggi: GET/PUT bozza e POST `counts/confirm`; il 409 conserva solo la bozza e restituisce
  le incongruenze strutturate: `backend/app/api/race/review_counts.py:15-35`,
  `backend/app/api/race/review_counts.py:38-74`.

### Servizi e persistenza descritta

- `card_play`: gara in corso senza risultati per scrivere, più recente non confermata per leggere;
  solo proprietario iscritto e campionato attivo; blocco in revisione; copie disponibili calcolate
  dall'inventario meno le giocate attive; 5 annulli consecutivi dal registro; giocata, annullo,
  eventi e commit nella stessa transazione con rollback:
  `backend/app/services/cards/card_play.py:18-19`,
  `backend/app/services/cards/card_play.py:60-111`,
  `backend/app/services/cards/card_play.py:113-160`,
  `backend/app/services/cards/card_play.py:163-212`.
- Tasto S: admin/giudice su qualsiasi iscritto, giocatore solo sui propri; estrazione ponderata
  sulle copie; pool e inventario aggiornati con riga `card_gift` ed eventi in un solo commit;
  annullo entro 60 secondi solo admin/giudice, stessa gara e copia ancora disponibile:
  `backend/app/services/cards/card_gift.py:25-29`,
  `backend/app/services/cards/card_gift.py:52-140`,
  `backend/app/services/cards/card_gift.py:143-205`.
- Notifiche regalo: elenco di quelle con `seen_at` vuoto e marcatura come viste; la variante
  selettiva tocca solo gli ID richiesti del pilota:
  `backend/app/services/cards/card_gift.py:207-237`,
  `backend/app/services/cards/card_gift_seen.py:16-52`.
- Chiusura: le giocate non annullate tolgono una copia ciascuna dall'inventario e la restituiscono
  alla pool del campionato, passando a `consumata`; la carta senza pool esce comunque
  dall'inventario: `backend/app/services/cards/card_play_close.py:10-64`.
- Revisore unico: le azioni di correzione richiedono revisione attiva aperta dall'utente; annullo
  di giocata consumata riporta la carta dalla pool se disponibile; bonus e rimozione spostano una
  copia tra pool e inventario senza creare `card_gift`:
  `backend/app/services/cards/card_judge.py:40-117`,
  `backend/app/services/cards/card_judge.py:118-205`.
- Revisione: 15 minuti da `review_started_at`; apertura, rinuncia, conferma legacy, scadenza e
  riapertura admin dell'ultima gara, ciascuna con lock, ricontrollo ed eventi nella stessa
  transazione: `backend/app/services/race/race_review.py:15`,
  `backend/app/services/race/race_review.py:18-84`,
  `backend/app/services/race/race_review.py:92-228`.
- Timer per worker: sweep periodico con sessioni brevi, isolamento degli errori per campionato e
  arresto cooperativo; la chiusura scaduta resta `settle_expired_reviews`:
  `backend/app/services/race/review_timer.py:19-86`,
  `backend/app/services/race/race_review.py:153-200`.
- Conteggi: bozza salvata senza muovere carte; conferma costruisce un piano senza scritture, applica
  i saldi finali ad inventari e pool, allinea il registro e chiude la gara solo senza
  incongruenze; gli eventi non contengono carte né conteggi:
  `backend/app/services/race/review_commit.py:23-96`,
  `backend/app/services/race/review_commit.py:99-149`,
  `backend/app/services/race/review_commit.py:152-188`,
  `backend/app/services/race/review_plan.py:6-112`.
- Scadenza con bozza: applica solo le carte coerenti, lascia invariate le incongruenti e mantiene la
  bozza se restano blocchi; senza bozza usa la chiusura legacy:
  `backend/app/services/race/review_expiry.py:15-52`,
  `backend/app/services/race/race_review.py:153-200`.
- Inventario revisione in sola lettura: totali che sommano le consumate, rimanenti che sottraggono
  le attive, bonus dal conteggio dei regali e massimi dalla pool prototype:
  `backend/app/services/race/review_inventory.py:18-33`,
  `backend/app/services/race/review_inventory.py:42-50`,
  `backend/app/services/race/review_inventory.py:53-131`.
- Eventi: `race.review_changed` e `cards.changed` senza nomi o quantità; giocate e regali hanno
  notifiche private al proprietario e invalidazioni pubbliche:
  `backend/app/services/race/review_events.py:10-40`,
  `backend/app/services/cards/card_events.py:1-29`,
  `backend/app/services/cards/gift_events.py:1-31`.
- Modelli: registro giocate con stato `giocata`/`annullata`/`consumata` e indici su gara e pilota;
  regali con `seen_at` e protezione contro ID riciclati:
  `backend/app/db/models/card_play.py:6-30`,
  `backend/app/db/models/card_gift.py:7-26`.
- **Schema SQLite effettivo non verificato**: colonne, indici e vincoli derivano dai modelli; il
  database reale non è stato ispezionato.

### Frontend

- Client giocate e regali: lettura, giocata e annullo rileggono lo stato dal server; tasto S,
  annullo, notifiche e conferma selettiva; intervallo di controllo configurabile:
  `frontend/src/lib/cards/card-play-api.ts:10-110`,
  `frontend/src/lib/cards/card-play-types.ts:4-53`.
- Notifiche: lettura di snapshot completi per pilota, Ack solo degli ID mostrati, in lotti da 100;
  il controller di popup non conferma gli annulli remoti e non crea timer:
  `frontend/src/lib/cards/gift-notifications-api.ts:10-88`,
  `frontend/src/lib/cards/gift-popup-controller.ts:12-89`.
- Client revisione storica (apertura, rinuncia, conferma legacy, riepilogo, correzioni) e formattazione
  del conto alla rovescia: `frontend/src/lib/race/race-review-api.ts:10-74`,
  `frontend/src/lib/race/race-review-types.ts:4-35`,
  `frontend/src/lib/race/race-review-format.ts:3-28`.
- Client conteggi: bozza e conferma con `ReviewConflictError` che conserva le incongruenze del 409:
  `frontend/src/lib/race/review/review-counts-api.ts:5-106`,
  `frontend/src/lib/race/review/review-counts-types.ts:1-36`.
- Regole pure: aggiustamento entro `0..total`, conversione in richiesta, merge della bozza server e
  riconciliazione con conflitti/blocco espliciti invece di scarti silenziosi:
  `frontend/src/lib/race/review/review-counts.ts:3-32`,
  `frontend/src/lib/race/review/review-draft.ts:3-33`,
  `frontend/src/lib/race/review/review-inventory-reconcile.ts:5-151`.
- Store conteggi: chiave di revisione propria verificata prima di ogni scrittura, snapshot live con
  un solo client condiviso, backup locale prima delle sostituzioni, conferma solo con tutte le spunte:
  `frontend/src/lib/stores/review-counts.svelte.ts:40-104`,
  `frontend/src/lib/stores/review-counts.svelte.ts:226-350`,
  `frontend/src/lib/stores/review-counts.svelte.ts:347-541`.
- Store revisione legacy: stato, riepilogo, conto alla rovescia locale e azioni del revisore:
  `frontend/src/lib/stores/race-review.svelte.ts:15-141`.
- Pannello: wizard per pilota con `+`/`−`, spunta «Controllato», conferma, rinuncia, rilettura con
  backup e finestre di conflitto/incongruenza; testo che spiega l'applicazione automatica della
  bozza alla scadenza: `frontend/src/lib/components/race/race-review-panel.svelte:12-82`,
  `frontend/src/lib/components/race/race-review-panel.svelte:84-240`,
  `frontend/src/lib/components/race/review-pilot-inventory.svelte:5-51`,
  `frontend/src/lib/components/race/review-incongruence-dialog.svelte:4-25`.

## Test individuati (non eseguiti in questa fase)

- `backend/tests/test_card_plays.py`, `backend/tests/test_card_gift_undo.py`,
  `backend/tests/test_card_gifts.py`, `backend/tests/test_card_gift_seen_selected.py` — giocate,
  annullo, tasto S e notifiche.
- `backend/tests/test_card_judge.py`, `backend/tests/test_card_judge_reopen.py`,
  `backend/tests/test_card_judge_expired.py` — revisore, riapertura e scadenza.
- `backend/tests/test_race_review.py`, `backend/tests/test_race_review_reopen.py` — stato e
  riapertura della revisione.
- `backend/tests/test_review_commit.py`, `backend/tests/test_review_plan.py`,
  `backend/tests/test_review_counts_api.py`, `backend/tests/test_review_counts_schema.py`,
  `backend/tests/test_review_inventory.py`, `backend/tests/test_review_expiry_counts.py` —
  bozza, piano, conferma, inventario e scadenza con conteggi.
- `backend/tests/test_review_timer.py`, `backend/tests/test_review_timer_lifespan.py`,
  `backend/tests/test_review_concurrency.py` — timer, lifespan e concorrenza.
- `backend/tests/test_card_play_events.py`, `backend/tests/test_card_gift_events.py`,
  `backend/tests/test_card_judge_events.py`, `backend/tests/test_review_commit_events.py`,
  `backend/tests/test_review_close_events.py`, `backend/tests/test_review_state_events.py` —
  eventi e atomicità.
- `frontend/src/lib/cards/*.spec.ts`, `frontend/src/lib/race/review/*.spec.ts`,
  `frontend/src/lib/race/race-review.test.ts` — client, controller, riconciliazione e store.

Nessun test è stato eseguito durante la generazione della scheda. I risultati riportati nei
documenti di fase e in `docs/PROJECT_STATUS.md` sono riferiti a fasi diverse e non qui ri-osservati.

## Osservato, dedotto e non verificato

- **Osservato:** router, DTO, modelli, servizi, componenti e test citati; documenti canonici e note
  di fase, incluse le affermazioni disallineate sul timer.
- **Dedotto dal codice:** l'inventario sponsor non cambia quando si gioca una carta; la scadenza
  può chiudere una revisione anche senza richieste dell'utente; una bozza con incongruenze non
  applica le carte coinvolte; gli eventi pubblici non espongono nomi o quantità di carte; il client
  blocca la conferma se il contesto o la chiave di revisione cambiano.
- **Non verificato:** database SQLite reale, esecuzione test, browser, CI e il comportamento
  effettivo del timer in runtime con più worker.

## Fonti da ricontrollare quando cambiano le fonti pertinenti

- `backend/app/main.py`, `backend/app/api/cards/`, `backend/app/api/race/`,
  `backend/app/schemas/cards/`, `backend/app/schemas/race/`, `backend/app/db/models/card_*.py`.
- `backend/app/services/cards/` e `backend/app/services/race/` per giocate, revisione, eventi e
  timer.
- `frontend/src/lib/cards/`, `frontend/src/lib/race/`, `frontend/src/lib/stores/` e
  `frontend/src/lib/components/race/`.
- I test elencati sopra e i documenti canonici linkati all'inizio. Se cambiano la durata della
  revisione, il revisore unico, i limiti di annullo, le regole del tasto S o il meccanismo di
  scadenza, aggiornare qui i rimandi a `PROJECT_SPEC.md` e alle note di fase.
