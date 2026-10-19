# Fase 14j - Base dati e validazione della bozza

Data: 2026-10-19. Ramo: phase-14. Integrazione a PHASE_14.md per il successivo accorpamento.

## Base dati

Il commit 9a0a581 aggiunge race.review_draft, TEXT nullable, e il campo del modello. La revisione esistente non usa ancora la colonna. Migrazione a2e6c0d4f8b3, collegata a b4d8f2a6c0e3, non a f8a4d2c6e0b1.

I test predisposti verificano testa unica, upgrade su database temporaneo con una gara esistente, valore iniziale NULL, ripetizione senza perdita della bozza e downgrade senza perdita della gara.

## Conteggi in ingresso

schemas/review_counts.py introduce ReviewCountsRequest e i suoi elementi. Rifiuta piloti duplicati, carte duplicate dopo trim e casefold, nomi vuoti, quantità negative, quantità non intere, booleani al posto di interi, ID non positivi e campi sconosciuti. La conversione to_counts non sovrascrive duplicati. La stessa carta per piloti diversi è ammessa.

Il totale avuto dal pilota, l'appartenenza alla gara e il saldo aggregato della pool dovranno essere controllati dal servizio di dominio sui dati del database, non fidandosi di valori inviati dal browser. Gli schemi non sono ancora collegati alle rotte.

## Verifiche e limiti

Test predisposti, non eseguiti dall'assistente. Nessun backup creato e nessuna migrazione applicata al database reale. Prima dell'applicazione occorrono backup verificato e autorizzazione; il downgrade elimina le bozze.

Restano da implementare: controllo di tutte le carte e saldo aggregato della pool, persistenza e lettura della bozza, conferma atomica, scadenza selettiva e nuova interfaccia. Nessuna nuova rotta o modifica agli inventari è inclusa in questo passaggio. SSE e aggiornamento dal vivo dello stato restano rinviati.
