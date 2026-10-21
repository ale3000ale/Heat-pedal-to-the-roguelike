# Fase 15 - SSE: implementazione e riscontri

Aggiornamento: 2026-10-21. Solo phase-15-sse-sistemazione; PR 14 in bozza.
Base main 2cded6d. Nessun merge autorizzato. Storia estesa in Git e nelle versioni
fcead0f/a36e536/cc8ba7a/b1035c2 e nelle note dei singoli blocchi.

## Verifiche automatiche

| Blocco | Commit | CI ordinaria verde |
|---|---|---|
| Campionato collegato | dc97fcf | 39502927035 |
| Gara e nullable corretto | 4978f73 | 39596834057 |
| Merge inventari puro | 6aa7fe6 | 39599465230 |
| Guardie sessione | 01c567a | 39636047244 |
| Store/pannello live | 1145a9a | 39650297363 |
| Lifecycle e canvas | 8018d18 | 39658083388 |
| Iscrizioni anche per osservatori | 1226172 | 39674942800 |

Ultimo bot 12261725bc3439cd3e593fda152e050563b0988f alle 22:58:37 CEST.
CI del 2026-10-21: migrazioni sintetiche success 23:00:16 CEST, frontend
check/lint/test/build success 23:00:48, backend pytest success 23:02:07.
Esiti e file modificati letti. Nessun comando npm/pytest locale dell'assistente.
Vecchi job rossi descrivono tentativi precedenti, non la testa corretta; non
rieseguire workflow di applicazione vincolati a blob ormai modificati.

## Riscontro manuale autore

Alle 22:39: PASS 1/4/5/6/7/9; non verificabili 2/3; non eseguiti 8/10.
Segnalata iscrizione non aggiornata nelle altre sessioni; alle 22:41 precisato
sia iscritti sia osservatori autenticati non iscritti. Fix 1226172 verificato in CI.
Alle 23:24, dopo richiesta di riprova, autore: "funziona". Conferma complessiva
riferita alle iscrizioni live; non sono stati forniti log, commit locale o dati
browser, ne' esiti separati dei due scenari. Il riscontro non copre i casi saltati.
Dettagli e stato per caso in PHASE_15_BROWSER_CHECKLIST.md e PHASE_15_ENROLLMENT_LIVE.md.

## Comportamento corrente

Campionato rilegge snapshot completo e popup dei soli regali propri; ack selettivo
/seen-selected solo per gli ID resi e chiusura volontaria. Niente ack per annulli
remoti. Risultati gara preservano ordine/assenti come assegnazione unica e sponsor
per pilota; PUT esplicita con copia preinvio, bozza in sola lettura se perde permesso,
uscita protetta senza annullare HTTP gia' partite.

Inventari con coda condivisa e merge conservativo: mount GET-only, bozza propria,
verifica chiave dopo risorse e prima delle scritture; 403/409 non diventano [].
Remaining locali preservati, metadati remoti applicati e spunte interessate revocate.
Incompatibilita' conserva copie senza clamp e blocca editing/conferma. Recupero
sostitutivo con dialogo e backup browser riuscito, copie distinte mai eliminate;
fallimento storage interrompe. Progresso legacy revoca spunte, non applicabile
resta testo. Bozza server incompatibile ignorata solo per l'esatto contenuto e
chiave dopo recupero confermato, nuovo contenuto riblocca. Nessuna PUT agli eventi.

Lifecycle conserva il pannello gia' mostrato sul solo cambio stato, nello stesso
contesto/utente per i gestori. enabled limita scritture senza sostituire copie;
riabilitazione rilegge e revoca spunte. Nuovo contesto/perdita ruolo possono smontare.
Canvas senza ruolo img non consentito, controllo nativo con focus/tastiera/pointer;
Maiusc fine e Invio/Spazio esportano. Correzione automatica e caso 7 PASS dichiarato.

Nuovo championship.pilots_changed: solo ID campionato, pilot_id nullo e payload
vuoto, registrato con iscrizione/reset nella stessa transazione. Solo questo
segnale canonico raggiunge anche osservatori autenticati non iscritti; gli altri
eventi mantengono filtri precedenti. Il client invalida la coda gia' esistente e
rilegge REST autorizzate, senza nomi/carte/conteggi nel segnale, nuovo polling o
secondo stream. Nessun endpoint, modello SQL o migrazione aggiunto.

## Limiti e sicurezza

Un EventSource per applicazione nella scheda, fallback/card_poll_seconds solo senza
open, nessun polling lento di sicurezza. Event_log persistente, ID non riusati,
eventi e azioni transazionali; replay via REST, nessun popup ricreato dal replay.
Timer per worker ogni 5 secondi, stop cooperativo e pulizia senza migrazioni nel
lifespan. Test su SQLite sintetico, anche due processi: non carico o multi-host.
Proxy/buffering reale non collaudati. Verifica preinvio e scrittura restano distinte,
nessun nuovo ETag o lock ottimistico. Sessione verificata a ogni ciclo SSE.

DB originale mai migrato, modificato o salvato in backup dall'assistente. Anche
heat.py start/setup possono migrare: arresto app, backup verificato, copia isolata
e permesso prima dell'uso reale. Catena letta a2e6c0d4f8b3/d5e9a3b7c1f6/d6f0a4b8c2e7,
merge b2d6f0a4c8e1; downgrade perde storia/garanzia non riuso. Non trasferire conferme
tra backup/DB ricreati. Differenza Deck.cards in DATABASE.md, nessun cambio formato.

## Stato e seguito

Fix iscrizioni confermato dall'autore; non risultano nuove anomalie segnalate su
questo fix. Collaudo manuale documentato ma non completo: 2/3/8/10 restano senza
verifica. Nessuna certificazione di accessibilita', produzione o SSE end-to-end
completo dalla sola CI. Non sono richieste altre modifiche funzionali in questo push.

Pendenti separati: vulnerabilita' npm segnalate (6 low, 2 moderate, 2 high), nessun
audit fix/force; backup/setup sicuro da verificare, cookie secure e SQLite fisso
in config.py per online; 15b da definire. PROJECT_SPEC.md/PROJECT_STATUS.md protetti,
riallineamento da autorizzare. Prima di aggiornamenti generali leggere SHOP_DESIGN.md
e PROJECT_NOTES.md. Nessun merge, produzione o migrazione reale impliciti.

Note di dettaglio: PHASE_15_CHAMPIONSHIP_LIVE.md, PHASE_15_RACE_LIVE.md,
PHASE_15_RACE_RESULT_RECONCILE.md, PHASE_15_REVIEW_INVENTORY_RECONCILE.md,
PHASE_15_REVIEW_SESSION_GUARD.md, PHASE_15_REVIEW_LIVE_CONNECT.md,
PHASE_15_REVIEW_LIFECYCLE_CANVAS.md e PHASE_15_ENROLLMENT_LIVE.md.
Questo riallineamento cambia solo quattro .md: non attendere relativa CI e non
attribuirle esiti presunti. Nessun codice, workflow, dipendenza o dato modificato.
