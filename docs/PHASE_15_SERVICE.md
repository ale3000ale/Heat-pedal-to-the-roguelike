# Fase 15 - Servizio transazionale degli eventi

Data: 2026-10-20. Solo ramo phase-15-sse-sistemazione.
Integrazione di PHASE_15.md, PHASE_15_DATABASE.md e PHASE_15_IMPLEMENTATION.md.

## Stato verificato prima di questo blocco

CI della PR 14 sulla correzione 47df2a5: backend, frontend e migrazioni success
(esecuzione 39340706339). Il problema del test della testa storica e' superato.

## File

- backend/app/services/core/event_log.py: accodamento validato senza commit;
  lettura ordinata e filtrata con pagine fino a 100 eventi; pulizia oltre 24 ore.
- backend/tests/test_event_log_service.py: isolamento dei privati anche verso
  admin e giudici, accesso pubblico per iscritti/ruoli, revoca per pilota nascosto,
  cursore, paginazione, rollback, soglia di conservazione e parametri non validi.

L'id utente deve provenire dall'autenticazione del server, non dal client.
Admin e giudice non ricevono dettagli privati delle carte altrui.
Nessuna funzione effettua commit: evento e azione potranno essere atomici.
Le funzioni non sono ancora collegate alle azioni o a un endpoint.
La pulizia esiste ma non e' ancora avviata da un timer.

## Rete e limiti

Letto frontend/src/lib/api.ts: usa /api e credentials same-origin tramite proxy,
non chiamate dirette. SSE manterra' la stessa origine previa verifica del proxy.
La lettura SSE dei pubblici e' limitata agli iscritti come concordato; le normali
API dei campionati attualmente consentono letture a ogni utente autenticato.
Il payload pubblico dovra' contenere solo informazioni pubbliche o invalidazioni,
mai carte private o bozze del revisore. La verifica della sessione e la gestione
Last-Event-ID appartengono al prossimo endpoint, non a questo servizio.

Test di questo blocco non eseguiti localmente: nuova CI da verificare dopo il push.
Nessuna nuova migrazione, nessuna modifica a dipendenze, database reale o immagini.
I documenti grandi restano intatti; questo file registra il delta del servizio.
