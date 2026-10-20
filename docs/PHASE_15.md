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
- Scelta 15a-4b: polling soltanto quando lo stream non e' open, senza controlli
  periodici di sicurezza con stream aperto. Resta il limite del buffering del proxy.
- Scelta 15a-4b: aggiornare i soli campi risultati non modificati localmente,
  preservando ordine, assenti e punti sponsor modificati ma non salvati.
- Timer backend per scadenza revisioni oltre alla conferma alla prima richiesta.
- Rete scelta dopo lettura di api.ts e vite.config.ts: /api same-origin tramite proxy
  verso FastAPI, non chiamate cross-origin. Buffering reale ancora da verificare.
- PROJECT_SPEC.md e PROJECT_STATUS.md lasciati intatti per richiesta dell'autore;
  integrazioni raccolte qui e nelle note PHASE_15.
- Prerequisito selettivo approvato: ID CardGift non riutilizzabili con nuova
  migrazione e API che conferma soltanto gli ID delle notifiche richieste.
  L'applicazione sui dati reali non e' autorizzata da un push o dal verde della CI.
- Richiesta dell'autore alle 20:37 CEST: avvisare esplicitamente per i test manuali
  finali, con checklist, dopo collegamento delle schermate e relativa CI verde.
  Nessuna nuova prova manuale richiesta durante questo riallineamento.

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
- 15a-4a: client condiviso, validazione, test e lifecycle nel layout pubblicati
  in cb5d649; primo lint fallito per formattazione nel run 39424794586.
- Workflow mirato aggiunto in bf1ab11; il bot ha formattato esclusivamente i
  sei file segnalati in 33f01f0447706cbfe78a7468b4e0c7cb13696deb.
- CI sulla testa 33f01f0 verificata: run 39425660561 tutto verde.
  Frontend check/lint/test/build concluso alle 15:03:35 CEST, backend pytest
  alle 15:04:41, migrazioni su DB di test alle 15:03:02 del 2026-10-20.
  Client condiviso verificato in CI; pagine e polling non ancora sottoscritti.
- Riscontro manuale dell'autore alle 15:23 CEST: "ok per ora va tutto".
  Esito positivo delle prove svolte, senza elenco dei casi, log o ambiente.
  Non equivale a copertura completa della checklist o della sincronizzazione UI.
- Riallineamento 2960c05 verificato: CI verde run 39430586035,
  backend concluso alle 15:29:56 CEST; frontend e migrazioni superati.
- 15a-4b, commit 1: strumenti condivisi in 33b87b8, primo lint fallito per
  formattazione nel run 39454933814. Job formatter mirato aggiornato in 96f98ef.
- Testa formattata fb4f128786d74bdcece526f28a8f158fb13374eb: il bot modifica
  esattamente i tre file segnalati; CI ordinaria 39457551822 tutta verde.
  Frontend check/lint/test/build concluso alle 18:31:14 CEST, backend pytest
  alle 18:32:17, migrazioni alle 18:30:41 del 2026-10-20.
  Coalescer, coordinatore SSE/fallback e riconciliazione regali verificati in CI.
- Riallineamento 1cb258c verificato: CI verde run 39464622506,
  migrazioni concluse alle 19:16:54 CEST, backend 19:18:40, frontend 19:20:14.
- Prerequisito ID notifiche in aa1a4c7: modello CardGift allineato e nuova
  migrazione d6f0a4b8c2e7 successiva a d5e9a3b7c1f6. CI 39467182291 tutta verde:
  migrazioni alle 19:34:17 CEST, frontend 19:34:44, backend 19:36:14.
  Verificati su DB sintetici conservazione delle righe/schema e non riuso degli ID.
- Riallineamento 21136eb verificato: CI 39468896207 tutta verde.
- API selettiva pubblicata in cda06a91799049022358df5cbb4129c91b83b7b2 e
  verificata in CI 39476606868: backend pytest alle 20:41:18 CEST,
  migrazioni alle 20:39:33, frontend check/lint/test/build alle 20:39:58.
  Endpoint /seen-selected disponibile nel backend; /seen storico invariato.
  Il frontend non usa ancora l'operazione selettiva.
- 15a-4b, commit 2: collegamento delle schermate ancora da implementare;
  prerequisiti backend verificati, scelte su risultati e fallback gia' approvate.
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
Gli errori di giro sono loggati e ritentati. Nessuna migrazione automatica nel lifespan.
L'API selettiva aggiunge soltanto registrazione del router: lifecycle invariato.

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
lo stream. Il client 15a-4a chiude EventSource e svuota l'utente locale;
il blocco ha superato la CI sulla testa formattata 33f01f0.
Primo accesso o cursore non recuperabile inviano resync. Il coordinatore condiviso
15a-4b commit 1 richiede una rilettura REST e gestisce fallback e 401, ma deve
ancora essere usato dalle schermate nel commit 2. Rilevato anche un registro
svuotato con sqlite_sequence.
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
Il nuovo helper riconcilia regali visibili e nuovi in attesa, senza marcare /seen.
La migrazione d6f0a4b8c2e7 abilita ID CardGift non riutilizzabili, prerequisito
per non confondere una conferma tardiva con un nuovo regalo dopo un annullo.
Questa garanzia non sostituisce le autorizzazioni dell'API selettiva.

POST /api/championships/{id}/card-gifts/seen-selected accetta pilot_id e gift_ids,
lista da 1 a 100 ID interi positivi entro int64. Solo il proprietario del pilota
puo' confermare; la query limita anche il campionato. ID annullati, assenti,
gia' visti o fuori ambito sono ignorati, con 204 senza dettagli. Conferme ripetute
non riscrivono seen_at. Nessuna modifica a carte, saldi o eventi SSE.
/seen storico resta compatibile e marca tutte le notifiche del pilota.
Il futuro frontend deve inviare solo gli ID mostrati, raggruppati per pilota
in batch di massimo 100; annullamenti remoti non devono confermare nuove
notifiche mai mostrate. Il backend non prova da solo la visibilita' nel browser.

## Note dei blocchi e correzioni

- PHASE_15_IMPLEMENTATION.md, PHASE_15_DATABASE.md, PHASE_15_SERVICE.md.
- PHASE_15_REVIEW_EVENTS.md, PHASE_15_LEGACY_EVENTS.md, PHASE_15_STATE_EVENTS.md,
  PHASE_15_RACE_EVENTS.md: transazioni ed eventi delle azioni implementate.
- PHASE_15_TIMER.md: modulo timer iniziale, ora collegato al lifecycle.
- PHASE_15_CARD_PLAY_EVENTS.md: giocate e annullamenti sponsor, CI verificata.
- PHASE_15_GIFT_EVENTS.md: assegnazioni tasto S e annullamenti, CI verificata.
- PHASE_15_JUDGE_EVENTS.md: correzioni del revisore, CI verde su 8e1f440.
- PHASE_15_FRONTEND_CLIENT.md: client condiviso, CI verde e riscontro manuale limitato.
- PHASE_15_FRONTEND_FORMATTING.md: errore Prettier, procedura e commit risolutivo.
- PHASE_15_FRONTEND_LIVE.md: strumenti del commit 1, scelte approvate, limiti e
  correzione Prettier; CI verde su fb4f128, schermate non ancora collegate.
- PHASE_15_GIFT_ID_MIGRATION.md: ID stabili, ricreazione batch, CI verde su aa1a4c7
  e precauzioni operative prima dell'applicazione sui dati reali.
- PHASE_15_GIFT_SEEN_SELECTED.md: API selettiva, contratto, CI verde su cda06a9,
  frontend pendente e richiesta di avviso per i test manuali finali.
- PHASE_15_CONCURRENCY.md: test reali a due processi, non prove di carico o multi-host.
- PHASE_15_CI_FIX.md: asserzione Alembic storica, superata in CI su 47df2a5.
- PHASE_15_STATE_EVENTS_FIX.md: ID ORM dopo rollback, superata in CI su 53709a0.

## Database reale e limiti

Nessuna migrazione applicata dall'assistente ai dati del gioco e nessun backup
reale effettuato dall'assistente. L'ambiente delle prove dell'autore non e'
stato dettagliato e non viene presunto. Prima di usare il ramo sui dati reali
occorrono arresto dell'app, backup verificato e prova su copia della migrazione,
poi autorizzazione dell'applicazione ai dati del gioco. Anche heat.py start e
setup applicano migrazioni: non avviarli prima di queste precauzioni.
Nessun reset/cancellazione autorizzato in questi blocchi.
La CI usa database nuovi o sintetici: non sostituisce le verifiche sui dati reali.
Catena letta: testa precedente a2e6c0d4f8b3, registro d5e9a3b7c1f6, nuova testa
d6f0a4b8c2e7; merge storico b2d6f0a4c8e1. Il blocco API non aggiunge migrazioni.
Il downgrade della nuova migrazione conserva righe ma perde la garanzia e la
storia di non riuso. Non usarlo con client che richiedono ID stabili; non portare
conferme pendenti attraverso ripristini di backup o ricreazioni del database.
Nessuna prova browser eseguita dall'assistente. Il riscontro positivo dell'autore
non dettaglia durata delle connessioni attraverso il proxy, carico, deployment
online o filesystem di rete: queste verifiche non sono dichiarate superate.
Il riscontro delle 15:23 non viene esteso agli strumenti introdotti dopo o all'API.
Non dichiariamo l'app completamente real-time. Nessuna nuova dipendenza.
Nessun comando o test eseguito localmente dall'assistente.

## Sistemazioni e riallineamenti pendenti

- PROJECT_STATUS.md: riga 14 vecchia, manca 15, data e descrizione 13e da riallineare.
- PROJECT_SPEC.md: rilettura dopo bc0fbfb e refuso storico da verificare.
- PHASE_14_POST_MERGE.md: aae6c33 e' storico; automazione format-championships non
  verificata in questa fase.
- DATABASE.md riallineato per ID CardGift e conferma selettiva, con rimando al
  registro SSE. Non e' una nuova ispezione del file SQLite reale.
- README.md, SETUP.md e SCRIPTS.md riletti nei blocchi precedenti; comandi invariati.
  Prima di ulteriori aggiornamenti rileggere SHOP_DESIGN.md e PROJECT_NOTES.md.
  Backup/setup sicuro ancora da verificare nel codice.
- config.py: cookie secure disattivato e URL SQLite fisso; da sistemare per online.
- Differenza del formato Deck.cards tra istruzioni e codice segnalata da DATABASE.md:
  nessuna modifica al formato delle carte o ai percorsi in questa fase.

## Metodo e verifica del riallineamento

Sottofasi approvate una alla volta; conferma puntuale prima dei push.
Dopo i check riallineare i documenti piccoli interessati e raccogliere qui i delta
non applicati ai documenti grandi. Nessuna esecuzione o riuscita presunta.
Scaffold e lockfile conservati. Questo riallineamento modifica soltanto
PHASE_15_GIFT_SEEN_SELECTED.md, PHASE_15_GIFT_ID_MIGRATION.md, DATABASE.md e PHASE_15.md.
Esiti CI letti per cda06a9: 39476606868 tutto verde; nessun conteggio test inventato.
Il nuovo commit documentale richiede una verifica CI separata.
Nessun codice, workflow o dato reale modificato e nessun avvio del commit 2.
Dopo il riallineamento preparare il collegamento delle schermate con i prerequisiti
backend ora disponibili; avviso e checklist manuale solo alla fine dei controlli.
