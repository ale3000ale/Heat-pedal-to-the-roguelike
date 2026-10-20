# Fase 15 - Correzione del test rollback degli eventi di stato

Data: 2026-10-20. Ramo esclusivo phase-15-sse-sistemazione.
Integrazione di PHASE_15.md e PHASE_15_STATE_EVENTS.md.

## Errore verificato

CI del commit 56e5740: backend fallito, frontend e migrazioni riusciti.
Il log fornito dall'autore riporta 584 passed e 1 failed in 75.82 secondi.
La riga finale di test_state_change_rolls_back_when_event_fails leggeva owner.id
quando l'oggetto User, scaduto dal rollback, era gia' scollegato dalla sessione:
DetachedInstanceError. Errore introdotto nel test dall'assistente.

## Correzione

backend/tests/test_review_state_events.py conserva owner_id prima della chiamata
che provoca rollback e lo usa nell'asserzione finale. Mantiene la verifica che
la revisione e il titolare non cambino e che nessun evento resti salvato.
Import regolari per EventCreate e abandon_review; rimosso l'import dinamico.
Nessuna disattivazione o rimozione di test, nessuna modifica alle fixture globali
o alle impostazioni di scadenza degli oggetti SQLAlchemy.

## Verifiche

File completo riletto dal ramo prima della modifica.
Test corretti non eseguiti localmente; esito nuova CI da verificare dopo il push.
Nessuna modifica a servizi, database reale, migrazioni, dipendenze o immagini.
Timer ancora non attivo. Documenti grandi lasciati intatti come richiesto.
