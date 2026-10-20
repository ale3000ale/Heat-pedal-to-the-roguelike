# Fase 15 - Prerequisito: identita' stabile delle notifiche regalo

Data: 2026-10-20. Ramo phase-15-sse-sistemazione, PR 14 in bozza.
Blocco approvato separatamente prima della conferma selettiva e delle schermate.

## Problema e perimetro

Il modello CardGift e la migrazione storica e7a3c9d1f5b2 non impostavano
AUTOINCREMENT esplicito SQLite. Dopo l'annullo che elimina la riga con ID
massimo, un nuovo regalo poteva riutilizzare quell'ID. Una conferma tardiva
basata solo sull'ID avrebbe potuto segnare visto il regalo nuovo mai mostrato.
Caso individuato nell'analisi; non dichiarato riprodotto prima di questo blocco.

Quattro file del blocco:

- app/db/models/card_gift.py: sqlite_autoincrement=True nei table_args,
  conservando indice pilot_id/seen_at e indice id.
- Nuova migrazione d6f0a4b8c2e7, successiva a d5e9a3b7c1f6. Ricreazione batch
  online della sola card_gift, con riflessione dello schema e copia delle righe.
  Colonne, ID presenti, date, FK e indici vanno preservati. La migrazione storica
  non viene modificata. sqlite_sequence e' una tabella interna SQLite.
- tests/test_card_gift_autoincrement.py: migrazione su file temporaneo popolato,
  preservazione dati/schema, foreign_key_check, cancellazione ID massimo e intera
  tabella, upgrade ripetuto, downgrade/upgrade e annullo reale attraverso le API
  sul database della fixture creato dai modelli.
- Questa nota; riepilogo PHASE_15.md e documenti database da riallineare dopo CI.

Nessuna nuova colonna, dipendenza, modifica a Deck.cards o immagini.
Endpoint /seen attuale invariato; endpoint selettivo e frontend non ancora modificati.
AUTOINCREMENT impedisce il riuso futuro nel database migrato, non autentica le
richieste: proprietario, campionato e lista selettiva saranno verificati dall'API.

## Precauzioni operative

Non e' autorizzata o eseguita alcuna migrazione sul database del gioco.
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

## Verifiche reali e passo successivo

Riletti modello, migrazione storica, testa event_log, configurazione Alembic,
test delle migrazioni e verificatore CI. Test nuovi preparati ma non eseguiti.
Nessun comando locale, backup reale, upgrade o downgrade reale eseguito.
I test e il ciclo completo delle migrazioni devono passare in CI prima di
considerare verificata la modifica. Nessun numero di test o successo presunto.

Dopo CI: riallineare le note, poi preparare l'endpoint selettivo con schema,
servizio, route e test dei permessi e delle notifiche concorrenti. Il commit 2
frontend resta separato; nessun merge autorizzato.
