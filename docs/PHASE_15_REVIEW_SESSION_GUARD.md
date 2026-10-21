# Guardie sessione conteggi revisione

Stato: patch applicata; formatter, lint, type-check, test e build frontend riusciti nel workflow che pubblica questo commit.

Blocco ridotto sul ramo phase-15-sse-sistemazione. Il workflow richiede il blob
store originale 326adebf9c500af51e1c5e613b6d0d2798e621b6, verifica ogni sostituzione
e si ferma se la base differisce. Modifica soltanto lo store esistente, formatta
store e test, esegue npm ci, lint, check, test e build. Solo dopo successo aggiorna
questa nota e pubblica quei tre file; nessun force push se il ramo e' cambiato.

La patch lega lo store all'utente iniziale e alla chiave della revisione caricata,
ricontrolla lo stato dopo il caricamento e prima delle scritture dei conteggi,
compreso il passaggio fra salvataggio e rinuncia. Progresso browser mantenuto
sotto la chiave iniziale. Nessun nuovo salvataggio automatico. La verifica e la
scrittura restano due richieste distinte, non una transazione backend.

Sei test mirati: salvataggio consentito, titolare cambiato, nuovo inizio dello
stesso revisore, cambio fra PUT e DELETE, cambio utente, dispose durante verifica.
Test con API simulate, non collaudo browser. Nessun comando npm eseguito localmente
dall'assistente. Verificare esito workflow e commit bot prima di dichiarare successo.

Non completa SSE, merge inventari o recupero confermato nel pannello: restano
pendenti. Non cambia pannello, API, database, dipendenze o lockfile. Dopo verifica
riallineare i documenti interessati senza dichiarare SSE concluso. Nessun merge.
