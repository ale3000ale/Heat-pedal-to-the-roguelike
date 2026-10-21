# Gara e revisione live - stato corrente

Aggiornamento: 2026-10-21. Solo phase-15-sse-sistemazione, PR 14 in bozza.
Gara: 4833a8d, nullable 44bb4dd, bot 4978f73, CI 39596834057 verde. Il primo
tentativo falli' il check, non gli si attribuiscono test/build riusciti.
Cronologia estesa nelle versioni precedenti e nella storia Git.

Pagina con snapshot gara/campionato/piloti e coda condivisa, eventi anche per is_last,
fallback solo senza open. Merge risultati 3c860d2: ordine/assenti coerenti e sponsor
locali conservati; ufficiali/permessi aggiornati. PUT esplicita con copia preinvio,
controlli piloti/duplicati/ID e massimo 12, normalizzazione sponsor preesistente.
Uscita protetta, risposte vecchie ignorate, HTTP inviate non annullate. Nessun lock
ottimistico o nuova atomicita' backend. Pannello usa onchanged, non reload browser.

Store/pannello live 1145a9a, CI 39650297363 verde: GET-only al mount, merge inventari,
revoca spunte, blocchi, copie e recupero confermato; guardie 01c567a mantenute.
Lifecycle ora corretto in 8018d18, CI 39658083388 verde su frontend, backend e
migrazioni test. La key non include piu' race.status. Il pannello gia' mostrato
resta nello stesso contesto gara/utente se il ruolo e' ancora ammesso; enabled=false
lo rende non modificabile senza eliminare la copia. Nuovo contesto o perdita ruolo
possono smontarlo. Riabilitare editing richiede nuova lettura e ricontrollo piloti.

Canvas corretto nello stesso commit: controllo nativo, tastiera/pointer e ruolo
non consentito rimosso. Diff letto; nessuna modifica fuori dai cinque frontend e
nota. Non si dichiarano DOM, dialoghi, focus o cambi fase collaudati dalla sola CI.

Collegamenti automatici pronti per la verifica browser su dati isolati: seguire
PHASE_15_BROWSER_CHECKLIST.md e registrare i casi realmente eseguiti. Nessun test
browser o comando npm locale dell'assistente. Solo .md in questo riallineamento,
nessun codice, workflow, API, schema, lockfile o dato modificato. Documenti protetti
intatti. Nessuna attesa CI dei soli .md, nessun merge o accesso al DB reale autorizzato.
