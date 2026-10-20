# Fase 15a-3 - Eventi di giocata e annullamento

Data: 2026-10-20. Ramo esclusivo phase-15-sse-sistemazione.
Integrazione di PHASE_15.md; la 15a-3 rimane incompleta.

## Base verificata

CI verde su 22d4aa4: backend, migrazioni e frontend (run 39408719258).
Il timer e' collegato al lifespan e i suoi test sono passati in CI.

## File del blocco

- card_events.py: helper senza commit. Evento privato card.played o
  card.play_undone al proprietario, con race_id/play_id; evento pubblico
  cards.changed con soli race_id/pilot_id. Nessun nome, immagine o conteggio.
- card_play.py: helper dopo la preparazione della giocata/annullo e prima del
  commit. Stesse autorizzazioni, limite annullamenti e disponibilita' precedenti.
- test_card_play_events.py: privati solo al proprietario, admin riceve soltanto
  invalidazioni pubbliche; annullo rifiutato senza nuovi eventi; errore dopo
  flush con rollback di eventi e stato delle giocate per entrambe le operazioni.

Il lettore SSE continua ad applicare i filtri di accesso gia' verificati.
Le invalidazioni pubbliche richiedono riletture autorizzate, non espongono carte.
Endpoint e codici HTTP riletti da api/card_play.py prima di scrivere i test.

## Verifiche e limiti

Nuovi test non eseguiti localmente: esito CI da verificare dopo il push.
Nessuna nuova migrazione, dipendenza, modifica al DB reale o alle immagini.
Nessun backup reale eseguito. Non riavviare sui dati reali senza backup e prova
su copia della migrazione event_log, come indicato in PHASE_15.md.
Tasto S, annullo assegnazione e correzioni del revisore restano da collegare.
Client SSE frontend e fallback ancora da implementare. Documenti grandi intatti.
