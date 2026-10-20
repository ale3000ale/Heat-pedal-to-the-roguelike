# Fase 15 - SSE in tempo reale e sistemazione

Aggiornamento: 2026-10-21. Solo ramo phase-15-sse-sistemazione.
Base iniziale main 2cded6d. PR 14 in bozza; nessun merge senza richiesta.
Questa pagina descrive lo stato corrente. Le note dei singoli blocchi restano
cronologia dei commit indicati: "timer non attivo" o "pagine non collegate"
nei blocchi precedenti non descrivono automaticamente la testa corrente.

## Stato e decisioni approvate

- Backend SSE, timer, client condiviso, servizio notifiche e controller verificati.
- Pagina campionato collegata in df7edf5 e formattata in dc97fcf; CI 39502927035
  tutta verde. La pagina usa /seen-selected, non la conferma generale /seen.
- Funzione pura di riconciliazione risultati verificata su 3c860d2, CI 39509635060
  verde, ma non ancora collegata. Pagina gara e pannello di revisione da completare.
- Scelta confermata nel seguito delle 00:27 del 2026-10-21: ordine e assenti come
  unica assegnazione coerente, sponsor riconciliati per pilota. Preservare modifiche
  locali e segnalare conflitti, anche se il remoto sposta un pilota con sponsor
  modificati. Se lo stato remoto revoca la modifica, mantenere bozza in sola lettura.
- Polling e card_poll_seconds conservati come fallback soltanto senza stream open.
  Nessun polling lento di sicurezza con stream aperto; buffering proxy da verificare.
- Eventi carte ottenute/annullate/giocate, stato gara/revisione, risultati e classifica.
  Non estende SSE automaticamente a tutti i CRUD o alle impostazioni/iscrizioni remote.
- Uso online a bassa affluenza, piu' worker sullo stesso SQLite. Nessuna prova di carico,
  multi-host o filesystem di rete dichiarata. /api same-origin tramite proxy FastAPI.
- ID CardGift stabili con nuova migrazione e conferma selettiva. La CI non autorizza
  migrazioni sui dati reali. PROJECT_SPEC.md e PROJECT_STATUS.md restano protetti.
- Richiesta dell'autore del 2026-10-20 alle 20:37 CEST: avviso esplicito e checklist
  per test manuali finali dopo il collegamento restante e la relativa CI verde.
  Nessuna nuova prova manuale richiesta ora.
- Richiesta del 2026-10-21 alle 00:26: i commit esclusivamente .md non bloccano il
  seguito in attesa della CI. Non attribuire loro esiti non letti. Modifiche a codice,
  configurazioni, workflow, dipendenze o migrazioni richiedono ancora i controlli.

## Registro sintetico delle verifiche

Le esecuzioni riportate sono quelle gia' lette nei blocchi. I dettagli storici,
le correzioni e le ore dei blocchi precedenti sono nelle note e nella storia Git.
"Verde" indica i job previsti completati con successo, non un collaudo browser.

| Blocco | Commit o testa verificata | Esecuzione CI verde |
|---|---|---|
| Contratto, event_log e servizio 15a-1 | 54079f7 | 39341481995 |
| Endpoint SSE 15a-2 | a332633 | 39342203544 |
| Eventi gara, risultati e classifica 15a-3 | 39572e3 | 39403393864 |
| Concorrenza a due processi | 819e1c0 | 39403918209 |
| Timer nel lifespan | 22d4aa4 | 39408719258 |
| Giocata e annullamento sponsor | e61aa83 | 39409688398 |
| Tasto S e annullamento regalo | 660a279 | 39410540606 |
| Riallineamento | c6898da | 39411533470 |
| Correzioni revisore, bonus e rimozione | 8e1f440 | 39414943186 |
| Riallineamento | 4430d40 | 39421574917 |
| Client frontend 15a-4a formattato | 33f01f0 | 39425660561 |
| Riallineamento | 2960c05 | 39430586035 |
| Coalescer, fallback e riconciliazione 15a-4b/1 | fb4f128 | 39457551822 |
| Riallineamento | 1cb258c | 39464622506 |
| ID CardGift e migrazione d6f0a4b8c2e7 | aa1a4c7 | 39467182291 |
| Riallineamento | 21136eb | 39468896207 |
| API selettiva | cda06a9 | 39476606868 |
| Riallineamento | 9ea0cb0 | 39479071828 |
| Servizio notifiche formattato | de29e70 | 39497343267 |
| Riallineamento | 991c218 | 39498576979 |
| Controller e popup | 936f27b | 39500026385 |
| Riallineamento | eca9adb | 39501199891 |
| Pagina campionato collegata e formattata | dc97fcf | 39502927035 |
| Riconciliazione risultati formattata | 3c860d2 | 39509635060 |

Correzioni storiche: cb5d649 ebbe lint fallito in 39424794586, workflow bf1ab11
poi bot 33f01f0447706cbfe78a7468b4e0c7cb13696deb sui sei file previsti.
33b87b8 ebbe lint fallito in 39454933814, workflow 96f98ef poi bot
fb4f128786d74bdcece526f28a8f158fb13374eb sui tre file del coordinatore.
493a3fb ebbe frontend fallito in 39491830284; log dell'autore alle 22:43 CEST
su Prettier del solo test notifiche. Workflow ae161cc poi bot
de29e7000aa5ad9bc6c313817178622b9844f903 alle 23:04:11 CEST.
936f27b ebbe anche formatter 39500018271 success alle 23:24:49 CEST;
testa riletta invariata, nessun nuovo commit bot presente al controllo.
cebcceb ebbe frontend fallito in 39509013765 sul Prettier del solo modulo
race-result-reconcile.ts; backend e migrazioni passati. Workflow 823572f poi
bot 3c860d2f9c576146a1867ca0da65634d0dc1d138 alle 00:38:52 CEST del 2026-10-21.
Diff letto: sola espressione conflict su una riga, nessun cambiamento logico.
Non si dichiarano test/build riusciti nei tentativi fermati dal lint.

Riscontro manuale dell'autore del 2026-10-20 alle 15:23 CEST: "ok per ora va tutto".
Nessun elenco casi, log o ambiente: non esteso ai blocchi introdotti successivamente.

## Campionato collegato: verifica

Implementazione df7edf52e46092a0102d5edcb3ac4a2373bf22ed. Bot
dc97fcf91a9c39ae4efcd956c64955a3006edcfe alle 23:45:21 CEST del 2026-10-20.
Diff letto: sola formattazione di championship-live.ts, championship-live.spec.ts
e routes/championships/[id]/+page.svelte. Nessun cambiamento logico nel commit bot.
CI 39502927035: migrazioni success alle 23:56:31, frontend check/lint/test/build
success alle 23:57:05, backend pytest success alle 23:58:10 CEST del 2026-10-20.
Verificati esiti, commit e diff, non log completi o conteggi numerici dei test.

championship-live.ts riusa coordinatore, servizio e controller: legge campionato,
classifica, gare e piloti propri, poi regali dei soli propri iscritti. Sono piu'
REST, non una transazione unica. Errori non diventano snapshot vuoti. Apply
aggiorna anche popup aperti e refreshKey delle sezioni sponsor. /seen-selected
riceve solo ID resi; annulli e chiusure remote non confermano. Dopo l'ack nuova
lettura accorpata. Contesto legato a parametro e utente, cleanup invalida risposte
tardive e avvii dopo lettura intervallo; 401 ferma il modulo prima di svuotare auth.
Il layout gestisce auth.expired. Nessun secondo EventSource o retry di scritture.
Campionati chiusi senza popup regali come prima; l'API ammette ack storici.
Test con dipendenze simulate, non DOM/browser; non dichiariamo l'app completamente
real-time.

## Riconciliazione risultati: verifica e collegamento pendente

Implementazione cebcceb, correzione formatter 823572f e testa bot 3c860d2.
CI 39509635060 tutta verde il 2026-10-21: migrazioni 00:40:00 CEST,
frontend check/lint/test/build 00:40:28, backend pytest 00:41:44.
Funzione pura e suite passate: base server, modulo locale e nuovo remoto;
ordine/assenti coerenti, sponsor non sovrascritti se modificati, input vuoto
preservato, conflitto e modifiche residue, nessuna mutazione degli input.
Non e' ancora usata dalla pagina gara e non implementa da sola permessi,
protezione uscita, bozza in sola lettura o sostituzione del reload del pannello.
Il prossimo blocco deve collegarla realmente e verificare anche questi aspetti.
Nessuna nuova garanzia di concorrenza lato server introdotta dal merge frontend.

## Timer, registro e autorizzazioni

main.py avvia heat-review-timer per worker dopo la manutenzione iniziale, ogni
5 secondi per revisioni scadute con risultati in campionati aperti. Riusa
settle_expired_reviews: ricontrollo sotto lock, commit per gara ed eventi nella
stessa transazione. Bozze applicate secondo logica esistente. Resta il controllo
REST di scadenza. Pulizia eventi oltre 24 ore al primo giro e poi ogni ora,
non esatta al secondo. Stop cooperativo e attesa anche se il corpo lifespan
fallisce; nessuna interruzione di transazioni. Errori loggati e ritentati.
Nessuna migrazione automatica nel lifespan. Test lifecycle in test_review_timer_lifespan.py.

Event_log persistente condiviso, ID AUTOINCREMENT non riutilizzati. Eventi prima
del commit dell'azione, rollback comune. GET /api/events/stream autenticato con
cookie e Last-Event-ID, letture ogni secondo, keep-alive 15 secondi, retry 3 secondi.
Sessioni SQL brevi nel thread pool, chiuse prima di invio/attesa. Sessione HTTP
ricontrollata a ogni lettura, auth.expired chiude lo stream. Primo accesso o cursore
non recuperabile inviano resync, rilevato anche registro svuotato con sqlite_sequence.
Privati solo al destinatario; pubblici agli iscritti con pilota non eliminato e ad
admin/giudici. Nessuna carta privata, conteggio o bozza nei pubblici.

card.played/card.play_undone privati con race_id/play_id; card.gifted/card.gift_undone
privati con race_id/gift_id. Anche cards.changed pubblico con soli race_id/pilot_id.
Nessun nome, immagine o conteggio nei payload. Il replay richiede REST autorizzate,
non ricrea direttamente popup. seen_at resta riferimento delle notifiche non viste.
Inventario, pool, notifica ed eventi condividono transazione. Revisore riusa
card.play_undone/cards.changed; bonus e rimozione emettono solo cards.changed,
non creano CardGift. Test concorrenti: due processi spawn indipendenti sullo stesso
SQLite sintetico per scadenza/scadenza e scadenza/conferma manuale, una sola
chiusura, consumo/restituzione e coppia di eventi. Non sono prove di carico.

## Conferma selettiva e database reale

POST /api/championships/{id}/card-gifts/seen-selected: pilot_id e lista da 1 a 100
ID positivi int64, solo proprietario anche per admin/giudice, ambito campionato.
ID assenti, annullati, gia' visti o fuori ambito ignorati; 204 senza dettagli.
Solo seen_at ancora vuoto, ripetizioni non riscrivono date; niente carte, saldi o
SSE nuovi. /seen storico resta compatibile, non usato dal nuovo flusso campionato.
Servizio TypeScript conserva pilotId assente nel DTO, valida ID sicuri JavaScript,
deduplica e usa batch per pilota. Nessuna atomicita' tra batch; quelli gia' riusciti
possono restare persistiti dopo errore. Controller gestisce coda, annulli senza ack,
chiusura volontaria e dispose; popup passa l'ultima lista registrata dopo render.
Backend e servizio non provano da soli la visibilita' nel browser.

Nessuna migrazione, backup o modifica dei dati del gioco eseguita dall'assistente.
Prima dell'uso reale: arrestare app, backup verificato, prova su copia e autorizzazione
all'applicazione. Anche heat.py start/setup migrano: non avviarli prima. Catena
letta a2e6c0d4f8b3, d5e9a3b7c1f6, d6f0a4b8c2e7; merge storico b2d6f0a4c8e1.
Nuovi moduli frontend non cambiano schema o dipendenze. Downgrade d6f0a4b8c2e7
conserva righe ma perde storia e garanzia di non riuso: non usarlo con client che
richiedono ID stabili. Non trasferire conferme pendenti tra backup o DB ricreati.
Nessun reset autorizzato. CI su DB nuovi/sintetici non certifica i dati originali.
Nessun comando o test locale eseguito e nessuna prova browser dell'assistente.

## Note, sistemazioni e seguito

Contratto/schema/servizio: PHASE_15_IMPLEMENTATION.md, PHASE_15_DATABASE.md,
PHASE_15_SERVICE.md. Eventi: PHASE_15_REVIEW_EVENTS.md, PHASE_15_LEGACY_EVENTS.md,
PHASE_15_STATE_EVENTS.md, PHASE_15_RACE_EVENTS.md, PHASE_15_CARD_PLAY_EVENTS.md,
PHASE_15_GIFT_EVENTS.md, PHASE_15_JUDGE_EVENTS.md. Timer: PHASE_15_TIMER.md.
Frontend: PHASE_15_FRONTEND_CLIENT.md, PHASE_15_FRONTEND_FORMATTING.md,
PHASE_15_FRONTEND_LIVE.md, PHASE_15_FRONTEND_GIFT_SERVICE.md,
PHASE_15_GIFT_POPUP_CONTROLLER.md, PHASE_15_CHAMPIONSHIP_LIVE.md e
PHASE_15_RACE_RESULT_RECONCILE.md.
ID/API: PHASE_15_GIFT_ID_MIGRATION.md e PHASE_15_GIFT_SEEN_SELECTED.md.
Concorrenza: PHASE_15_CONCURRENCY.md. Fix storici: PHASE_15_CI_FIX.md (47df2a5)
e PHASE_15_STATE_EVENTS_FIX.md (53709a0). Stato corrente nelle sezioni sopra;
indicazioni delle vecchie note limitate ai commit del loro blocco.

Pendenti: 15b da definire con autore dopo SSE; PROJECT_STATUS.md con riga 14 vecchia,
manca 15 e data/descrizione 13e; PROJECT_SPEC.md da rileggere dopo bc0fbfb e refuso
storico. PHASE_14_POST_MERGE.md/aae6c33 storico, format-championships non verificato.
README.md, SETUP.md e SCRIPTS.md riletti in blocchi precedenti, comandi invariati;
prima di altri aggiornamenti rileggere SHOP_DESIGN.md e PROJECT_NOTES.md.
Backup/setup sicuro ancora da verificare nel codice. config.py: cookie secure
disattivato e URL SQLite fisso da sistemare per online. Differenza Deck.cards tra
istruzioni e codice segnalata da DATABASE.md: nessuna modifica al formato/percorsi.

Questo riallineamento aggiorna solo questa pagina e PHASE_15_RACE_RESULT_RECONCILE.md.
Nessuna modifica a codice, workflow, dipendenze, schema o dati. PROJECT_SPEC.md e
PROJECT_STATUS.md intatti. Essendo soltanto .md, non attendere i test del commit
per il seguito e non attribuirgli esiti presunti. Prossimo blocco: collegamento
pagina gara/pannello, controlli del codice, riallineamento e avviso esplicito per
i test manuali finali. Nessun merge autorizzato.
