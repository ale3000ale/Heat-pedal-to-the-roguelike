# Fase 15a-4b - Riconciliazione conservativa inventari revisione

Aggiornamento: 2026-10-21. Solo phase-15-sse-sistemazione, PR 14 in bozza.
Modulo 05b2829, bot formattazione 6aa7fe6, CI 39599465230 tutti success:
migrazioni 14:26:26 CEST, frontend 14:26:47, backend 14:28:04 del 2026-10-21.
Cronologia dettagliata nella versione fcead0f e nella storia Git.

## Politica e funzioni

Politica approvata: conservare conteggi incompatibili senza clamp, bloccare
conferma, revocare spunte interessate, non trasferire bozze fra revisori/nuovi
inizi; rilettura che abbandona modifiche solo con conferma esplicita.

ownReviewKey distingue gara/revisore/inizio della propria revisione attiva.
Non autorizza HTTP e non sostituisce controllo server di scadenza.
reconcileReviewInventory confronta base server, copia locale e remoto con bozza
gia' applicata. Preserva remaining locali modificati con metadati remoti nuovi;
changedPilotIds ignora riordini e solo nome pilota, conflictingPilotIds segnala
conteggi concorrenti validi. Carte/piloti rimossi con modifiche o quantita' oltre
il nuovo totale producono issues/blocked e preservano l'intera copia locale.
Duplicati normalizzati o fonti server invalide generano RangeError, mai [].
Restituisce copie indipendenti, senza richieste REST o scritture.

## Collegamento effettivamente presente

Dal commit 01c567a lo store importa ownReviewKey per le guardie della sessione.
Non e' quindi piu' corretto dire che nessuna parte del modulo sia usata.
La funzione di merge reconcileReviewInventory NON e' ancora collegata allo store
o al pannello. Restano nuovi inventari live, revoca spunte da snapshot, blocchi UI
e recupero confermato. Le guardie preinvio non completano questa politica.

Le guardie hanno sei test mirati e CI 39636047244 verde su frontend, backend e
migrazioni di test. Dettagli in PHASE_15_REVIEW_SESSION_GUARD.md. Nessuna nuova
atomicita' fra verifica e scrittura, nessun lock ottimistico o cambio backend.

## API, verifiche e seguito

API rilette nei blocchi precedenti: inventario leggibile da giudice/admin senza
titolarita', bozza solo titolare attivo. GET stato puo' elaborare scadenze.
Il futuro collegamento non deve introdurre salvataggi/conferme agli eventi;
403/409 nelle letture richiedono verifica contesto, non bozze vuote fittizie.

Suite pura verificata: chiave/nuovo inizio, fonti pulite, conteggi locali, nuove
carte, immutabilita', totale ridotto, carta/pilota rimosso, conflitto valido,
snapshot vuoto riuscito e input invalidi. Test puri e guardie non sono prove DOM.
Letti esiti e commit, non log completi o conteggi dell'intera suite. Nessun comando
npm/formatter/lint/check/test/build locale eseguito dall'assistente.

Solo documenti in questo riallineamento; nessuna modifica a codice, workflow,
dipendenze, API, schema, immagini o dati. PROJECT_SPEC.md e PROJECT_STATUS.md
protetti. Non attendere CI dei soli .md. Collegare ora store/pannello a coda live,
fallback e merge nella stessa chiave, mantenendo copie, permessi e conferme.
Warning canvas e prove browser pendenti; avviso manuale finale dopo collegamenti
restanti e controlli verdi. Nessun nuovo prerequisito backend o merge autorizzato.
