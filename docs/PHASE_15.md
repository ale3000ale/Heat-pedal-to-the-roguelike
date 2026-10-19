# Fase 15 - SSE in tempo reale e sistemazione

Aggiornamento: 2026-10-20. Ramo esclusivo: phase-15-sse-sistemazione.
Base iniziale main: 2cded6d. PR provvisoria 14, in bozza; nessun merge senza richiesta.

## Decisioni approvate

- Applicazione predisposta anche per uso online a bassa affluenza e piu' worker.
- Eventi per carte ottenute/annullate, giocate, stato gara/revisione, risultati e classifica.
- Polling e card_poll_seconds mantenuti come fallback; rimozione rinviata.
- Timer backend per revisioni scadute, oltre alla conferma alla prima richiesta.
- Scelta della rete affidata alla verifica tecnica: api.ts e vite.config.ts usano
  gia' /api same-origin con proxy verso FastAPI. Non sono chiamate cross-origin.
- Documenti grandi PROJECT_SPEC.md e PROJECT_STATUS.md lasciati intatti;
  questo documento e le note PHASE_15 raccolgono le integrazioni.

## Avanzamento

- 15a-1: contratto Pydantic, modello event_log, migrazione d5e9a3b7c1f6,
  servizio transazionale e test pubblicati. CI verde su 54079f7 (run 39341481995).
- Correzione del test Alembic storico: CI verde su 47df2a5, vedi PHASE_15_CI_FIX.md.
- 15a-2: endpoint e servizio SSE introdotti in questo blocco; test scritti ma non
  eseguiti localmente. Nuova CI da leggere dopo il push; nessun successo presunto.
- 15a-3: pubblicazione degli eventi nelle azioni e timer ancora da implementare.
- 15a-4: client frontend e fallback ancora da implementare.
- 15b: sistemazione generale da definire con l'autore dopo SSE.

## Registro ed endpoint

Dettagli SQL: PHASE_15_DATABASE.md. Dettagli servizio: PHASE_15_SERVICE.md.
La conservazione pianificata e' di 24 ore. Il servizio di pulizia esiste ma non
viene ancora eseguito automaticamente. Il registro e' condiviso tra worker.
GET /api/events/stream usa cookie, Last-Event-ID, letture ogni secondo,
keep-alive ogni 15 secondi e retry SSE di 3 secondi. Nessuna nuova dipendenza.
Ogni lettura chiude la sessione SQL prima di attese o invio; SQL nel thread pool.
La sessione autenticata viene ricontrollata a ogni lettura: revoca/scadenza
produce auth.expired e chiusura. Il client dovra' chiudere EventSource su tale evento.
Il primo accesso emette resync; un cursore anteriore ai dati disponibili o oltre
la sequenza corrente richiede resync. Il client dovra' ricaricare lo stato REST.
La sequenza AUTOINCREMENT permette di rilevare anche un registro svuotato.
Un resync puo' essere conservativo se gli id mancanti appartengono ad altri utenti.
I privati sono visibili solo al destinatario; gli eventi pubblici agli iscritti
con pilota non eliminato e ad admin/giudici. Mai dettagli privati nei payload pubblici.

## File del blocco endpoint

Nuovi: backend/app/api/events.py, backend/app/services/event_stream.py,
backend/tests/test_events_stream.py. Modificati: backend/app/main.py e questo file.
Test: parsing cursore, frame JSON, replay, revoca, registro svuotato, cursore futuro,
autenticazione HTTP e header. Lo stream HTTP dei test e' finito tramite sostituzione:
non e' una prova end-to-end di una connessione lunga o del proxy.
Nessuna prova browser, di buffering proxy o di carico ancora eseguita.
SSE non e' ancora collegato alle azioni o al frontend: non dichiariamo l'app real-time.

## Database reale e verifiche

Nessuna migrazione applicata ai dati del gioco e nessun backup effettuato.
Prima della migrazione reale: backup verificato e prova su copia obbligatori.
La CI usa un database nuovo del runner e non sostituisce la verifica sui dati reali.
La catena dei 19 file storici e' stata letta: testa precedente a2e6c0d4f8b3;
merge storico b2d6f0a4c8e1 dei rami negozio e oro. Vedi PHASE_15_DATABASE.md.

## Sistemazioni e riallineamenti pendenti

- PROJECT_STATUS.md: riga 14 ancora da definire, manca 15, data vecchia e descrizione
  13e incompleta; integrazioni correnti raccolte qui, senza riscrivere il file.
- PROJECT_SPEC.md: rilettura dopo bc0fbfb e verifica del refuso storico da completare.
- PHASE_14_POST_MERGE.md: aae6c33 e' un riferimento storico; esito dell'automazione
  format-championships.yml non verificato in questa fase.
- DATABASE.md letto: schema storico; delta SSE in PHASE_15_DATABASE.md.
- README.md, SETUP.md, SCRIPTS.md, SHOP_DESIGN.md e PROJECT_NOTES.md da rileggere
  prima di ulteriori riallineamenti. Backup/setup sicuro ancora da verificare nel codice.
- config.py ha cookie secure disattivato e URL SQLite fisso: configurazione online
  da sistemare prima della consegna online. Non modificata in questi blocchi.
- Differenza storica del formato Deck.cards nelle istruzioni e nel codice segnalata
  da DATABASE.md: nessun cambio al formato o ai percorsi in questa fase.

## Metodo

Sottofasi approvate una alla volta, conferma puntuale prima dei push.
Dopo CI verde riallineare i documenti piccoli interessati e raccogliere qui i delta
non applicati ai documenti grandi. Nessun test locale o risultato viene inventato.
