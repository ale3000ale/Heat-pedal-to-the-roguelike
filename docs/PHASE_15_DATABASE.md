# Fase 15 - Registro SSE e migrazione

Data: 2026-10-20. Ramo: phase-15-sse-sistemazione.
Integrazione di PHASE_15.md e DATABASE.md: non sostituisce lo schema storico.

## Verifica della catena

Letti i 19 file di backend/alembic/versions. Unica testa ricostruita dai
revision/down_revision: a2e6c0d4f8b3. Il merge storico b2d6f0a4c8e1 unisce
il ramo negozio a1c5e9b3d7f2 e il ramo oro c9f3a1b6d8e4.
La nuova revisione d5e9a3b7c1f6 dipende da a2e6c0d4f8b3.
Questa verifica deriva dalla lettura dei file, non dall'esecuzione locale di alembic heads.

## event_log

- id INTEGER, chiave primaria con AUTOINCREMENT SQLite: gli id confermati non
  vengono riutilizzati dopo la pulizia, anche se il registro si svuota.
- type VARCHAR(64), championship_id INTEGER, payload TEXT JSON, created_at DATETIME:
  obbligatori. created_at usa CURRENT_TIMESTAMP (UTC).
- pilot_id INTEGER e recipient_user_id INTEGER: facoltativi.
- Chiavi esterne: championship_id verso championship.id con CASCADE;
  pilot_id verso pilot.id con SET NULL; recipient_user_id verso user.id con CASCADE.
  Eliminare un utente elimina i suoi eventi privati, senza trasformarli in pubblici.
- Indici: (championship_id, id), (recipient_user_id, id), created_at.
- Il modello non applica autorizzazioni e non scrive autonomamente gli eventi.
  Il servizio transazionale e il filtro di lettura sono il prossimo blocco.
- Conservazione pianificata: 24 ore; nessuna pulizia automatica ancora collegata.

## File e verifiche

Nuovi: modello event_log.py, migrazione d5e9a3b7c1f6, test_event_log_model.py,
questo documento. Modificato solo il registro app/db/models/__init__.py.
Nessun endpoint o timer aggiunto. Nessuna modifica a Deck.cards, immagini o dipendenze.
I test coprono indici, rollback con l'azione, id non riutilizzati e cancellazione
in cascata del campionato su SQLite temporaneo.
Test non eseguiti localmente: esito della nuova CI da leggere dopo il push.
Il precedente blocco b9c50dc ha superato backend, frontend e migrazioni in CI.

## Sicurezza del database reale

Non è stata applicata alcuna migrazione al database del gioco e non è stato
eseguito alcun backup. Prima di una migrazione reale occorrono backup verificato
ed esecuzione su copia. La pubblicazione del file Alembic non autorizza a migrare
i dati reali. Il downgrade elimina gli eventi: backup e conferma obbligatori.
La CI esegue upgrade/downgrade/upgrade su un database nuovo del runner.
PROJECT_SPEC.md e PROJECT_STATUS.md restano intatti come richiesto dall'autore.
