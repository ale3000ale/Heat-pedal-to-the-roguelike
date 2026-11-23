# Campionati e iscrizioni

Mappa delle fonti, non requisito approvato: le regole autorevoli sono in `PROJECT_SPEC.md`.

## Documenti canonici

- [Indice della KB](../INDICE.md)
- [Specifiche di gioco](../../PROJECT_SPEC.md) — sezioni 7–9: ruoli, iscrizione, campionati,
  regole dell'oro e classifica.
- [Mappa del codice](../../PROJECT_NOTES.md) — convenzioni e sezione “Live e lifecycle”.
- [Stato del progetto](../../PROJECT_STATUS.md) — avanzamento, non specifica.
- [Database](../../DATABASE.md) — schema descritto dai modelli, non database reale.
- [Campionato live fase 15](../../PHASE_15_CHAMPIONSHIP_LIVE.md) e
  [Iscrizioni live fase 15](../../PHASE_15_ENROLLMENT_LIVE.md) — cronologia storica.

Schede collegate esistenti: [Team, piloti e mazzi](team-piloti-e-mazzi.md),
[Eventi live e SSE](eventi-live-e-sse.md),
[Database, migrazioni e concorrenza](database-migrazioni-e-concorrenza.md),
[Preparazione della prossima gara](setup-prossima-gara.md).

Allineamento controllato: creazione, chiusura e cancellazione admin, iscrizione con team e senza
campionato attivo, reset all'iscrizione e regole dell'oro copiate alla creazione corrispondono a
quanto descritto in `PROJECT_SPEC.md`. I documenti di fase 15 dichiarano il proprio carattere
storico; non è emersa una discrepanza irrisolta.

## Perimetro ed esclusioni

**Incluso:** creazione, elenco, dettaglio, chiusura e cancellazione dei campionati; iscrizione e
reset del pilota; copie delle pool e regole dell'oro; classifica viva e congelata; pagine e
coordinatore live del campionato.

**Escluso:** gestione delle pool di origine e caricamento carte (scheda amministrazione carte),
ciclo di vita di gare/risultati/revisione, acquisti e pacchetti, emissione degli eventi da altri
sottosistemi, database SQLite reale, esecuzione test. Il setup gara è solo richiamato come pulsante:
la sequenza è nella scheda pilota dedicata.

Questa scheda è proprietaria di: `championship`, `championship_pilot`,
`championship_defaults`, `championship_standing`, regole dell'oro e snapshot live del campionato.
Le schede funzionali citano l'iscrizione o le regole dell'oro senza ridescriverle.

## Revisione e stato del worktree esaminati

- Revisione: `21e17e637b43528d7320e88f0af5623db7158ee9`; branch
  `feat/0.9-mappe-eventi` in tracking con `origin/feat/0.9-mappe-eventi`.
- Worktree invariato rispetto alle schede precedenti: tre file tracciati modificati in fasi
  documentali precedenti e due directory non tracciate. Qui si aggiungono solo scheda e link.
- Non sono stati eseguiti test, né ispezionato il database reale o usato il browser.

## Punti d'ingresso e flusso

### API e contratto

- Router campionati con prefisso `/api/championships`; il router gare usa lo stesso prefisso:
  `backend/app/main.py:69-70`.
- DTO di creazione con nome 2–40, pool facoltative e template negozio, iscrizione con `pilot_id`,
  `EntrantRead`, `ChampionshipRead` e dettaglio con percorsi della prossima gara:
  `backend/app/schemas/championship/championship.py:8-24`,
  `backend/app/schemas/championship/championship.py:27-49`.
- Elenco di tutti i campionati, creazione solo admin 201/404/409/422, dettaglio per tutti:
  `backend/app/api/championship/championships.py:65-103`.
- Setup della prossima gara per admin/giudice con traduzione 409/503; avvio gara e draft non
  sono in questo router: `backend/app/api/championship/championships.py:106-127`.
- Regole dell'oro per campionato: lettura per tutti, modifica solo admin su campionato attivo:
  `backend/app/api/championship/championships.py:130-151`.
- Chiusura solo admin 409 se già chiuso; iscrizione con 404/409 per campionato chiuso, pilota
  senza team o già iscritto; cancellazione solo admin di campionato chiuso:
  `backend/app/api/championship/championships.py:154-197`.
- Impostazioni generali e intervallo notifiche nell'router admin:
  `backend/app/api/admin/admin.py:53-78`.

### Servizi e persistenza descritta

- Nome normalizzato con `name_key` unico; creazione con copie indipendenti delle pool di
  modifiche e sponsor, regole dell'oro copiate dalle impostazioni generali e pacchetti copiati
  dal template se indicato: `backend/app/services/championship/championships.py:91-139`.
- Se la pool sponsor di base non esiste, il campionato viene creato senza seconda pool:
  `backend/app/services/championship/championships.py:113-122`.
- Iscrizione sotto lock: nessun draft, campionato attivo, pilota proprio con team e non in altro
  campionato attivo; reset di inventari, mazzi, gold, sponsor e point; evento pubblico
  `championship.pilots_changed`, rollback su errore:
  `backend/app/services/championship/championships.py:177-203`.
- “Attivo” significa iscritto a un campionato non chiuso:
  `backend/app/services/pilots/teams.py:31-41`.
- Chiusura sotto lock: `is_closed=True`, azzeramento dei percorsi della prossima gara, congelamento
  della classifica e reset dei soli iscritti; rollback completo su errore:
  `backend/app/services/championship/championships.py:154-174`.
- Cancellazione di un campionato chiuso in un'unica transazione: giocate/regali/risultati/gare,
  iscrizioni, classifica congelata, pacchetti e storico acquisti, copie delle pool; piloti e
  file orfani gestiti dopo il commit: `backend/app/services/championship/championships.py:205-247`.
- Classifica viva dai risultati, con pari punti alla stessa posizione e nome usato solo per
  l'ordine di visualizzazione; chiuso usa la classifica congelata, con fallback ai risultati se
  non ci sono righe congelate: `backend/app/services/championship/championships.py:259-320`.
- Regole dell'oro: base, sei modificatori di posizione e modificatore “altre”; limiti e riga
  unica delle impostazioni generali; il totale non scende sotto zero:
  `backend/app/services/championship/gold.py:8-17`,
  `backend/app/services/championship/gold.py:20-43`,
  `backend/app/services/championship/gold.py:87-103`.
- Modelli con `name_key`, pool copiate, percorsi della prossima gara, tabella iscrizioni con
  vincolo di unicità e classifica congelata senza riferimento al pilota:
  `backend/app/db/models/championship.py:18-48`,
  `backend/app/db/models/championship.py:63-85`.
- **Schema SQLite effettivo non verificato**: colonne e vincoli elencati derivano dai modelli; il
  database reale non è stato ispezionato.

### Frontend

- Pagina Campionati: carica campionati e piloti, divide le sezioni Iscritto/Attivi/Chiusi, apre
  impostazioni e creazione solo per admin:
  `frontend/src/routes/championships/+page.svelte:37-75`,
  `frontend/src/routes/championships/+page.svelte:127-138`,
  `frontend/src/routes/championships/+page.svelte:243-258`.
- Raggruppamento e apertura iniziale della sezione:
  `frontend/src/lib/championship/championship-groups.ts:9-44`,
  `frontend/src/lib/championship/championship-groups.ts:46-54`.
- Dialog di creazione con nome, due pool e template negozio:
  `frontend/src/lib/components/championship/new-championship-dialog.svelte:72-83`.
- Pagina admin campionati con impostazioni generali e moduli; creazione senza template:
  `frontend/src/routes/admin/championships/+page.svelte:68-104`,
  `frontend/src/routes/admin/championships/+page.svelte:121-132`.
- Dettaglio campionato: snapshot live con `startChampionshipLive`, iscrizione, setup e aperture
  del draft; `dispose` invalida risposte tardive al cambio contesto:
  `frontend/src/routes/championships/[id]/+page.svelte:89-110`,
  `frontend/src/routes/championships/[id]/+page.svelte:112-175`,
  `frontend/src/routes/championships/[id]/+page.svelte:178-184`,
  `frontend/src/routes/championships/[id]/+page.svelte:197-264`.
- Snapshot REST: campionato, classifica, gare, piloti e notifiche dei soli piloti propri iscritti;
  nei campionati chiusi non si aprono notifiche:
  `frontend/src/lib/championship/championship-live.ts:32-58`,
  `frontend/src/lib/championship/championship-live.ts:97-125`.
- Candidati all'iscrizione: team presente e nessun campionato attivo; pulsante solo se non ci sono
  già iscritti dell'utente: `frontend/src/lib/championship/enroll-candidates.ts:3-25`.
- Impostazioni campionato: chiusura e cancellazione con conferma, regole dell'oro e pannello pool:
  `frontend/src/lib/components/championship/championship-settings.svelte:83-105`,
  `frontend/src/lib/components/championship/championship-settings.svelte:121-132`,
  `frontend/src/lib/components/championship/championship-settings.svelte:169-186`.
- Chiave `{#each}` della classifica: il rango non basta perché i pari merito lo condividono:
  `frontend/src/lib/championship/standings.ts:3-8`.

## Test individuati (non eseguiti in questa fase)

- `backend/tests/test_championships_api.py:125-175` — permessi admin, pool scelte e copie
  indipendenti.
- `backend/tests/test_championships_api.py:195-282` — chiusura, reset all'iscrizione, team e
  unicità del campionato attivo.
- `backend/tests/test_championships_api.py:296-359` — cancellazione solo da chiuso e storico
  rimosso.
- `backend/tests/test_championship_close_reset.py:52-86` — reset dei soli iscritti e classifica
  congelata conservata.
- `backend/tests/test_gold_rules.py:25-162` — copia delle regole, posizioni, limite a zero,
  modifiche valide dalla gara successiva e guard admin.
- `backend/tests/test_enrollment_events.py:44-115` — segnale di iscrizione senza dettagli e
  rollback se l'evento fallisce.
- `frontend/src/lib/championship/championship-groups.spec.ts`,
  `frontend/src/lib/championship/enroll-candidates.spec.ts`,
  `frontend/src/lib/championship/championship-live.spec.ts`,
  `frontend/src/lib/championship/standings.spec.ts` — raggruppamenti, candidati, snapshot live e
  chiavi di classifica.

Nessun test è stato eseguito durante la generazione della scheda.

## Osservato, dedotto e non verificato

- **Osservato:** router, servizi, modelli, trasformazioni del nome, snapshot live, pagine e test
  citati.
- **Dedotto dal codice:** l'iscrizione è libera finché il campionato è aperto, ma il reset
  azzera anche i progressi del pilota; la chiusura congela la classifica prima di resettare i
  piloti; il segnale di iscrizione non contiene dati dei piloti.
- **Non verificato:** database SQLite reale, esecuzione test, browser, CI, effettiva pubblicazione
  degli eventi in runtime.

## Fonti da ricontrollare quando cambiano le fonti pertinenti

- `backend/app/api/championship/championships.py`, `backend/app/api/admin/admin.py`,
  `backend/app/schemas/championship/`.
- `backend/app/services/championship/championships.py`, `backend/app/services/championship/gold.py`,
  `backend/app/services/pilots/teams.py`, `backend/app/db/models/championship.py`.
- `frontend/src/routes/championships/`, `frontend/src/routes/admin/championships/+page.svelte`,
  `frontend/src/lib/championship/`,
  `frontend/src/lib/components/championship/championship-settings.svelte`,
  `frontend/src/lib/components/championship/new-championship-dialog.svelte`.
- I test elencati sopra e i documenti canonici linkati all'inizio. Se cambiano le regole
  dell'oro o il reset, aggiornare qui i rimandi a `PROJECT_SPEC.md`.
