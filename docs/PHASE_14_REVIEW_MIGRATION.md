# Fase 14j - Base dati della bozza

Data: 2026-10-19. Ramo: phase-14. Integrazione a PHASE_14.md per il successivo accorpamento.

Questa modifica aggiunge soltanto race.review_draft, TEXT nullable, e il campo del modello. La revisione esistente non usa ancora la colonna. Nessuna nuova rotta, conferma con conteggi o gestione della scadenza è inclusa.

Migrazione: a2e6c0d4f8b3, collegata a b4d8f2a6c0e3, non a f8a4d2c6e0b1. I test verificano testa unica, upgrade su database temporaneo con una gara esistente, valore iniziale NULL, ripetizione senza perdita della bozza e downgrade senza perdita della gara.

Verifiche: test predisposti, non eseguiti dall'assistente. Nessun backup creato e nessuna migrazione applicata al database reale. Prima dell'applicazione occorrono backup verificato e autorizzazione; il downgrade elimina le bozze.

Restano da implementare: validazione dei conteggi duplicati, controllo di tutte le carte e saldo aggregato della pool, persistenza e lettura della bozza, conferma atomica, scadenza selettiva e nuova interfaccia. SSE e aggiornamento dal vivo dello stato restano rinviati.
