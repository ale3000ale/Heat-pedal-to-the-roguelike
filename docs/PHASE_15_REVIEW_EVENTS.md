# Fase 15a-3 - Eventi della conferma conteggi

Data: 2026-10-20. Ramo esclusivo phase-15-sse-sistemazione.
Integrazione di PHASE_15.md e PHASE_15_TIMER.md: fase ancora incompleta.

## Base verificata

CI verde sul commit be76f40: backend pytest, migrazioni e frontend completo;
esecuzione 39397520155. Il modulo timer ha superato la CI ma non e' attivato.

## File del blocco

Modificato backend/app/services/race/review_commit.py: solo il percorso di conferma
riuscita accoda race.review_changed (action counts_confirmed) e cards.changed
prima dello stesso commit che salva inventari, pool, giocate e chiusura.
I payload contengono soltanto race_id e azione; niente carte, conteggi o bozze.
Il salvataggio della bozza e il conflitto non generano conferme pubbliche.
Nessuna nuova migrazione, dipendenza o modifica di regole.

Nuovo backend/tests/test_review_commit_events.py: conferma e payload minimi,
conflitto senza eventi, errore simulato dopo flush con rollback di eventi,
inventario, pool e chiusura. Questo test non sostituisce la concorrenza reale.

## Verifiche

File di servizio e test esistenti riletti prima della modifica.
Test di questo blocco non eseguiti localmente: nuova CI da verificare dopo il push.
Nessuna modifica al database del gioco, nessun backup o migrazione effettuati.
PROJECT_SPEC.md e PROJECT_STATUS.md restano intatti; delta documentato qui.

## Resta prima di attivare il timer

Eventi nelle revisioni legacy, nei cambi di stato e nella scadenza; test di
atomicita' e concorrenza su file SQLite; aggancio lifecycle e riallineamento di
PHASE_15.md dopo le verifiche. Altre azioni di gioco e frontend ancora da integrare.
