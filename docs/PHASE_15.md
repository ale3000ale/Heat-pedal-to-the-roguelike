# Fase 15 - SSE in tempo reale e sistemazione

Aggiornamento: 2026-10-21. Solo phase-15-sse-sistemazione; PR 14 in bozza.
Base main 2cded6d. Nessun merge o intervento sui dati reali autorizzato.
Riepilogo corrente; cronologia estesa nelle versioni fcead0f/a36e536, note e Git.

## Collegamenti verificati

| Blocco | Testa | CI verde |
|---|---|---|
| Client condiviso | 33f01f0 | 39425660561 |
| Coalescer e fallback | fb4f128 | 39457551822 |
| ID CardGift e migrazione d6f0a4b8c2e7 | aa1a4c7 | 39467182291 |
| Conferma selettiva | cda06a9 | 39476606868 |
| Servizio notifiche | de29e70 | 39497343267 |
| Controller e popup | 936f27b | 39500026385 |
| Campionato collegato | dc97fcf | 39502927035 |
| Merge risultati puro | 3c860d2 | 39509635060 |
| Gara e fix nullable | 4978f73 | 39596834057 |
| Merge inventari puro | 6aa7fe6 | 39599465230 |
| Guardie sessione store | 01c567a | 39636047244 |
| Store/pannello inventari live | 1145a9a | 39650297363 |

Backend SSE, eventi e timer gia' verificati nei blocchi precedenti.
Campionato usa /seen-selected per i soli regali resi, snapshot e popup riconciliati;
annulli/chiusure remote non confermano notifiche. Gara preserva ordine/assenti come
assegnazione unica e sponsor locali per pilota, aggiorna ufficiali/permessi e usa
PUT esplicita con copia preinvio. Bozza risultati in sola lettura se perde permesso;
uscita protetta con modifiche/PUT, senza annullare HTTP gia' partite.

## Inventari: ora realmente collegati

Store e pannello usano coda live condivisa e reconcileReviewInventory. Mount senza
POST, ripresa GET della revisione propria. autoOpen resta richiesta GET accorpata.
Bozza mai richiesta quando lo stato non indica titolarita'; confronto chiave anche
dopo risorse, verifica contesto su 403/409 senza convertirli in bozze vuote.
Base server distinta, remaining locali preservati con metadati remoti, revoca spunte
interessate. Incompatibilita' congela la copia senza clamp e blocca editing/conferma.
Cambio titolare/inizio non trasferisce lavoro automaticamente. Guardie utente e
preinvio mantenute; nessun ETag, lock ottimistico o atomicita' nuova nel backend.

Rilettura/apertura che sostituisce lavoro richiede conferma e backup browser
riuscito; copie distinte mai eliminate, precedente visibile nella vista. Fallimento
storage interrompe il recupero. Progresso legacy revoca spunte; non applicabile
conservato come testo. Recupero confermato puo' ignorare un'esatta bozza server
incompatibile nella stessa revisione; un nuovo contenuto incompatibile riblocca.
Nessuna scrittura REST dei conteggi agli eventi. Risposte durante scritture o di
generazioni precedenti non applicate; nuova lettura accorpata dopo le azioni.
401/auth.expired fermano il contesto senza svuotare un diverso utente sopraggiunto.

Bot 1145a9af097b839a06e10e7bd22df9e742a4520f alle 20:10:11 CEST del 2026-10-21.
Modifica solo store, pannello, sette test simulati e stato della nota live.
CI ordinaria 39650297363 della nuova testa: migrazioni di test success 20:12:09,
frontend check/lint/test/build success 20:12:36, backend pytest success 20:14:01.
Esiti e file modificati letti, non log completi o conteggio totale suite.
Primo tentativo 23b6bda fermato da sette errori ESLint; non gli si attribuiscono
check/test/build riusciti. Preparazione fix dbe8204, nessuna regola disattivata.

## Invarianti e sicurezza dati

Un EventSource condiviso. Polling/card_poll_seconds solo senza stream open, mai
polling lento di sicurezza. Countdown con rilettura alla scadenza senza riarmare
su scadenza trascorsa. Eventi carte, gara/revisione, risultati e classifica, non ogni
CRUD/impostazione. Event_log persistente, ID non riusati, eventi nella transazione;
stream autenticato, resync e auth.expired. Payload pubblici senza conteggi o bozze.
Replay rilegge REST autorizzate e non ricrea popup. Nessun retry delle scritture.

Timer per worker ogni 5 secondi, stop cooperativo e pulizia registro, nessuna
migrazione nel lifespan. Test a due processi sullo stesso SQLite sintetico, non
prove di carico/multi-host. Uso previsto a bassa affluenza, piu' worker sullo stesso
SQLite e /api same-origin. Proxy reale e buffering non collaudati.

Nessun dato reale migrato, salvato in backup o modificato dall'assistente. Anche
heat.py start/setup migrano: arresto app, backup verificato, prova su copia e
permesso prima dell'uso reale. Catena letta a2e6c0d4f8b3, d5e9a3b7c1f6,
d6f0a4b8c2e7, merge b2d6f0a4c8e1. Downgrade perde storia/garanzia non riuso:
non usarlo con client che dipendono da ID stabili. Non trasferire conferme pendenti
fra backup/DB ricreati. CI sintetica non certifica gli originali. Differenza
Deck.cards in DATABASE.md, nessun cambio di formato o percorsi.

## Pendenti e seguito

Il genitore puo' smontare/nascondere il pannello per stato/permessi: copia visibile
fino allo smontaggio, progresso nel browser sotto chiave propria. Da valutare e
collaudare cambio fase, dialoghi, permessi, callback e chiusure durante richieste.
Nessuna nuova prova DOM/browser dell'assistente. Warning canvas role img in
card-crop-editor.svelte ancora pendente. SSE non dichiarato complessivamente concluso.
Nessun avviso/checklist manuale finale prima della valutazione di questi confini.

npm ci ha segnalato 10 vulnerabilita' (6 low, 2 moderate, 2 high), non risolte qui;
nessun audit fix/force o aggiornamento dipendenze autorizzato. Backup/setup sicuro
ancora da verificare; cookie secure disattivato e URL SQLite fisso in config.py
pendenti per online. 15b da definire dopo SSE. PROJECT_SPEC.md e PROJECT_STATUS.md
protetti, loro riallineamento ancora da autorizzare. Prima di aggiornamenti generali
leggere SHOP_DESIGN.md e PROJECT_NOTES.md. Comandi setup/database invariati.

Dettagli: PHASE_15_CHAMPIONSHIP_LIVE.md, PHASE_15_RACE_LIVE.md,
PHASE_15_RACE_RESULT_RECONCILE.md, PHASE_15_REVIEW_INVENTORY_RECONCILE.md,
PHASE_15_REVIEW_SESSION_GUARD.md e PHASE_15_REVIEW_LIVE_CONNECT.md; altre note
restano cronologia dei propri blocchi. Nessun comando npm locale dell'assistente.
Questo aggiornamento cambia solo cinque .md: non attendere CI e non attribuire
esiti presunti al commit documentale. Prossimo passo: valutare lifecycle del
genitore e warning prima del collaudo finale, non altri moduli preparatori.
