# Fase 15a-3 - Creazione gara, risultati e classifica

Data: 2026-10-20. Solo ramo phase-15-sse-sistemazione.
Integrazione di PHASE_15.md e PHASE_15_STATE_EVENTS.md.

## Base verificata

CI su 53709a0: backend, migrazioni e frontend success (run 39402153657).
Il test DetachedInstanceError corretto non blocca piu' la suite.

## File e comportamento

- races.py riletto insieme al router api/races.py: Termina gara imposta
  direttamente revisore e inizio revisione, senza passare da begin_review.
- create_race scrive race.started con race_id; flush prima dell'evento per
  ottenere l'id; rollback di gara ed evento su errore.
- set_results delega la preparazione a _set_results: un solo commit per risultati,
  saldi, oro, revisione ed eventi. Alla prima registrazione con reviewer_id emette
  race.review_changed/action opened. Ogni salvataggio valido emette
  race.results_changed e standings.changed (solo race_id nei payload).
- Correzioni mantengono le regole: non riassegnano oro e non riavviano revisione.
- Le scritture acquisiscono il lock SQLite esistente con import locale per
  evitare il ciclo shop_purchase -> races; rollback esplicito su ogni errore.
- test_race_events.py: creazione, prima chiusura, correzione, saldi e timestamp
  invariati, errori evento dopo flush con rollback di gara o risultati/saldi.
- test_review_timer.py: verifica che la pulizia elimini l'evento scaduto e mantenga
  quelli recenti, invece di pretendere un registro interamente vuoto.

## Verifiche e limiti

Test nuovi non eseguiti localmente: CI del blocco da leggere dopo il push.
Nessuna nuova migrazione, dipendenza, modifica al database reale o immagini.
Nessun backup eseguito. Timer ancora non collegato al lifespan.
Test concorrenti su SQLite file, lifecycle, giocate, annullamenti e tasto S
restano da completare. Il client SSE frontend e il fallback restano da collegare.
I dettagli correnti sono raccolti nelle note PHASE_15; documenti grandi intatti.
