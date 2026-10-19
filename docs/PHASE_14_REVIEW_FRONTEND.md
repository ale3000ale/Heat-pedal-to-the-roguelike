# Fase 14j - Client frontend della revisione

Data: 2026-10-19. Ramo phase-14. Integrazione alle note della fase 14.

Aggiunti tipi per inventari, conteggi e incongruenze, conversione della richiesta completa e logica +/− limitata tra zero e totale avuto. Il client legge inventario e bozza e salva la bozza con il servizio API esistente. La conferma usa un fetch dedicato con gli stessi cookie e prefisso /api: il servizio API generale attuale elimina i dettagli strutturati degli errori, mentre il popup richiede l'elenco completo delle incongruenze.

ReviewConflictError conserva l'elenco validato restituito dal backend. Altri errori restano ApiError con stato e messaggio. Non è stato modificato il servizio API condiviso, evitando effetti sulle altre pagine.

Sei test Vitest predisposti per limiti +/−, correzione, conteggi incoerenti, conservazione delle incongruenze e permessi. Non eseguiti dall'assistente; lint, type-check e build non eseguiti.

## Segnalazione CI e correzione della formattazione

Il 2026-10-19 l'autore ha riportato npm run lint fallito su Prettier, con tre file: review-counts-api.ts, review-counts.spec.ts e review-counts.ts. ESLint non è stato raggiunto perché lo script usa prettier --check . && eslint . La configurazione letta è frontend/prettier.config.js: tab, apici singoli, nessuna virgola finale, larghezza 100.

La correzione proposta modifica soltanto la formattazione dei tre file. È stata preparata manualmente: Prettier, ESLint, test, type-check e build non sono stati eseguiti dall'assistente. Serve un nuovo esito CI; non è dichiarato superato.

Il pannello attuale e il suo store non sono ancora modificati: nessun cambiamento visibile nell'interfaccia in questo commit. Prossimo passo: collegamento del nuovo store e dei componenti pilota/popup, navigazione, spunte e recupero della bozza. Nessuna modifica al database o alle migrazioni.
