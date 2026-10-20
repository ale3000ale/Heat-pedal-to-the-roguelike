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
Commit implementativo: 8e1f440e13dfc4bd36c7839ec49b411dd72e68fe.
CI della PR 14 verificata e ricontrollata: run 39414943186.
https://github.com/ale3000ale/Heat-pedal-to-the-roguelike/actions/runs/39414943186

| Job | Esito | Conclusione CEST del 2026-10-20 |
|---|---|---|
| Backend (pytest) | success | 13:28:32 |
| Frontend (check, lint, test, build) | success | 13:26:59 |
| Migrazioni (database di test) | success | 13:26:38 |

Tutti i job sono completati. Sono stati letti gli esiti, non i conteggi dei test
nei log pytest; non viene dichiarato un numero di test eseguiti.
Test locali non eseguiti. Nessuna nuova migrazione o dipendenza.
Nessuna modifica al database reale o alle immagini, nessun backup reale,
nessuna prova browser o deployment. La CI non verifica una connessione SSE
end-to-end attraverso il proxy e non certifica l'uso sui dati del gioco.
Il successivo commit di solo riallineamento documentale richiedera' una
verifica CI separata; il verde qui registrato riguarda il codice 8e1f440.

## Prossimo passo

Le correzioni del revisore sono collegate e verificate in CI.
Dopo il riallineamento delle note, presentare l'analisi e i file previsti del
client frontend SSE per approvazione. Reconnect, resync, auth.expired e fallback
polling restano da implementare nella sottofase 15a-4.
PROJECT_SPEC.md e PROJECT_STATUS.md intatti secondo la decisione in PHASE_15.md.
