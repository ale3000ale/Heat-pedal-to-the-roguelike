# Fase 15 - Correzione test della catena Alembic

Data: 2026-10-20. Ramo: phase-15-sse-sistemazione.
Nota integrativa di PHASE_15.md e PHASE_15_DATABASE.md.

## Errore osservato

L'autore ha fornito il log pytest successivo al commit d43fbdf:
545 test passati e 1 fallito (test_review_draft_has_one_head).
Il test pretendeva che a2e6c0d4f8b3 fosse ancora la testa; la nuova migrazione
SSE d5e9a3b7c1f6 ne e' invece la discendente. L'asserzione obsoleta non era
stata controllata prima del push.

## Correzione

backend/tests/test_review_draft_migration.py ora verifica:
- una sola testa Alembic;
- a2e6c0d4f8b3 nella catena di antenati della testa corrente;
- down_revision della migrazione della bozza ancora b4d8f2a6c0e3.

REVISION e PREVIOUS non cambiano: il test di upgrade, conservazione delle
righe e della bozza, ripetizione e downgrade resta invariato.
Non si sostituisce semplicemente la testa storica con un nuovo valore fisso.

## Verifiche e limiti

Letto il file completo dal ramo prima della modifica.
Nessun comando di test eseguito localmente. Esito della CI della correzione
ancora da verificare dopo il push; non si dichiara il problema gia' risolto nei test.
Nessuna migrazione applicata ai dati reali, nessun backup eseguito e nessuna
modifica allo schema, ai servizi o alle dipendenze in questo commit.
I documenti generali restano invariati: la correzione riguarda soltanto il test.
