# Merge inventari e integrazione verificata

Aggiornamento: 2026-10-21. Solo phase-15-sse-sistemazione.
Modulo 05b2829/6aa7fe6, CI 39599465230; guardie 01c567a, CI 39636047244;
collegamento 1145a9a, CI 39650297363; lifecycle 8018d18, CI 39658083388. Tutte verdi
nei rispettivi blocchi. Cronologia completa in Git e nelle versioni precedenti.

ownReviewKey distingue gara/revisore/inizio proprio attivo, non autorizza HTTP.
reconcileReviewInventory confronta base, locale e remoto con bozza applicata.
Remaining modificati conservati, metadati remoti aggiornati, changedPilotIds ignora
riordino/solo nome, conflictingPilotIds segnala concorrenza valida. Rimozioni con
modifiche e quantita' oltre il nuovo totale producono issues/blocked e copia intera,
senza clamp. Duplicati/fonti server invalide generano RangeError, non []. Copie
indipendenti; modulo puro senza REST. Store e pannello ora usano realmente il merge.

Load legge bozza solo da stato proprio, verifica chiave dopo risorse, 403/409 non
sono bozze vuote. GET stato puo' elaborare scadenze. Apply scarta generazioni vecchie
o letture durante scritture, revoca spunte interessate, preserva incompatibilita'
e blocca editing/conferma. Recupero con conferma e backup browser obbligatorio;
fallimento storage interrompe operazione. Nessuna scrittura conteggi agli eventi.
Bozza incompatibile esatta puo' essere ignorata solo nel recupero confermato della
stessa revisione; un nuovo contenuto incompatibile riblocca. Nessuna nuova atomicita'.

Dal lifecycle 8018d18, cambio di solo stato non ricrea il pannello gia' mostrato;
enabled del genitore puo' congelare editing/copie senza smontarlo. Chiave sempre
separata per contesto/utente, perdita ruolo puo' nascondere la vista. Tre nuovi test
del limite del genitore oltre ai sette live e alle suite precedenti. Test simulati,
non DOM/browser. Diff ed esiti letti, nessun totale suite inventato.

Prova browser ancora da eseguire: PHASE_15_BROWSER_CHECKLIST.md, dati isolati e
risultati per caso. Nessun npm locale o successo manuale dell'assistente. Canvas
non piu' bloccato dalla diagnostica, interazioni da collaudare. Solo documenti qui;
nessun API/schema/DB, dipendenza o workflow modificato. Documenti protetti intatti,
nessun merge; non attendere CI di questo aggiornamento solo .md.
