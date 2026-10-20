# Fase 15 - SSE in tempo reale e sistemazione

Aggiornamento: 2026-10-20. Ramo esclusivo: phase-15-sse-sistemazione.
Base iniziale main: 2cded6d. PR provvisoria 14 in bozza; nessun merge senza richiesta.
Questa pagina riassume lo stato corrente; le note PHASE_15 registrano i singoli blocchi.
Le indicazioni storiche "timer non attivo" nelle note precedenti descrivono quei commit.

## Decisioni approvate

- Predisposizione per uso online a bassa affluenza e piu' worker sullo stesso SQLite.
- Tutti gli eventi proposti: carte ottenute/annullate, giocate, stato gara/revisione,
  risultati e classifica. Non estende automaticamente SSE a ogni CRUD dell'app.
- Polling e card_poll_seconds mantenuti come fallback; rimozione rinviata.
- Timer backend per scadenza revisioni oltre alla conferma alla prima richiesta.
- Rete scelta dopo lettura di api.ts e vite.config.ts: /api same-origin tramite proxy
  verso FastAPI, non chiamate cross-origin. Buffering reale ancora da verificare.
- PROJECT_SPEC.md e PROJECT_STATUS.md lasciati intatti per richiesta dell'autore;
  integrazioni raccolte qui e nelle note PHASE_15.

## Avanzamento verificato

- 15a-1: contratto Pydantic, modello event_log, migrazione d5e9a3b7c1f6,
  servizio transazionale e test. CI verde su 54079f7 (run 39341481995).
- 15a-2: endpoint SSE autenticato e test; CI verde su a332633 (run 39342203544).
- 15a-3: eventi di conferma conteggi, conferma legacy, scadenza, apertura/rinuncia/
  riapertura/blocco/sblocco, creazione gara, Termina gara, risultati e classifica.
  CI verde su 39572e3 (run 39403393864).
- Test concorrenti pubblicati in 819e1c0: CI tutta verde (run 39403918209).
  Due processi spawn con connessioni indipendenti sullo stesso file SQLite sintetico:
  scadenza contro scadenza e scadenza contro conferma manuale. Una sola chiusura,
  un solo consumo/restituzione e una sola coppia di eventi.
- In questo blocco il timer viene collegato al lifespan. Test lifecycle scritti ma
  non eseguiti localmente: esito della nuova CI da verificare dopo il push.
- 15a-3 resta incompleta: eventi giocate/annullamenti/tasto S ancora da collegare.
- 15a-4: client SSE frontend e collegamento del fallback ancora da implementare.
- 15b: sistemazione generale da definire dopo SSE con l'autore.

## Timer e lifecycle

main.py avvia un task heat-review-timer per worker dopo la manutenzione iniziale.
Ogni 5 secondi cerca revisioni scadute con risultati in campionati aperti.
Riusa settle_expired_reviews: ricontrollo sotto lock e commit per gara con eventi
nella stessa transazione. Le bozze applicano le sole carte coerenti secondo la
logica esistente. La richiesta REST mantiene il controllo di scadenza preesistente.
La pulizia degli eventi oltre 24 ore parte al primo giro e poi ogni ora.
All'uscita, anche per errore nel corpo del lifespan, stop cooperativo e attesa del
task. Non viene interrotta a meta' una transazione; l'attesa dipende dal giro SQL.
Gli errori di giro sono loggati e ritentati. Nessuna migrazione automatica.

File del blocco: backend/app/main.py, backend/tests/test_review_timer_lifespan.py,
questo documento. Test: avvio/arresto normale e con errore nel corpo, startup
fallito senza task e timer reale su dati temporanei con prima scadenza osservata.
La prova lifecycle non e' una verifica di deployment o di traffico HTTP reale.

## Registro ed endpoint

SQL in PHASE_15_DATABASE.md; servizio in PHASE_15_SERVICE.md.
Registro persistente condiviso dai worker, id AUTOINCREMENT SQLite non riutilizzati.
Gli eventi sono accodati prima del commit dell'azione; rollback rimuove entrambi.
GET /api/events/stream: cookie, Last-Event-ID, letture ogni secondo, keep-alive ogni
15 secondi, retry SSE 3 secondi. Sessioni SQL brevi nel thread pool, chiuse prima
di invio/attesa. Sessione HTTP ricontrollata a ogni lettura; auth.expired chiude
lo stream e il futuro client dovra' chiudere EventSource.
Primo accesso o cursore non recuperabile inviano resync: il client ricarichera'
lo stato REST. Rilevato anche un registro svuotato con sqlite_sequence.
I privati sono visibili solo al destinatario; i pubblici agli iscritti con pilota
non eliminato e ad admin/giudici. Mai carte private, conteggi o bozze nei pubblici.
La conservazione e' 24 ore, con eliminazione periodica e non esatta al secondo.

## Note dei blocchi e correzioni

- PHASE_15_IMPLEMENTATION.md, PHASE_15_DATABASE.md, PHASE_15_SERVICE.md.
- PHASE_15_REVIEW_EVENTS.md, PHASE_15_LEGACY_EVENTS.md, PHASE_15_STATE_EVENTS.md,
  PHASE_15_RACE_EVENTS.md: transazioni ed eventi delle azioni implementate.
- PHASE_15_TIMER.md: modulo timer iniziale; ora collegato al lifecycle in questo blocco.
- PHASE_15_CONCURRENCY.md: test reali a due processi, non prove di carico o multi-host.
- PHASE_15_CI_FIX.md: asserzione Alembic storica, superata in CI su 47df2a5.
- PHASE_15_STATE_EVENTS_FIX.md: ID ORM dopo rollback, superata in CI su 53709a0.

## Database reale e limiti

Nessuna migrazione applicata ai dati del gioco e nessun backup reale effettuato.
Prima di usare questo ramo sui dati reali occorrono backup verificato e prova su
copia della migrazione, prima dell'avvio del backend. Nessun reset/cancellazione.
La CI usa database nuovi o sintetici: non sostituisce le verifiche sui dati reali.
Catena storica letta: testa precedente a2e6c0d4f8b3; merge storico b2d6f0a4c8e1.
Nessuna prova browser, connessione SSE lunga attraverso il proxy, carico o
filesystem di rete ancora eseguita. Non dichiariamo l'app completamente real-time.
Nessuna nuova dipendenza di questi blocchi. Test locali non eseguiti.

## Sistemazioni e riallineamenti pendenti

- PROJECT_STATUS.md: riga 14 vecchia, manca 15, data e descrizione 13e da riallineare.
- PROJECT_SPEC.md: rilettura dopo bc0fbfb e refuso storico da verificare.
- PHASE_14_POST_MERGE.md: aae6c33 e' storico; automazione format-championships non
  verificata in questa fase.
- DATABASE.md letto: delta SSE in PHASE_15_DATABASE.md. Prima di ulteriori
  aggiornamenti rileggere README.md, SETUP.md, SCRIPTS.md, SHOP_DESIGN.md,
  PROJECT_NOTES.md. Backup/setup sicuro da verificare nel codice.
- config.py: cookie secure disattivato e URL SQLite fisso; da sistemare per online.
- Differenza del formato Deck.cards tra istruzioni e codice segnalata da DATABASE.md:
  nessuna modifica al formato delle carte o ai percorsi in questa fase.

## Metodo

Sottofasi approvate una alla volta; conferma puntuale prima dei push.
Dopo i check riallineare i documenti piccoli interessati e raccogliere qui i delta
non applicati ai documenti grandi. Nessuna esecuzione o riuscita presunta.
