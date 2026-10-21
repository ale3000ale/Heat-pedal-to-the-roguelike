# Fase 15 - SSE in tempo reale e sistemazione

Aggiornamento: 2026-10-21. Solo phase-15-sse-sistemazione; PR 14 in bozza.
Base iniziale main 2cded6d. Nessun merge o intervento sui dati reali autorizzato.
Riepilogo corrente abbreviato; cronologia completa nella versione fcead0f di
questo documento, nella storia Git e nelle note dei singoli blocchi.

## Stato verificato

| Blocco | Testa verificata | CI verde |
|---|---|---|
| Client condiviso | 33f01f0 | 39425660561 |
| Coalescer e fallback | fb4f128 | 39457551822 |
| ID CardGift e migrazione d6f0a4b8c2e7 | aa1a4c7 | 39467182291 |
| Conferma selettiva | cda06a9 | 39476606868 |
| Servizio notifiche | de29e70 | 39497343267 |
| Controller e popup | 936f27b | 39500026385 |
| Campionato collegato | dc97fcf | 39502927035 |
| Merge risultati puro | 3c860d2 | 39509635060 |
| Gara collegata e nullable corretto | 4978f73 | 39596834057 |
| Merge inventari puro | 6aa7fe6 | 39599465230 |
| Guardie sessione dello store | 01c567a | 39636047244 |

Backend SSE, event_log, eventi e timer erano gia' verificati nei blocchi precedenti.
Le nuove guardie non completano la sincronizzazione interna della revisione.

Campionato usa /seen-selected sui soli regali resi, non /seen generale. Snapshot
completi, popup riconciliati, nessuna conferma per annulli o chiusure remote.
Gara usa merge risultati, aggiorna ufficiali e permessi, preserva ordine/assenti
come assegnazione unica e sponsor locali per pilota. PUT esplicita con copia
preinvio; bozza risultati in sola lettura se il permesso viene meno. Protezione
uscita con modifiche o PUT in corso; uscire non annulla HTTP gia' partite.
Pannello usa onchanged, non reload browser, ed e' ricreato per contesto/stato.

## Revisione inventari: cosa e' realmente collegato

Il modulo puro review-inventory-reconcile.ts contiene ownReviewKey e il merge
conservativo. Dal commit 01c567a lo store usa ownReviewKey per legare i conteggi
all'utente e all'inizio revisione, ricontrolla lo stato dopo il caricamento e prima
delle scritture, anche fra PUT bozza e DELETE di rinuncia. Il progresso browser
resta sotto la chiave iniziale. Nessun nuovo salvataggio automatico.

Il merge reconcileReviewInventory NON e' ancora usato dallo store/pannello.
Restano sottoscrizione live interna, fallback, merge dei nuovi inventari, revoca
spunte sui dati remoti, blocco delle incompatibilita' e recupero con conferma.
La politica approvata conserva copie incompatibili senza clamp, non trasferisce
bozze fra revisori/nuovi inizi e richiede conferma per abbandonare modifiche.
403/409 nelle letture non devono diventare bozze vuote. Inventario leggibile per
giudice/admin; bozza solo titolare attivo. GET stato puo' elaborare scadenze.
Verifica preinvio e scrittura sono richieste distinte: nessun lock ottimistico,
ETag o nuova atomicita' backend. Il vecchio POST di apertura al mount resta nel
pannello: questo blocco non ha cambiato il suo lifecycle.

Implementazione guardie: preparazione 37e635c, bot 01c567aeff63646ce9ad5eec4412e85bc25af9cd.
CI 39636047244 del 2026-10-21: migrazioni di test success 18:35:53 CEST,
frontend check/lint/test/build success 18:36:16, backend pytest success 18:37:54.
Letti esiti e file modificati, non log completi o conteggi dell'intera suite.
Sei test mirati delle guardie, non prove DOM/browser. Nessun comando locale eseguito.

## Invarianti SSE e limiti

Un client EventSource condiviso; polling/card_poll_seconds solo senza stream open,
mai polling lento di sicurezza. Letture accorpate, cleanup di contesto, risposte
vecchie scartate secondo i singoli moduli; nessun retry automatico delle scritture.
Eventi carte, gara/revisione, risultati e classifica: non ogni CRUD o impostazione.
Event_log persistente con ID non riusati, eventi nella transazione dell'azione;
stream autenticato, resync e auth.expired. Payload pubblici senza carte private,
conteggi o bozze. Replay rilegge REST autorizzate, non ricrea popup.

Timer per worker ogni 5 secondi, stop cooperativo e pulizia periodica del registro;
nessuna migrazione nel lifespan. Test a due processi sullo stesso SQLite sintetico,
non prove di carico o multi-host. Uso previsto online a bassa affluenza, piu' worker
sullo stesso SQLite e /api same-origin. Proxy reale e buffering non collaudati.

Nessuna migrazione, backup o modifica dei dati reali eseguita dall'assistente.
Anche heat.py start/setup migrano: prima dell'uso reale arrestare app, autorizzare,
verificare backup e provare su copia. Catena letta a2e6c0d4f8b3, d5e9a3b7c1f6,
d6f0a4b8c2e7, merge storico b2d6f0a4c8e1. Downgrade perde storia/garanzia di non
riuso: non usarlo con client che dipendono da ID stabili. Non trasferire conferme
pendenti fra backup/DB ricreati. CI su DB sintetici non certifica gli originali.
Differenza Deck.cards documentata in DATABASE.md, nessun cambio di formato/percorsi.

## Seguito e documentazione

Dettagli correnti: PHASE_15_CHAMPIONSHIP_LIVE.md, PHASE_15_RACE_LIVE.md,
PHASE_15_RACE_RESULT_RECONCILE.md, PHASE_15_REVIEW_INVENTORY_RECONCILE.md,
PHASE_15_REVIEW_SESSION_GUARD.md. Altre note di contratto, servizio, eventi, timer,
concorrenza, client e notifiche restano riferimenti dei rispettivi blocchi.

Pendenti: integrazione interna inventari e prove browser; warning canvas role img
in card-crop-editor.svelte; 15b da definire dopo SSE. PROJECT_SPEC.md e
PROJECT_STATUS.md protetti: vecchia riga 14, fase 15 mancante e descrizione/data 13e
restano da riallineare con autorizzazione. Prima di altri aggiornamenti generali
leggere SHOP_DESIGN.md e PROJECT_NOTES.md. Backup/setup sicuro da verificare;
cookie secure disattivato e URL SQLite fisso in config.py da sistemare per online.

Questo aggiornamento cambia solo quattro .md: riepilogo, nota gara, inventari e
guardie. Nessuna modifica a codice, workflow, dipendenze o dati. Non attendere CI
per i soli .md e non attribuire loro esiti presunti. Prossimo blocco funzionale:
collegamento effettivo store/pannello al merge e alla coda live. Avviso e checklist
manuale finale solo dopo collegamenti restanti e controlli verdi. Nessun merge.
