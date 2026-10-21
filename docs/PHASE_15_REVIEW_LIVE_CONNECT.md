# Collegamento inventari live verificato

Aggiornamento: 2026-10-21. Solo phase-15-sse-sistemazione, PR 14 in bozza.
Collegamento 1145a9a, CI 39650297363 verde; lifecycle/canvas successivo 8018d18,
CI 39658083388 verde su frontend, backend e migrazioni sintetiche. Diff ultimo blocco
letto e conforme al perimetro. Nessun merge autorizzato.

Tentativo 23b6bda/39646853375 fallito su sette errori ESLint, non su test/build.
Fix dbe8204: autoOpen come GET, chiavi each, SvelteSet, senza disattivare regole.
I vecchi job rossi restano storia dei rispettivi commit, non esito della testa nuova.
Workflow di applicazione vincolano blob/commit: non rieseguirli sul codice gia'
modificato aspettandosi un aggiornamento, interrompono su basi diverse.

Mount GET-only, un client SSE condiviso, fallback solo senza open con intervallo
admin. Stato, inventario/bozza propri e stato finale letti senza effetti UI in load;
403/409 verificano il contesto. Apply scarta letture obsolete/durante scritture;
nuova lettura dopo azioni esplicite. Base distinta, conteggi locali preservati e
metadati remoti applicati, revoca spunte e blocchi senza clamp. Titolare/inizio nuovi
non trasferiscono lavoro. Nessuna PUT di conteggi agli eventi o nuova atomicita'.

Recupero/apertura sostitutiva con dialogo e backup riuscito, copie distinte mai
eliminate. Progresso legacy revoca spunte, non applicabile resta testo. Recupero
confermato puo' ignorare un contenuto server incompatibile esatto nella stessa
chiave, un altro riblocca. 401/auth.expired fermano contesto senza svuotare un nuovo
utente. HTTP gia' partite non cancellate. Countdown non si riarma su scadenze passate.

Lifecycle 8018d18 evita smontaggio per il solo stato: resta copia nel medesimo
contesto/utente se il ruolo e' ancora ammesso, con enabled=false in sola lettura.
Nuovo contesto/perdita ruolo possono nasconderla. Riabilitare richiede lettura nuova.
Canvas ora senza ruolo img non consentito, con controllo nativo e tastiera.

Sette test live simulati e suite precedenti conservati; tre test sul limite genitore
aggiunti nel blocco successivo. Nessun totale suite o risultato browser inventato.
Ora seguire PHASE_15_BROWSER_CHECKLIST.md su ambiente isolato: dialoghi, cambi fase,
permessi, connessioni e interazioni non sono certificati dalla compilazione.

Nessun npm locale dell'assistente. Vulnerabilita' npm segnalate ancora pendenti,
nessun audit fix/force. Backend/API/DB, lockfile e documenti protetti intatti.
Questo riallineamento modifica solo .md, senza attendere relativa CI. SSE in
collaudo browser, non dichiarato concluso. Nessun merge o dato reale modificato.
