# Gare, risultati e classifica

Mappa delle fonti, non requisito approvato: le regole autorevoli sono in `PROJECT_SPEC.md`.

## Documenti canonici

- [Indice della KB](../INDICE.md)
- [Specifiche di gioco](../../PROJECT_SPEC.md) — sezione 9 (campionati, gare e classifica) e
  sezione 14 (rapporto con le carte sponsor).
- [Mappa del codice](../../PROJECT_NOTES.md) — sezioni “Gare” e “Live e lifecycle”.
- [Stato del progetto](../../PROJECT_STATUS.md) — avanzamento, non specifica.
- [Database](../../DATABASE.md) — schema descritto, non database reale.
- [Draft: specifiche](../../DRAFT_SPEC.md) — il Guard drafts precede l'avvio della gara.
- Note storiche: [Fase 13](../../PHASE_13_SPEC.md),
  [Eventi live gara fase 15](../../PHASE_15_RACE_EVENTS.md),
  [Gara live fase 15](../../PHASE_15_RACE_LIVE.md),
  [Riconciliazione risultati fase 15](../../PHASE_15_RACE_RESULT_RECONCILE.md),
  [Revisione eventi fase 15](../../PHASE_15_REVIEW_EVENTS.md).

Schede collegate esistenti: [Campionati e iscrizioni](campionati-e-iscrizioni.md),
[Team, piloti e mazzi](team-piloti-e-mazzi.md), [Eventi live e SSE](eventi-live-e-sse.md),
[Database, migrazioni e concorrenza](database-migrazioni-e-concorrenza.md),
[Preparazione della prossima gara](setup-prossima-gara.md).

Allineamento controllato: numerazione automatica, una sola gara in corso, massimo 12 piloti,
punti per posizione, assenti dichiarati a mano, correzione solo admin, oro assegnato una sola
volta, classifica con pari merito e stato “in revisione” come sotto-stato della gara corrispondono
a `PROJECT_SPEC.md`. Le note di fase sono cronologia dichiarata. Non è emersa una discrepanza
irrisolta tra specifiche e codice. Una docstring interna
(`backend/app/services/race/race_deck_readiness.py:38-58`) dice ancora che il controllo non è
collegato ad avvio gara “in questo incremento”; il chiamante effettivo
(`backend/app/services/race/races.py:98-100`) lo invoca, quindi per il flusso si è seguito il
codice chiamante. Segnalazione senza modifica: il commento è potenzialmente obsoleto.

## Perimetro ed esclusioni

**Incluso:** creazione della gara e relative precondizioni, calendario e stato, inserimento e
correzione dei risultati, punti e saldi oro/sponsor, suggerimento dei punti dai tasti S, classifica
viva come consumo del servizio campionati, modulo frontend dei risultati, riconciliazione live e
avviso di uscita con bozza non salvata.

**Escluso:** sequenza SETUP GARA → AVVIA GARA (scheda pilota dedicata), regole del tasto S e
della revisione carte nei loro dettagli, acquisti e pacchetti, gestione delle pool, emissione
generale degli eventi, database SQLite reale ed esecuzione test. La revisione compare qui solo
come stato derivato e come effetto della prima registrazione risultati.

Questa scheda è proprietaria di: `race`, `race_result`, validazione dei risultati, effetti su
punti/sponsor/oro e relativi eventi, modulo risultati e riconciliazione live. La classifica del
campionato e la sua versione congelata sono descritte in
[Campionati e iscrizioni](campionati-e-iscrizioni.md); qui se ne documenta solo il consumo.

## Revisione e stato del worktree esaminati

- Revisione: `21e17e637b43528d7320e88f0af5623db7158ee9`; branch
  `feat/0.9-mappe-eventi` in tracking con `origin/feat/0.9-mappe-eventi`.
- Worktree invariato rispetto alle schede precedenti: tre file tracciati modificati in fasi
  documentali precedenti e due directory non tracciate. Qui si aggiungono solo scheda e link.
- Non sono stati eseguiti test, né ispezionato il database reale o usato il browser.

## Punti d'ingresso e flusso

### API e contratto

- Router gare registrato con prefisso `/api/championships`, insieme a quello dei campionati:
  `backend/app/main.py:69-70`.
- Quattro stati: `in_progress` senza risultati, `in_review` con revisione attiva, `to_review`
  con risultati e revisione non aperta/non confermata, `closed` dopo la conferma:
  `backend/app/schemas/race/race.py:6-8`,
  `backend/app/api/race/races.py:43-52`.
- DTO: creazione con data facoltativa, risultato con pilota e punti sponsor non negativi,
  elenco ordinato con `absent`, lettura con posizione/punti e suggerimento sponsor, classifica
  con `rank`, nome, punti e gare disputate: `backend/app/schemas/race/race.py:11-27`,
  `backend/app/schemas/race/race.py:30-59`.
- Elenco gare per numero, creazione giudice/admin 201/404/409, dettaglio per utenti collegati:
  `backend/app/api/race/races.py:84-127`.
- `PUT .../results` termina o corregge: passa `can_correct` solo per admin, `reviewer_id` a chi
  preme Termina e traduce errori di dominio in 403/404/422:
  `backend/app/api/race/races.py:129-157`.
- `GET .../standings` restituisce tutti gli iscritti; nei campionati chiusi usa la classifica
  congelata con `pilot_id` nullo: `backend/app/api/race/races.py:160-176`.
- Lo stato della revisione è leggibile da ogni utente collegato e riporta revisore, scadenza e
  flag “ultima gara”; i dettagli operativi sono fuori da questa scheda:
  `backend/app/api/race/race_review.py:76-90`,
  `backend/app/schemas/race/race_review.py:6-19`.

### Servizi e persistenza descritta

- Punti 9/6/4/3/2/1 dalle posizioni 1 a 6, poi 0; limite 12 piloti. Errori dedicati per gara
  mancante, già chiusa, in corso, conflitto di lock e risultati non validi:
  `backend/app/services/race/races.py:24-46`.
- Una gara resta non conclusa finché mancano risultati o manca la conferma della revisione;
  elenco e ricerca per campionato: `backend/app/services/race/races.py:49-75`.
- Avvio sotto lock condiviso: campionato attivo, nessuna gara conclusa incompleta, nessun draft,
  mazzi da gioco pronti, numero successivo, data di creazione, evento `race.started` e commit
  unico; conflitti di lock tradotti senza retry:
  `backend/app/services/race/races.py:78-127`.
- Idoneità mazzi: 15 copie per ogni iscritto, compresi i nascosti, senza esporre carte;
  mancanza del mazzo o JSON non valido sono errori distinti da “count zero”:
  `backend/app/services/race/race_deck_readiness.py:17-23`,
  `backend/app/services/race/race_deck_readiness.py:38-70`,
  `backend/app/services/race/race_deck_snapshot.py:16-46`.
- `count_participants` conta le righe risultato; `set_results` acquisisce il lock, chiama la
  validazione e fa un solo commit con rollback su qualsiasi errore:
  `backend/app/services/race/races.py:130-159`.
- Validazione: almeno un risultato, non più di 12, nessun duplicato o sponsor negativo, piloti
  iscritti, assenti non sovrapposti e copertura di tutti gli iscritti quando la lista assenti è
  presente: `backend/app/services/race/races.py:162-199`.
- Scrittura: la posizione deriva dall'ordine, i punti dalla tabella; vengono risincronizzati
  `Pilot.point`, applicato il solo delta sponsor (mai sotto zero) e, alla prima chiusura,
  assegnato l'oro con le regole del campionato e azzerati i percorsi della prossima gara:
  `backend/app/services/race/races.py:200-223`,
  `backend/app/services/race/races.py:226-238`.
- Prima registrazione con revisore indicato: apre la revisione e accoda `race.results_changed` e
  `standings.changed` nella stessa transazione; una correzione non riapre la revisione e non
  riassegna l'oro: `backend/app/services/race/races.py:209-223`.
- Punti sponsor suggeriti derivano dal conteggio dei tasti S della gara; annullamento entro 60
  secondi li rimuove. Il dettaglio mostra prima i partecipanti per posizione, poi gli assenti a
  zero: `backend/app/services/race/races.py:241-266`.
- Classifica viva: totale dei punti, pari merito con stessa posizione; campionato chiuso usa la
  classifica congelata, con fallback ai risultati se non esistono righe congelate:
  `backend/app/services/championship/championships.py:259-320`.
- Modelli descritti: `race` con numero unico per campionato, date revisione/campi bozza;
  `race_result` con posizione 1–12, punti, sponsor non negativo e unicità gara/pilota e
  gara/posizione: `backend/app/db/models/race.py:5-24`,
  `backend/app/db/models/race.py:27-42`.
- **Schema SQLite effettivo non verificato**: colonne e vincoli elencati derivano dai modelli; il
  database reale non è stato ispezionato.

### Frontend

- Pagina gara: snapshot live di gara, campionato e piloti propri con `startLiveRefresh`, filtro
  per campionato e `dispose` al cambio contesto:
  `frontend/src/routes/championships/[id]/races/[raceId]/+page.svelte:20-89`,
  `frontend/src/routes/championships/[id]/races/[raceId]/+page.svelte:144-204`.
- Traduzione REST in modulo: i risultati con posizione diventano ordine, chi non ha partecipato
  finisce tra gli assenti solo se la gara ha risultati:
  `frontend/src/routes/championships/[id]/races/[raceId]/+page.svelte:95-137`.
- Permessi derivati: modifica se campionato attivo e ruolo abilitato; correzione e revisione
  estese richiedono il ruolo admin o lo stato appropriato:
  `frontend/src/routes/championships/[id]/races/[raceId]/+page.svelte:48-89`.
- Assegnazione piloti, riordino e normalizzazione locale dei punti sponsor prima dell'invio:
  `frontend/src/routes/championships/[id]/races/[raceId]/+page.svelte:207-234`.
- Salvataggio esplicito con `PUT .../results`, verifica locale di copertura degli ID e
  riconciliazione con la risposta; la PUT non viene annullata da un cambio di contesto:
  `frontend/src/routes/championships/[id]/races/[raceId]/+page.svelte:236-290`.
- Uscita con bozza sporca: popup con “Esci”/“Rimani” per navigazioni interne e avviso del
  browser per ricarica/chiusura:
  `frontend/src/routes/championships/[id]/races/[raceId]/+page.svelte:292-308`,
  `frontend/src/routes/championships/[id]/races/[raceId]/+page.svelte:538-559`.
- Interfaccia: risultati in sola lettura, pannello revisione montato solo se abilitato, tasto S
  con gara in corso, modulo “Termina la gara”/“Correggi i risultati” con massimo 12 piloti e
  assegnazione obbligatoria di tutti gli iscritti:
  `frontend/src/routes/championships/[id]/races/[raceId]/+page.svelte:363-420`,
  `frontend/src/routes/championships/[id]/races/[raceId]/+page.svelte:421-535`.
- Etichetta uniforme dello stato: `to_review` è mostrato come “in revisione”:
  `frontend/src/lib/race/race-status.ts:3-26`.
- Tipi condivisi per gara, risultato, input e classifica: `frontend/src/lib/race/race-types.ts:1-45`.
- Rilevamento modifiche e merge a tre vie: nomi non editabili, ordine significativo, assenti
  senza ordine, conflitti su sponsor e assegnazioni conservate:
  `frontend/src/lib/race/race-result-reconcile.ts:14-48`,
  `frontend/src/lib/race/race-result-reconcile.ts:50-99`.
- Suggerimento sponsor: valore salvato se il risultato ha posizione, altrimenti somma dei tasti S;
  il campo resta modificabile: `frontend/src/lib/race/race-sponsor-suggestion.ts:3-13`.

## Test individuati (non eseguiti in questa fase)

- `backend/tests/test_races_api.py:106-158` — permessi, numerazione, punti e assenti a zero.
- `backend/tests/test_races_api.py:158-220` — validazione liste, duplicati e sponsor non negativi.
- `backend/tests/test_races_api.py:220-292` — correzione admin, differenze sponsor e rimborsi.
- `backend/tests/test_races_api.py:300-400` — classifica, pareggi, congelamento e fallback.
- `backend/tests/test_race_status.py:20-67` — quattro stati e riapertura della revisione.
- `backend/tests/test_race_events.py:18-84` — eventi di creazione/finish/correzione e rollback.
- `backend/tests/test_race_start_readiness.py` e `backend/tests/test_race_start_write_lock.py` —
  precondizioni dei mazzi e conflitti di avvio.
- `backend/tests/test_race_deck_snapshot.py` e `backend/tests/test_race_deck_readiness.py` —
  lettura DB e valutazione pura dei mazzi.
- `frontend/src/lib/race/race-status.spec.ts`,
  `frontend/src/lib/race/race-result-reconcile.spec.ts`,
  `frontend/src/lib/race/race-sponsor-suggestion.spec.ts` — etichette, merge e suggerimenti.

Nessun test è stato eseguito durante la generazione della scheda.

## Osservato, dedotto e non verificato

- **Osservato:** router, servizi, DTO, modelli, pagina gara, funzioni frontend e test citati.
- **Dedotto dal codice:** lo stato `to_review` non è mostrato agli utenti come nome distinto; la
  prima registrazione risultati apre la revisione, ma il consumo delle carte avviene solo alla
  conferma; una correzione non riassegna oro né riapre la revisione.
- **Non verificato:** database SQLite reale, esecuzione test, browser, CI, pubblicazione degli
  eventi in runtime e comportamento della docstring obsoleta segnalata all'inizio.

## Fonti da ricontrollare quando cambiano le fonti pertinenti

- `backend/app/main.py`, `backend/app/api/race/` e `backend/app/schemas/race/race.py`.
- `backend/app/services/race/races.py`, `backend/app/services/race/race_review.py`,
  `backend/app/services/race/race_deck_readiness.py`,
  `backend/app/services/race/race_deck_snapshot.py`,
  `backend/app/services/championship/championships.py`, `backend/app/db/models/race.py`.
- `frontend/src/routes/championships/[id]/races/[raceId]/+page.svelte` e `frontend/src/lib/race/`.
- I test elencati sopra e i documenti canonici linkati all'inizio. Se cambiano stato gara,
  punteggio, correzioni o documenti di fase, aggiornare qui i rimandi a `PROJECT_SPEC.md`.
