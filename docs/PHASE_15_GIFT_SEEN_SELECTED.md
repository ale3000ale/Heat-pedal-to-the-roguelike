# Fase 15 - API di conferma selettiva delle notifiche regalo

Aggiornamento: 2026-10-21. Ramo phase-15-sse-sistemazione, PR 14 in bozza.
API cda06a9 verificata in CI 39476606868. Prerequisito ID aa1a4c7 e migrazione
d6f0a4b8c2e7 verificati in CI 39467182291; riallineamento 21136eb in 39468896207.
Ora usata dal flusso campionato df7edf5/dc97fcf, CI 39502927035 verde.

## Contratto invariato

POST /api/championships/{championship_id}/card-gifts/seen-selected
JSON: {"pilot_id": 1, "gift_ids": [10, 11]}. Risposta 204 senza corpo.
Cookie obbligatorio, 401 senza sessione. Schema strict, extra vietati, ID interi
positivi int64 SQLite. Lista obbligatoria non vuota, massimo 100 elementi per
limitare query IN; duplicati ignorati. Input non valido: 422. Il servizio frontend
suddivide gia' le selezioni grandi per pilota e usa solo ID sicuri JavaScript.

Campionato esistente, pilota proprio non eliminato. Non trovato/non proprio:
404 generico, anche per admin/giudice senza proprieta'. Query con pilot_id e
campionato della gara della notifica. ID assenti, annullati, gia' visti o fuori
ambito ignorati senza rivelare notifiche altrui. Ammessi campionati chiusi per
ack storici, senza richiedere iscrizione attuale o gara in corso.

Solo seen_at ancora vuoto viene modificato sotto il lock SQLite nella stessa
transazione; ripetizioni mantengono la prima data. Niente carte, saldi, inventario
o eventi SSE. /card-gifts/seen storico invariato e compatibile. Il blocco API non
cambiava frontend o lifespan; il collegamento frontend e' successivo.
L'autorizzazione non dimostra che il browser abbia mostrato una notifica.

## Implementazione e verifiche

schemas/card_gift_seen.py, services/card_gift_seen.py e api/card_gift_seen.py;
main.py aggiunge import/router, lifespan invariato. test_card_gift_seen_selected.py:
sottoinsieme/nuovo regalo dopo lettura, idempotenza, annullo e nuovo regalo,
ambito pilota/campionato, permessi, strict/batch, rollback dopo flush e legacy.
La sequenza del nuovo regalo e' deterministica, non concorrenza a piu' processi.

Commit cda06a91799049022358df5cbb4129c91b83b7b2, run 39476606868 tutta verde il
2026-10-20: migrazioni 20:39:33 CEST, frontend 20:39:58, backend pytest 20:41:18.
Verificati esiti dei job, non log completi o conteggi. Nessun comando locale.
Nessuna nuova migrazione o dipendenza del blocco API. DB operativo deve gia'
includere d6f0a4b8c2e7: backup verificato, prova su copia e autorizzazione prima
dei dati reali; CI non certifica il database del gioco.

## Frontend corrente e seguito

La pagina campionato ora usa servizio, controller e coordinator condivisi e
invia solo gli ID resi, non tutta la coda. Annullamenti remoti non invocano ack.
Dettagli, commit bot dc97fcf e CI 39502927035 in PHASE_15_CHAMPIONSHIP_LIVE.md.
Il backend permette ack storici, ma la UI del campionato chiuso continua a non
aprire popup regali, come prima. Pagina gara e merge dei risultati pendenti.

Nessuna prova browser eseguita. Richiesta dell'autore del 2026-10-20 alle 20:37
CEST: avviso e checklist manuale finale dopo collegamento restante e CI verde.
Il riscontro delle 15:23 non viene esteso ai blocchi successivi. PROJECT_SPEC.md
e PROJECT_STATUS.md protetti. Solo riallineamento documentale, nuovo commit da
verificare separatamente in CI; nessun merge o intervento sui dati autorizzato.
