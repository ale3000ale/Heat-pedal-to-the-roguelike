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
  versoFastAPI, non chiamate cross-origin. Buffering reale ancora da verificare.
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
- Timer collegato al lifespan; test lifecycle passati in CI su 22d4aa4
  (run 39408719258), come registrato in PHASE_15_CARD_PLAY_EVENTS.md.
- Giocata e annullamento sponsor collegati; CI verde su e61aa83
  (run 39409688398). Dettagli in PHASE_15_CARD_PLAY_EVENTS.md.
- Tasto S e annullamento assegnazione collegati in 660a279; CI verde
  (run 39410540606): backend pytest, migrazioni e frontend check/lint/test/build.
  Test del blocco: privacy, rifiuti senza eventi, ripristino saldi e rollback.
- Riallineamento documentale c6898da verificato: CI verde run 39411533470,
  backend pytest concluso alle 12:59:00 CEST; migrazioni e frontend superati.
- Correzioni del revisore collegate in 8e1f440: annullo attivo/consumato,
  bonus e rimozione. CI verde run 39414943186: backend pytest concluso alle
  13:28:32 CEST, frontend alle 13:26:59, migrazioni alle 13:26:38 del 2026-10-20.
  Le integrazioni backend previste per 15a-3 sono collegate e verificate in CI;
  questo esito non certifica il funzionamento end-to-end del frontend SSE.
- Riallineamento 4430d40 verificato: run 39421574917 tutto verde,
  backend concluso alle 14:22:43 CEST, frontend 14:21:51, migrazioni 14:21:21.
- 15a-4a approvata: client condiviso, validazione, test e lifecycle nel layout.
  Implementazione nel blocco corrente; test locali non eseguiti, CI da leggere.
  Pagine e polling non collegati agli eventi: nessun real-time UI dichiarato.
- 15a-4b: sottoscrizioni delle pagine, resync REST e fallback da implementare
  dopo verifica del client e approvazione del blocco successivo.
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

File del blocco lifecycle: backend/app/main.py,
backend/tests/test_review_timer_lifespan.py, questo documento.
Test: avvio/arresto normale e con errore nel corpo, startup fallito senza task
 e timer reale su dati temporanei con prima scadenza osservata.
La prova lifecycle non e' una verifica di deployment o di traffico HTTP reale.

## Registro ed endpoint

SQL in PHASE_15_DATABASE.md; servizio in PHASE_15_SERVICE.md.
Registro persistente condiviso dai worker, id AUTOINCREMENT SQLite non riutilizzati.
Gli eventi sono accodati prima del commit dell'azione; rollback rimuove entrambi.
GET /api/events/stream: cookie, Last-Event-ID, letture ogni secondo, keep-alive ogni
15 secondi, retry SSE 3 secondi. Sessioni SQL brevi nel thread pool, chiuse prima
di invio/attesa. Sessione HTTP ricontrollata a ogni lettura; auth.expired chiude
lo stream. Il client del blocco 15a-4a chiude EventSource e svuota l'utente locale;
la verifica CI di questa integrazione e' ancora pendente.
Primo accesso o cursore non recuperabile inviano resync: il client ricarichera'
lo stato REST nel blocco schermate 15a-4b. Rilevato anche un registro svuotato
con sqlite_sequence.
I privati sono visibili solo al destinatario; i pubblici agli iscritti con pilota
non eliminato e ad admin/giudici. Mai carte private, conteggi o bozze nei pubblici.
La conservazione e' 24 ore, con eliminazione periodica e non esatta al secondo.

## Eventi carte e notifiche persistenti

card.played e card.play_undone sono privati al proprietario, con race_id/play_id.
card.gifted e card.gift_undone sono privati al proprietario, con race_id/gift_id.
Ogni azione accoda anche cards.changed pubblico con soli race_id/pilot_id.
Nessun nome, immagine o conteggio delle carte nei payload di questi eventi.
Il client dovra' rileggere le API autorizzate; il replay di card.gifted non deve
mostrare direttamente una carta gia' annullata o una notifica gia' vista.
CardGift.seen_at rimane il riferimento delle notifiche non viste, anche nel
fallback polling. Eventi, inventario, pool e notifica sono nella stessa transazione.
Il revisore riusa card.play_undone e cards.changed per annullare una giocata.
Bonus e rimozione emettono soltanto cards.changed: non sono regali e non creano
notifiche CardGift. Correzioni ed eventi condividono commit e rollback.

## Note dei blocchi e correzioni

- PHASE_15_IMPLEMENTATION.md, PHASE_15_DATABASE.md, PHASE_15_SERVICE.md.
- PHASE_15_REVIEW_EVENTS.md, PHASE_15_LEGACY_EVENTS.md, PHASE_15_STATE_EVENTS.md,
  PHASE_15_RACE_EVENTS.md: transazioni ed eventi delle azioni implementate.
- PHASE_15_TIMER.md: modulo timer iniziale, ora collegato al lifecycle.
- PHASE_15_CARD_PLAY_EVENTS.md: giocate e annullamenti sponsor, CI verificata.
- PHASE_15_GIFT_EVENTS.md: assegnazioni tasto S e annullamenti, CI verificata.
- PHASE_15_JUDGE_EVENTS.md: correzioni del revisore, CI verde su 8e1f440.
- PHASE_15_FRONTEND_CLIENT.md: client condiviso, test preparati e CI da verificare.
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
- README.md, SETUP.md, SCRIPTS.md e DATABASE.md riletti per il riallineamento c6898da.
  Nessun comando, dipendenza o schema aggiunto dai blocchi eventi carte.
  Delta SSE del database in PHASE_15_DATABASE.md. Prima di ulteriori
  aggiornamenti rileggere SHOP_DESIGN.md e PROJECT_NOTES.md.
  Backup/setup sicuro ancora da verificare nel codice.
- config.py: cookie secure disattivato e URL SQLite fisso; da sistemare per online.
- Differenza del formato Deck.cards tra istruzioni e codice segnalata da DATABASE.md:
  nessuna modifica al formato delle carte o ai percorsi in questa fase.

## Metodo e verifica del blocco

Sottofasi approvate una alla volta; conferma puntuale prima dei push.
Dopo i check riallineare i documenti piccoli interessati e raccogliere qui i delta
non applicati ai documenti grandi. Nessuna esecuzione o riuscita presunta.
La 15a-4a parte da 4430d409a84b541c8f8bd096a0d7589935166460, PR 14 in bozza.
Riletti layout e autenticazione, pagine campionato/gara, polling, store revisione,
protocollo backend, package.json e vite.config.ts. Scaffold e lockfile conservati.
Nessun comando locale eseguito: formatter, lint, check, test e build del nuovo
codice restano da verificare tramite CI dopo il push. Poi riallineare le note.
Il collegamento alle schermate richiede l'approvazione separata della 15a-4b.
