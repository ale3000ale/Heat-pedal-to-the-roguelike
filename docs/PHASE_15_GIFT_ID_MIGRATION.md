# Fase 15 - Prerequisito: identita' stabile delle notifiche regalo

Data: 2026-10-20. Ramo phase-15-sse-sistemazione, PR 14 in bozza.
Blocco approvato separatamente prima della conferma selettiva e delle schermate.

## Problema e perimetro

Il modello CardGift e la migrazione storica e7a3c9d1f5b2 non impostavano
AUTOINCREMENT esplicito SQLite. Dopo l'annullo che elimina la riga con ID
massimo, un nuovo regalo poteva riutilizzare quell'ID. Una conferma tardiva
basata solo sull'ID avrebbe potuto segnare visto il regalo nuovo mai mostrato.
Caso individuato nell'analisi; non dichiarato riprodotto prima di questo blocco.

Quattro file implementativi del blocco:

- app/db/models/card_gift.py: sqlite_autoincrement=True nei table_args,
  conservando indice pilot_id/seen_at e indice id.
- Nuova migrazione d6f0a4b8c2e7, successiva a d5e9a3b7c1f6. Ricreazione batch
  online della sola card_gift, con riflessione dello schema e copia delle righe.
  Colonne, ID presenti, date, FK e indici preservati nelle prove sintetiche.
  La migrazione storica non viene modificata. sqlite_sequence e' interna SQLite.
- tests/test_card_gift_autoincrement.py: migrazione su file temporaneo popolato,
  preservazione dati/schema, foreign_key_check, cancellazione ID massimo e intera
  tabella, upgrade ripetuto, downgrade/upgrade e annullo reale attraverso le API
  sul database della fixture creato dai modelli.
- Questa nota, riallineata insieme a PHASE_15.md e DATABASE.md.

Nessuna nuova colonna, dipendenza, modifica a Deck.cards o immagini.
Il blocco ID lasciava invariati /seen e il frontend. Successivamente l'API
selettiva e' stata pubblicata in cda06a9 e verificata in CI 39476606868:
vedi PHASE_15_GIFT_SEEN_SELECTED.md. Il frontend non la usa ancora.
AUTOINCREMENT impedisce il riuso futuro nel database migrato, non autentica
le richieste: proprietario e ambito campionato/pilota sono verificati dal
servizio dell'API selettiva. /seen storico resta compatibile e invariato.

## Precauzioni operative

Nessuna migrazione sul database del gioco applicata dall'assistente.
Prima dell'applicazione locale: fermare l'app, creare e verificare un backup,
provare upgrade e controlli su una copia, poi autorizzare l'uso sui dati reali.
Non avviare heat.py start o setup prima di questi passaggi: applicano migrazioni.
La nuova migrazione richiede SQLite online e non produce SQL offline generico.

Il downgrade conserva le righe ma rimuove la garanzia di non riuso e la relativa
storia di allocazione: non usarlo mentre sono attivi client o endpoint che
richiedono ID stabili. Non riutilizzare conferme pendenti attraverso ripristini
di backup o ricreazioni del database. Dopo una migrazione operativa riavviare
il backend e ricaricare i client; non trasferire popup obsoleti tra copie DB.
Nessuna cancellazione, reset o modifica manuale di sqlite_sequence prevista.

## Verifiche reali

Commit implementativo: aa1a4c7aa6d1a2e56ef38ff3f95fc4ed93b33204.
Riletti modello, migrazione storica, testa event_log, configurazione Alembic,
test delle migrazioni e verificatore CI prima della preparazione.

CI della PR 14 verificata: run 39467182291, tutti i job success.
https://github.com/ale3000ale/Heat-pedal-to-the-roguelike/actions/runs/39467182291

| Job | Esito | Conclusione CEST del 2026-10-20 |
|---|---|---|
| Migrazioni (database di test) | success | 19:34:17 |
| Frontend (check, lint, test, build) | success | 19:34:44 |
| Backend (pytest) | success | 19:36:14 |

La suite backend include i nuovi test; il job migrazioni esegue il ciclo su
DB nuovo del runner. Verificati gli esiti dei job, non log completi o conteggi
numerici. Non si estende questa verifica al database reale dell'autore.
Nessun comando locale, backup reale, upgrade o downgrade reale eseguito
dall'assistente. Il successivo commit documentale richiede una CI separata.

## Passo successivo

Prerequisito ID e API selettiva verificati in CI nei rispettivi commit.
Il commit 2 frontend resta separato: collegare l'invio dei soli ID mostrati,
proteggere le modifiche locali e attivare polling soltanto senza stream open.
Non richiedere test manuali finali prima del collegamento e della relativa CI
verde; avvisare esplicitamente l'autore a quel punto. Nessun merge autorizzato.
