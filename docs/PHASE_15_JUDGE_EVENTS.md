# Fase 15a-3 - Eventi delle correzioni del revisore

Data: 2026-10-20. Ramo esclusivo phase-15-sse-sistemazione.
Integrazione di PHASE_15.md; nessun merge autorizzato.

## Base verificata e file

Base c6898da, CI verde run 39411533470: backend pytest, migrazioni su
DB di test e frontend check/lint/test/build. La PR 14 resta in bozza.

- card_judge.py: cancel_play accoda card.play_undone privato al proprietario
  e cards.changed pubblico tramite record_card_action. Vale anche per una
  giocata consumata dopo riapertura: il trasferimento resta nella transazione.
- judge_events.py: record_inventory_correction accoda soltanto cards.changed
  con race_id/pilot_id per bonus e rimozione. Nessun nome, immagine o conteggio.
  Nessun card.gifted, CardGift o popup regalo introdotto per queste correzioni.
- test_card_judge_events.py: annullo attivo/consumato, trasferimenti bonus e
  rimozione, privacy rispetto ad admin/giudice e utente non iscritto, rifiuti
  senza eventi, rollback dopo flush per tutte le operazioni.

Permessi HTTP, titolarita' della revisione, limiti di disponibilita', formato
Deck.cards e regole di consumo invariati. Gli helper non fanno commit.
Gli eventi richiedono riletture delle API autorizzate, non mostrano carte.

## Verifiche realmente svolte e limiti

Riletti card_judge.py, event_log.py, api/race_review.py, api/card_play.py e
la riapertura nei test; verificata la testa della PR prima della preparazione.
Test locali non eseguiti. Test aggiunti ma CI di questo blocco ancora da leggere
 dopo il push: il verde della base non certifica il nuovo codice.
Nessuna nuova migrazione o dipendenza. Nessuna modifica al database reale o
alle immagini, nessun backup reale, nessuna prova browser o deployment.
Dopo CI verde riallineare le note con l'esito effettivo.

## Prossimo passo

Verificare la CI del blocco e correggere eventuali errori prima del frontend.
Client SSE, gestione reconnect/resync/auth.expired e fallback polling restano
 da implementare in una sottofase separata con approvazione.
PROJECT_SPEC.md e PROJECT_STATUS.md intatti secondo la decisione in PHASE_15.md.
