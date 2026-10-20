# Fase 15a-3 - Modulo timer, non ancora attivo

Data: 2026-10-20. Solo ramo phase-15-sse-sistemazione.
Integrazione di PHASE_15.md: la 15a-3 rimane incompleta.

## Base verificata

CI PR 14 sul commit a332633: backend, frontend e migrazioni success
(run 39342203544). Test locali non eseguiti.

## Questo blocco

Nuovi file: backend/app/services/review_timer.py, backend/tests/test_review_timer.py,
questa nota. Nessuna modifica a main.py o ai servizi di chiusura in questo blocco.
Il modulo non si avvia da solo e non e' ancora collegato al lifespan.

run_review_sweep cerca campionati aperti con revisioni scadute e risultati;
usa settle_expired_reviews senza modificare le regole. Ogni campionato ha una
sessione separata, chiusa prima del successivo. Errori inattesi sono loggati
con traceback; la scomparsa del campionato e' gestita separatamente.
La pulizia degli eventi, quando richiesta, ha una transazione distinta.

review_timer prevede controllo ogni 5 secondi e pulizia ogni ora (anche al primo
giro), SQL nel thread pool e arresto cooperativo tramite asyncio.Event.
L'arresto attende il giro SQL corrente: non promette un termine immediato se il
database e' occupato. Nessuna nuova dipendenza o migrazione.

## Test e limiti

Scritti test di scadenza senza nuova richiesta HTTP, ripetizione senza doppio
consumo, revisione ancora attiva, pulizia, arresto e intervalli invalidi.
Non eseguiti localmente: nuova CI da verificare dopo il push.
Il test di arresto sostituisce il thread pool; non dimostra la concorrenza reale.
Non e' ancora presente un test multi-worker con connessioni su SQLite file.

## Prossimo blocco obbligatorio prima dell'attivazione

Collegare eventi alle chiusure legacy, ai conteggi e alla scadenza nella stessa
transazione, senza pubblicare conferme per conflitti o rollback. Aggiungere test
di atomicita' e concorrenza. Poi avviare/arrestare il task nel lifespan e riallineare
PHASE_15.md dopo i check. Le altre azioni di gioco saranno integrate separatamente.
Nessun database reale o immagine modificati; nessun backup/migrazione eseguiti.
