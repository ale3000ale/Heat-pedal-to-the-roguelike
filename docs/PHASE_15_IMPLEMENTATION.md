# Fase 15 - Registro di implementazione

## Primo blocco della 15a-1 - 20 ottobre 2026

Ramo esclusivo: phase-15-sse-sistemazione. Documento integrativo di PHASE_15.md.

File introdotti:
- backend/app/schemas/core/events.py: contratto Pydantic degli eventi, tipi espliciti,
  identificativi interi positivi, destinatario privato facoltativo e payload JSON.
- backend/tests/test_event_schemas.py: test di validazione e indipendenza dei payload.

Il destinatario privato è esplicito: il solo pilot_id non costituisce un controllo
  di accesso. Le autorizzazioni reali saranno applicate dal servizio di lettura.

Questo blocco non crea tabelle, non registra endpoint, non cambia dipendenze e
non abilita ancora SSE. Non modifica database, configurazioni o immagini.
I documenti del database e del setup restano invariati perché schema SQL e
procedura di installazione non cambiano in questo blocco.

Verifiche: letti i modelli Pilot, Championship, CardGift, il registro dei modelli,
le fixture pytest, le dipendenze dichiarate, il servizio card_gift e due migrazioni
recenti. La testa unica dell'intero grafo Alembic non è ancora verificata.
Test di questo blocco non eseguiti localmente; esito CI da leggere dopo il push.
Nessun backup o migrazione eseguiti. Nessun successo di test presunto.

Prossimo blocco: verifica completa del grafo Alembic, modello e servizio
transazionale event_log, migrazione e test su database temporaneo. Prima di
applicare una migrazione al database del gioco è obbligatorio un backup.
