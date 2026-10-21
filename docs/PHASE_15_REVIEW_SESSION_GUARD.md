# Guardie sessione e limite del genitore

Aggiornamento: 2026-10-21. Solo phase-15-sse-sistemazione.
Guardie 37e635c/01c567a, CI 39636047244 verde. Integrazione 1145a9a, CI 39650297363;
limite del genitore 8018d18, CI 39658083388, entrambe verdi. Cronologia in Git.

Utente iniziale e chiave revisione caricata vincolano le scritture. Verifica prima
dei conteggi e fra PUT bozza e DELETE rinuncia; progresso browser sotto la chiave
propria. Nessuna atomicita' fra verifica e richiesta successiva. Sei test iniziali
coprono salvataggio valido, titolare/inizio cambiati, cambio fra PUT/DELETE, cambio
utente e dispose durante verifica. I sette casi live sono descritti nella nota live.

Ora enabled del genitore limita anche lo store: false preserva copia, revoca spunte
e blocca azioni; true impone nuova lettura. Apertura e recupero confermati non
aggirano il limite. Tre test aggiunti coprono blocco/preservazione, cambio durante
preinvio e riabilitazione. Il limite non concede diritti backend e non annulla HTTP
in corso. Il pannello resta sul solo cambio stato se il ruolo e' ancora ammesso;
cambio contesto o perdita ruolo possono smontarlo senza trasferire copie.

Diff del blocco 8018d18 ed esiti CI letti. Nessun nuovo test DOM/browser e nessun
npm locale dell'assistente. Per il collaudo seguire PHASE_15_BROWSER_CHECKLIST.md,
solo dati isolati. Non certificare guardie UI o SSE complessivi dalla sola CI.
Solo documenti in questo riallineamento; backend, DB, dipendenze e documenti protetti
intatti. Nessun merge e nessuna attesa CI dei soli .md.
