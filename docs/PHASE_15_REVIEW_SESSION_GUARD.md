# Guardie sessione conteggi revisione

Aggiornamento: 2026-10-21. Applicate e verificate, non SSE completo.
Preparazione 37e635c; bot 01c567aeff63646ce9ad5eec4412e85bc25af9cd alle 18:34:46 CEST.
Il bot modifica solo store, formattazione test e stato di questa nota.

## Verifica riuscita

CI ordinaria 39636047244 sulla nuova testa, tutti i job success:
- Migrazioni (database di test): 18:35:53 CEST.
- Frontend (check, lint, test, build): 18:36:16 CEST.
- Backend (pytest): 18:37:54 CEST.

Esiti e file modificati letti; nessun log completo o conteggio dell'intera suite
presunto. Il workflow di applicazione formatta e verifica prima di pubblicare,
con blob sorgente vincolato e arresto se il ramo cambia, senza force push.

## Portata e limiti

Store legato all'utente iniziale e alla chiave della revisione caricata. Controllo
dopo caricamento e prima delle scritture dei conteggi, anche fra PUT bozza e DELETE
di rinuncia. Progresso browser sotto la chiave iniziale, nessun nuovo autosalvataggio.
Verifica e scrittura restano richieste distinte, non transazione o lock backend.

Sei test simulati: salvataggio consentito, titolare cambiato, nuovo inizio dello
stesso revisore, cambio fra PUT e DELETE, cambio utente, dispose durante verifica.
Non collaudano DOM o browser. Nessun comando npm locale eseguito dall'assistente.

Nessuna modifica a pannello, API, database, dipendenze o lockfile. Apertura al mount,
coda SSE interna, merge inventari, spunte remote e recupero confermato restano da
collegare. Riepilogo fase, nota gara e inventari riallineati nello stesso aggiornamento
solo documentale; non attendere CI dei soli .md. Documenti protetti intatti.
Nessun merge o intervento sui dati reali autorizzato.
