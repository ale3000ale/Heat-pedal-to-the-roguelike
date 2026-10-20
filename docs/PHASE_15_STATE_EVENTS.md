# Fase 15a-3 - Eventi di stato della revisione

Data: 2026-10-20. Ramo phase-15-sse-sistemazione.
Nota integrativa di PHASE_15.md e PHASE_15_LEGACY_EVENTS.md.

## Base verificata

CI verde sul commit 0204e0d: backend, migrazioni e frontend
(run 39400531143). Conferma conteggi, conferma legacy e scadenza sono coperte.

## Modifiche

- review_events.py: nuovo record_review_changed senza commit; azioni opened,
  abandoned, reopened, started, cancelled. Payload: solo race_id e azione.
- race_review.py: begin_review, abandon_review, reopen_review, start_review e
  cancel_review accodano l'evento prima dello stesso commit dello stato.
  Ripresa della propria revisione gia' attiva, start gia' avviato e cancel senza
  blocco non generano eventi. Le regole di permesso e stato non cambiano.
- test_review_state_events.py: aperture ripetute, rinuncia, riapertura, blocco e
  sblocco prima dei risultati, rollback con stato invariato dopo errore evento.

## Limiti

Non e' ancora coperto il percorso set_results/Termina gara, che non e' stato
letto in questo blocco: potrebbe avviare la revisione senza usare queste funzioni.
Resta da verificarlo prima di dichiarare completi gli eventi di stato gara.
Sono ancora da integrare giocate, annullamenti, tasto S, risultati e classifica.
Test nuovi non eseguiti localmente: esito CI da leggere dopo il push.
Nessun database reale, migrazione, dipendenza o immagine modificati; nessun backup.
Timer ancora non attivo. PROJECT_SPEC.md e PROJECT_STATUS.md restano intatti.
