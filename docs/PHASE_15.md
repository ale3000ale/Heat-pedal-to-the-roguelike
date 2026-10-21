# Fase 15 - SSE in tempo reale e sistemazione

Aggiornamento: 2026-10-21. Solo ramo phase-15-sse-sistemazione.
Base iniziale main 2cded6d. PR 14 in bozza; nessun merge senza richiesta.
Stato corrente qui; note precedenti limitate ai commit del singolo blocco.
"Timer non attivo" o "pagine non collegate" nei blocchi storici non descrivono
la testa corrente. Nessun esito CI attribuito a commit solo documentali non letti.

## Stato e decisioni approvate

- Backend SSE, timer, client condiviso, servizio notifiche e controller verificati.
- Campionato collegato df7edf5/dc97fcf, CI 39502927035 verde: /seen-selected al
  posto della conferma generale /seen, snapshot completi e popup riconciliati.
- Gara collegata in 4833a8d, fix nullable 44bb4dd, testa formattata 4978f73:
  CI 39596834057 verde. Merge risultati usato dalla pagina, callback revisione
  senza reload completo. Non sono ancora prove DOM/browser dei nuovi componenti.
- Inventari: modulo puro 05b2829/6aa7fe6 verificato in CI 39599465230. Non ancora
  usato da review-counts.svelte.ts o dal pannello: sincronizzazione interna pendente.
- Scelta confermata dopo proposta delle 00:27: ordine/assenti unica assegnazione,
  sponsor per pilota; preservare modifiche e segnalare conflitti. Se cambia il
  permesso, bozza risultati in sola lettura, non autosalvata.
- Politica inventari approvata dopo proposta delle 14:13 e seguito delle 14:15:
  conservare conteggi incompatibili, non ridurli automaticamente; bloccare conferma,
  revocare spunte interessate e non trasferire bozze tra revisori/nuovi inizi.
  Rilettura che abbandona modifiche solo con conferma esplicita. UI ancora da collegare.
- Polling/card_poll_seconds soltanto come fallback senza stream open. Nessun polling
  lento di sicurezza con stream aperto; buffering proxy reale non verificato.
- Eventi carte ottenute/annullate/giocate, stato gara/revisione, risultati/classifica.
  Non estende SSE a tutti i CRUD o a impostazioni/iscrizioni remote senza eventi.
- Uso online a bassa affluenza e piu' worker sullo stesso SQLite. Nessuna prova di
  carico, multi-host o filesystem di rete. /api same-origin tramite proxy FastAPI.
- ID CardGift stabili e conferma selettiva non autorizzano migrazioni sui dati reali.
  PROJECT_SPEC.md e PROJECT_STATUS.md restano protetti.
- Autore, 2026-10-20 alle 20:37 CEST: avviso esplicito e checklist per test manuali
  finali dopo collegamenti restanti e relativa CI verde. Nessuna prova nuova richiesta ora.
- Autore, 2026-10-21 alle 00:26: commit solo .md non bloccano il seguito in attesa CI.
  Codice, configurazioni, workflow, dipendenze e migrazioni richiedono ancora controlli.

## Registro sintetico delle verifiche

Esecuzioni gia' lette nei blocchi; dettagli, ore e correzioni nelle note e nella
storia Git. Verde significa job previsti riusciti, non collaudo browser.

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
| Campionato collegato e formattato | dc97fcf | 39502927035 |
| Merge risultati puro formattato | 3c860d2 | 39509635060 |
| Gara collegata, fix nullable e formattazione | 4978f73 | 39596834057 |
| Merge inventari puro formattato | 6aa7fe6 | 39599465230 |

Correzioni storiche: cb5d649 ebbe lint fallito in 39424794586, workflow bf1ab11
poi bot 33f01f0447706cbfe78a7468b4e0c7cb13696deb sui sei file previsti.
33b87b8 ebbe lint fallito in 39454933814, workflow 96f98ef poi bot
fb4f128786d74bdcece526f28a8f158fb13374eb sui tre file del coordinatore.
493a3fb ebbe frontend fallito in 39491830284; log autore 22:43 CEST sul Prettier
del test notifiche. Workflow ae161cc poi bot de29e7000aa5ad9bc6c313817178622b9844f903
alle 23:04:11 CEST. 936f27b ebbe anche formatter 39500018271 success 23:24:49,
testa riletta invariata senza nuovo bot. cebcceb ebbe Prettier fallito in
39509013765, backend/migrazioni passati; workflow 823572f poi bot
3c860d2f9c576146a1867ca0da65634d0dc1d138 alle 00:38:52 del 2026-10-21, sola
espressione conflict su una riga. Non dichiarare test/build riusciti nei tentativi
fermati dal lint. Il primo collegamento gara 4833a8d ebbe frontend e formatter
falliti; cronologia del type-check nella nota PHASE_15_RACE_LIVE.md.

Riscontro autore del 2026-10-20 alle 15:23 CEST: "ok per ora va tutto". Nessun
elenco casi, log o ambiente; non esteso ai blocchi introdotti successivamente.

## Campionato e gara collegati

Campionato: implementazione df7edf52e46092a0102d5edcb3ac4a2373bf22ed, bot
dc97fcf91a9c39ae4efcd956c64955a3006edcfe alle 23:45:21 CEST del 2026-10-20.
Diff letto, sola formattazione dei tre file del collegamento. CI 39502927035:
migrazioni 23:56:31, frontend check/lint/test/build 23:57:05, backend 23:58:10.
Legge campionato, classifica, gare, piloti propri e regali dei soli propri iscritti;
piu' REST, non transazione unica. Errori non diventano []. Apply aggiorna popup e
refreshKey delle sezioni sponsor. Solo ID resi a /seen-selected; annulli/chiusure
remote non confermano. Dopo ack nuova lettura accorpata. Cleanup per parametro e
utente, 401 ferma il modulo prima di svuotare auth, auth.expired gestito dal layout.
Campionati chiusi senza popup regali come prima, API comunque disponibile per ack storici.

Risultati: funzione pura cebcceb/3c860d2, CI 39509635060 verde il 2026-10-21:
migrazioni 00:40:00, frontend 00:40:28, backend 00:41:44. Ora usata nella pagina gara.
Base server separata dal modulo; ordine/assenti coerenti e sponsor locali preservati.
PUT esplicita con copia preinvio come base per non perdere modifiche durante la
richiesta. Valida tutti i piloti/duplicati/ID e massimo 12 partecipanti, normalizzazione
sponsor preesistente. Backend resta autorevole; nessun lock ottimistico introdotto.

Gara: implementazione 4833a8dce73dec8d6634376fdaaab67fa1d24168, fix
44bb4dd6a7eb90dca59299c0a09dea2795e5f6e8, bot 4978f7387562aea7f09d14fea05025ae01ed3025
alle 14:05:14 CEST del 2026-10-21. Diff letto: sola formattazione dei due componenti.
CI 39596834057: migrazioni 14:06:53, frontend 14:07:09, backend 14:08:53, tutti success.
Snapshot gara/campionato/piloti, eventi del campionato anche per is_last e resync;
fallback solo senza stream open. Risultati ufficiali e permessi aggiornati, bozza
locale in sola lettura se la modifica non e' piu' permessa, fino all'uscita.
Uscita protetta con modifiche o PUT in corso; uscire non annulla HTTP gia' partite.
Risposte del vecchio contesto scartate. Pannello usa onchanged, non reload browser;
ricreato per contesto/stato, non a ogni snapshot. Store inventari ancora invariato.

Nessun secondo EventSource o retry automatico delle scritture. Test puri/coordinatore
e controlli compiler superati non certificano DOM, guardie uscita, vista bozza,
callback e modifiche durante PUT. Nessuna prova browser dell'assistente.

## Inventari: modulo verificato, integrazione pendente

Implementazione 05b282984b492fdf3a666c2383d40b938e7e6c19, bot
6aa7fe6c4b2307550aa3f229b0a3f99810d1a67a alle 14:25:19 CEST del 2026-10-21.
Diff letto: sola formattazione di review-inventory-reconcile.ts e .spec.ts.
CI 39599465230: migrazioni 14:26:26, frontend check/lint/test/build 14:26:47,
backend pytest 14:28:04, tutti success. Verificati esiti, commit e diff, non log
completi o conteggi numerici. Funzione pura, non ancora importata da store/pannello.

ownReviewKey distingue gara/revisore/inizio della propria revisione attiva, non
sostituisce autorizzazione o scadenza server. Merge conteggi locali nella stessa
revisione, nuovi metadati dal remoto; piloti da ricontrollare e conflitti validi.
Con carte/piloti rimossi con modifiche o quantita' oltre il nuovo totale, blocco
esplicito e intera copia locale preservata, nessun clamp. Fonti invalide non sono [].
API rilette: inventario giudice/admin leggibile senza essere titolare, bozza solo
al titolare attivo. GET stato puo' elaborare scadenze come gia' avviene nel backend.
Il collegamento non dovra' introdurre conferme o salvataggi automatici agli eventi.
403/409 durante le letture richiedono verifica del contesto, non bozze vuote fittizie.

Da fare nello store e nel pannello: sottoscrizioni/fallback, confronto chiavi prima
del merge, aggiornamenti che preservano conteggi, revoca spunte, blocchi conferma,
chiusura/cambio titolare, recupero esplicito con conferma e test di permessi/lifecycle.
Non e' un altro prerequisito backend. Fase SSE non ancora conclusa.

## Timer, registro e autorizzazioni

main.py avvia heat-review-timer per worker dopo manutenzione iniziale, ogni 5 secondi
per revisioni scadute con risultati in campionati aperti. settle_expired_reviews
ricontrolla sotto lock e committa gara/eventi nella stessa transazione; bozze secondo
logica esistente. Resta il controllo REST di scadenza. Pulizia oltre 24 ore al primo
giro e poi ogni ora, non esatta al secondo. Stop cooperativo e attesa anche se il
corpo lifespan fallisce; nessuna interruzione di transazioni. Errori loggati/ritentati.
Nessuna migrazione nel lifespan. Test lifecycle in test_review_timer_lifespan.py.

Event_log condiviso e persistente, ID AUTOINCREMENT non riutilizzati. Eventi prima
del commit dell'azione e rollback comune. GET /api/events/stream autenticato con
cookie/Last-Event-ID, letture ogni secondo, keep-alive 15 secondi, retry 3 secondi.
Sessioni SQL brevi nel thread pool, chiuse prima di invio/attesa; sessione HTTP
ricontrollata a ogni lettura, auth.expired chiude lo stream. Primo accesso/cursore
non recuperabile inviano resync, rilevato anche registro svuotato con sqlite_sequence.
Privati al destinatario; pubblici agli iscritti con pilota non eliminato e admin/giudici.
Mai carte private, conteggi o bozze nei pubblici.

card.played/card.play_undone privati con race_id/play_id; card.gifted/card.gift_undone
privati con race_id/gift_id; cards.changed pubblico con soli race_id/pilot_id.
Niente nomi, immagini o conteggi nei payload. Replay tramite REST autorizzate,
non ricrea popup. seen_at riferimento notifiche non viste. Inventario, pool,
notifica ed eventi condividono transazione. Revisore riusa card.play_undone/cards.changed;
bonus/rimozione solo cards.changed, non CardGift. Test a due processi spawn sullo
stesso SQLite sintetico per scadenza/scadenza e scadenza/conferma manuale: una sola
chiusura, consumo/restituzione e coppia eventi. Non prove di carico.

## Conferma selettiva e database reale

POST /api/championships/{id}/card-gifts/seen-selected: pilot_id e lista 1..100 ID
positivi int64, solo proprietario anche per admin/giudice, ambito campionato.
Assenti, annullati, gia' visti o fuori ambito ignorati, 204 senza dettagli.
Solo seen_at vuoto modificato, ripetizioni non riscrivono date; niente carte,
saldi o SSE nuovi. /seen compatibile ma non usato dal nuovo flusso campionato.
Servizio conserva pilotId assente nel DTO, valida ID sicuri JavaScript e invia
batch deduplicati per pilota. Nessuna atomicita' tra batch, precedenti possono
restare persistiti dopo errore. Controller gestisce coda, annulli senza ack,
chiusura volontaria e dispose; popup passa l'ultima lista registrata dopo render.
Backend/servizio non provano da soli la visibilita' nel browser.

Nessuna migrazione, backup o modifica dei dati del gioco eseguita dall'assistente.
Prima dell'uso reale: arresto app, backup verificato, prova su copia e autorizzazione.
Anche heat.py start/setup migrano, non avviarli prima. Catena letta a2e6c0d4f8b3,
d5e9a3b7c1f6, d6f0a4b8c2e7; merge storico b2d6f0a4c8e1. Moduli frontend non cambiano
schema/dipendenze. Downgrade d6f0a4b8c2e7 conserva righe ma perde storia/garanzia di
non riuso: non usarlo con client che richiedono ID stabili; non trasferire conferme
pendenti tra backup o DB ricreati. Nessun reset autorizzato. CI su DB sintetici non
certifica gli originali. Nessun comando o test locale eseguito dall'assistente.

## Note, sistemazioni e seguito

Contratto/schema/servizio: PHASE_15_IMPLEMENTATION.md, PHASE_15_DATABASE.md,
PHASE_15_SERVICE.md. Eventi: PHASE_15_REVIEW_EVENTS.md, PHASE_15_LEGACY_EVENTS.md,
PHASE_15_STATE_EVENTS.md, PHASE_15_RACE_EVENTS.md, PHASE_15_CARD_PLAY_EVENTS.md,
PHASE_15_GIFT_EVENTS.md, PHASE_15_JUDGE_EVENTS.md. Timer: PHASE_15_TIMER.md.
Frontend: PHASE_15_FRONTEND_CLIENT.md, PHASE_15_FRONTEND_FORMATTING.md,
PHASE_15_FRONTEND_LIVE.md, PHASE_15_FRONTEND_GIFT_SERVICE.md,
PHASE_15_GIFT_POPUP_CONTROLLER.md, PHASE_15_CHAMPIONSHIP_LIVE.md,
PHASE_15_RACE_RESULT_RECONCILE.md, PHASE_15_RACE_LIVE.md e
PHASE_15_REVIEW_INVENTORY_RECONCILE.md. ID/API: PHASE_15_GIFT_ID_MIGRATION.md,
PHASE_15_GIFT_SEEN_SELECTED.md. Concorrenza: PHASE_15_CONCURRENCY.md. Fix storici:
PHASE_15_CI_FIX.md (47df2a5), PHASE_15_STATE_EVENTS_FIX.md (53709a0).

Pendenti: sincronizzazione interna revisione e test integrati/browser; warning
canvas role img in card-crop-editor.svelte non corretto dal fix nullable. 15b da
definire dopo SSE. PROJECT_STATUS.md con riga 14 vecchia, manca 15 e data/descrizione
13e; PROJECT_SPEC.md da rileggere dopo bc0fbfb e refuso storico. PHASE_14_POST_MERGE.md/
aae6c33 storico, format-championships non verificato. README.md, SETUP.md e SCRIPTS.md
riletti in blocchi precedenti, comandi invariati; prima di altri aggiornamenti leggere
SHOP_DESIGN.md e PROJECT_NOTES.md. Backup/setup sicuro ancora da verificare nel codice.
config.py: cookie secure disattivato e URL SQLite fisso da sistemare per online.
Differenza Deck.cards tra istruzioni e codice in DATABASE.md, nessuna modifica formato/percorsi.

Questo push aggiorna solo quattro documenti: questa pagina, nota gara, nota risultati
e nota inventari. Nessuna modifica a codice, workflow, schema, dipendenze o dati.
PROJECT_SPEC.md e PROJECT_STATUS.md intatti. Solo .md: non attendere la CI per il
seguito e non attribuire esiti presunti. Prossimo blocco funzionale: collegare store
e pannello al merge inventari e alla coda live, con test mirati, poi riallineare.
Avviso e checklist manuale finale solo dopo completamento e relativi controlli verdi.
Nessun merge autorizzato.
