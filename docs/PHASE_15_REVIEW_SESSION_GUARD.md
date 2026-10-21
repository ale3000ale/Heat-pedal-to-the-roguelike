# Guardie sessione conteggi revisione

Aggiornamento: 2026-10-21. Solo phase-15-sse-sistemazione.
Preparazione 37e635c, bot 01c567a; CI 39636047244 verde su frontend, backend e
migrazioni di test. Cronologia dettagliata nella versione a36e536 e nella storia Git.

## Guardie conservate nel collegamento live

Store legato all'utente iniziale e alla chiave della revisione caricata, controllo
prima di inviare conteggi e fra PUT bozza e DELETE rinuncia. Progresso browser
sotto la chiave iniziale. Nessuna atomicita' aggiunta fra verifica e scrittura.
Sei test simulati: salvataggio consentito, titolare cambiato, nuovo inizio dello
stesso revisore, cambio fra PUT e DELETE, cambio utente, dispose durante verifica.

Dal bot 1145a9a queste guardie fanno parte dello store collegato realmente a SSE
e merge inventari. CI 39650297363 tutta verde, inclusi i test preesistenti e sette
nuovi casi simulati. Apertura al mount ora GET-only; merge, revoca spunte, blocchi
e recupero confermato implementati. Le precedenti indicazioni di integrazione
ancora pendente descrivevano il blocco storico 01c567a, non la testa corrente.
Dettagli in PHASE_15_REVIEW_LIVE_CONNECT.md.

Nessun comando locale o collaudo DOM/browser dell'assistente. Esiti/file modificati
letti, non log completi. Restano lifecycle del genitore al cambio fase, dialoghi e
warning canvas da valutare prima del collaudo finale. Nessuna modifica ad API,
backend, dati, dipendenze o documenti protetti in questo riallineamento solo .md.
Non attendere CI dei soli documenti. Nessun merge o intervento sui dati reali.
