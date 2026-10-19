# Fase 14j - API dei conteggi

Data: 2026-10-19. Ramo phase-14. Integrazione alle note della fase 14.

Nuove rotte sotto /api/championships/{championship_id}/races/{race_id}/review:

- GET /draft: bozza validata o null; solo titolare di una revisione attiva.
- PUT /draft: salva la bozza, risposta 204 senza corpo, nessun movimento di carte.
- POST /counts/confirm: conferma con corpo ReviewCountsRequest; restituisce RaceReviewRead. Le incongruenze producono 409 con detail.message e detail.incongruities e conservano soltanto la bozza.

Le dipendenze esistenti autorizzano giudice/admin. Un altro giudice riceve 409 quando non è titolare. Richieste duplicate o malformate ricevono 422. La lettura di una bozza corrotta restituisce 409 senza sostituirla o cancellarla.

main.py registra il router nuovo. La rotta legacy /review/confirm rimane invariata: il vecchio frontend continua a usarla, senza ancora i nuovi controlli. La nuova conferma richiede una revisione attiva; non sostituisce la conferma amministrativa legacy fuori dal timer.

Sei test API predisposti per bozza, conferma, incongruenze, permessi e duplicati; non eseguiti dall'assistente. Nessun test API/SQLite o CI dichiarato superato. Nessuna nuova migrazione e nessuna operazione sul database reale.

Restano da implementare scadenza selettiva, metadati delle spunte e nuovo frontend con popup. In particolare il comportamento richiesto alla scadenza non è ancora disponibile e non va considerato completato. Le altre note 14j descrivono i singoli moduli, non una funzionalità già conclusa.
