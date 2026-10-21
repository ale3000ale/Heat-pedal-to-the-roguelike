# Fase 15a-4b - Merge inventari e integrazione

Aggiornamento: 2026-10-21. Solo phase-15-sse-sistemazione, PR 14 in bozza.
Modulo puro 05b2829, bot 6aa7fe6, CI 39599465230 verde. Cronologia estesa nelle
versioni fcead0f/a36e536 e Git. Guardie 01c567a, CI 39636047244 verde.

## Politica e funzioni

ownReviewKey identifica gara/revisore/inizio della revisione propria attiva, senza
sostituire autorizzazione o scadenza server. reconcileReviewInventory confronta
base server, locale e remoto con bozza applicata. Remaining locali modificati
preservati con metadati nuovi; changedPilotIds ignora riordino/solo nome pilota,
conflictingPilotIds segnala conteggi concorrenti validi. Carte/piloti rimossi
con modifiche o quantita' oltre il nuovo totale producono issues/blocked e copia
locale intera. Nessun clamp. Duplicati/fonti server invalide generano RangeError,
non []. Copie indipendenti e nessuna REST nel modulo puro.

## Collegamento verificato

Dal commit 1145a9a lo store usa anche il merge, non solo ownReviewKey. Pannello
collegato alla coda live condivisa, fallback solo senza open, caricamento GET
senza apertura automatica. Bozza richiesta solo allo stato proprio attivo,
chiave verificata anche dopo letture. Snapshot vecchi o durante scritture scartati.
Spunte interessate revocate, incompatibilita' preservate e editing/conferma bloccati.
Cambio titolare/inizio non trasferisce conteggi. Recupero che abbandona modifiche
richiede dialogo e backup browser riuscito; se storage fallisce si interrompe.
Conferme/salvataggi REST soltanto azioni esplicite, mai agli eventi.

Inventario leggibile da giudice/admin senza titolarita', bozza solo titolare;
GET stato puo' elaborare scadenze. 403/409 verificano il contesto e non diventano
bozze vuote. Recupero confermato puo' ripartire dall'inventario ignorando una bozza
server incompatibile esatta nella stessa chiave; un contenuto nuovo riblocca.
Nessuna nuova concorrenza protetta o atomicita' backend fra verifica e scrittura.

CI ordinaria 39650297363 sulla nuova testa tutta verde: frontend check/lint/test/
build, backend pytest e migrazioni di test. Sette test simulati di integrazione
oltre a suite pura e guardie preesistenti. Dettagli in PHASE_15_REVIEW_LIVE_CONNECT.md.
Esiti e file modificati letti, non log completi o totale numerico della suite.

## Confini

Test simulati non collaudano DOM, dialoghi o cambio fase. Il genitore puo' smontare
il pannello; copia visibile fino a quel momento, progresso sotto la chiave propria.
Valutazione lifecycle e warning canvas pendenti prima del collaudo finale.
Nessun npm locale o riuscita browser dichiarata dall'assistente. Solo .md in questo
riallineamento, nessun codice, workflow, dipendenza, API o dato modificato.
Documenti protetti intatti. Non attendere CI dei soli .md. Nessun merge autorizzato.
