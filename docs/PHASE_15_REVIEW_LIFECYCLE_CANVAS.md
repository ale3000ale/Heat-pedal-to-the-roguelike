# Lifecycle revisione e canvas - verificati

Aggiornamento: 2026-10-21. Solo phase-15-sse-sistemazione; nessun merge.
Preparazioni 9a0ef20/5908cc6/fa0450e, bot
8018d189dcef770a76093c59489566cdeccd4dc6 alle 21:02:09 CEST del 2026-10-21.

## Esito verificato

CI ordinaria 39658083388 della nuova testa tutta verde:
- Migrazioni database di test: 21:09:09 CEST.
- Frontend check/lint/test/build: 21:09:40 CEST.
- Backend pytest: 21:10:33 CEST.

Letto il diff: pagina gara, pannello, store, canvas, test guardie e stato nota,
nessun altro file nel commit bot. Prima della pubblicazione il workflow ha richiesto
formatter, lint, check senza diagnostica del canvas, test e build. Nessun comando
npm locale eseguito dall'assistente; non si dichiarano log completi letti.

9a0ef20/39654061238 si fermo' sull'ancora non univoca !this.disposed &&; 5908cc6
la limita al getter active senza cambiare refreshStatus. Tentativo 39655437138:
log autore delle 20:56, lint riuscito, check 0 errori/1 warning per role img sul
canvas; guardia bloccante, test/build non eseguiti. fa0450e rimuove il solo ruolo
riapplicando la patch immutabile 5908cc6, mantenendo guardie e perimetro.

## Comportamento applicato

Il pannello gia' mostrato resta nello stesso contesto gara/utente senza race.status
nella key; flag azzerato al cambio contesto. Resta subordinato al ruolo di gestione.
enabled=canReview limita editing e canOpen, inoltrato con untrack allo store.
False revoca spunte e congela azioni senza sostituire copie; true richiede lettura
nuova. Verifica preinvio, apertura e recupero rispettano il limite, senza concedere
permessi backend o annullare HTTP gia' partite. Tre test store simulati verificati.

Canvas senza ruolo esplicito non consentito, aria-label mantenuto; gestori sul
button nativo con nome/focus. Trascinamento usa panView e larghezza canvas,
frecce spostano, Maiusc usa passo fine, Invio/Spazio esportano. Zoom e WebP invariati.
Warning mirato corretto nel codice verificato, non una certificazione di accessibilita'.

## Collaudo browser

Avviso: completate le correzioni automatiche previste, ora eseguire i casi di
PHASE_15_BROWSER_CHECKLIST.md esclusivamente su dati isolati. Non sono stati eseguiti
nuovi test DOM/browser dall'assistente. Restano da confermare cambi fase, contesto,
permessi, dialoghi, tastiera, mouse/touch e uscite durante richieste. Nessuna nuova
funzionalita' richiesta prima di raccogliere questi esiti.

Questo riallineamento e' solo documentale: codice, workflow, backend/API/SQLite,
lockfile e documenti protetti intatti. Vulnerabilita' npm segnalate non risolte;
nessun audit fix/force. Non attendere CI dei soli .md e non rieseguire vecchie patch
sulla base gia' modificata. Nessun merge o intervento sui dati reali autorizzato.
