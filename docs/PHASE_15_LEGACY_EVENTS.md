# Fase 15a-3 - Chiusura legacy e scadenza con eventi

Data: 2026-10-20. Ramo phase-15-sse-sistemazione.
Nota integrativa di PHASE_15.md, PHASE_15_TIMER.md e PHASE_15_REVIEW_EVENTS.md.

## Base verificata

CI del commit 5fe65ea tutta verde: backend, frontend e migrazioni
(run 39399546044). Conferma conteggi e relativi test pubblicati.

## Modifiche

- review_events.py: helper senza commit per race.review_changed e cards.changed.
  Payload pubblici minimi: race_id e action confirmed/expired, senza carte o bozze.
- race_review.py: helper prima del commit di confirm_review e di ogni scadenza
  confermata. Le bozze scadute mantengono l'applicazione delle sole carte coerenti.
- Ricontrollo sotto lock di gara esistente, campionato aperto, revisione ancora
  iniziata/non confermata, scadenza e presenza risultati. La gara viene riletta
  con populate_existing, per non usare uno stato ORM precedente al lock.
- test_review_close_events.py: legacy, ripetizione, scadenza, errore dopo flush
  con rollback completo e annullamento simulato tra ricerca e lock.

L'annullamento simulato e' un test di interleaving, non un test multi-worker reale.
Gli eventi di apertura, rinuncia, riapertura e blocco pre-risultati restano da
collegare, come gli eventi delle altre azioni di gioco.

## Verifiche e prossimo passo

Servizi riletti prima della modifica. Test nuovi non eseguiti localmente;
esito della nuova CI da leggere dopo il push. Nessun successo presunto.
Nessun database reale, migrazione, dipendenza o immagine modificati.
Il timer rimane non attivo: prima servono test concorrenti su file SQLite e
aggancio controllato al lifespan. Poi riallineare PHASE_15.md e documenti piccoli.
PROJECT_SPEC.md e PROJECT_STATUS.md restano intatti come richiesto.
