# Chiusura autorizzata fase 15

Data: 2026-10-22. Solo ramo phase-15-sse-sistemazione.
Riallineamento generale: preparato, pubblicazione automatica ancora da verificare.

## Decisione dell'autore

Alle 00:47 CEST: "passa direttamente alla 2 che in 1 alcune cose non si possono
provare per motivi pratici ma ci sono. cosí chiudiamo la fase 15".
Autorizzato il riallineamento di PROJECT_STATUS.md e PROJECT_SPEC.md e accettati
come non bloccanti per la chiusura i limiti del collaudo. Stato prodotto: fase 15
completata e chiusa sul ramo, non automaticamente unita a main o pronta produzione.

## Evidenze mantenute

Codice finale 12261725bc3439cd3e593fda152e050563b0988f, CI 39674942800 verde su
frontend, backend e migrazioni di test. Lifecycle/canvas 8018d18, CI 39658083388.
Autore: PASS 1/4/5/6/7/9, 2/3 non verificabili, 8/10 non eseguiti; conferma del
fix iscrizioni alle 23:24 del 2026-10-21. Gli ultimi quattro casi restano non
verificati, non sono promossi a PASS. Nessuna nuova esecuzione locale o browser
dell'assistente e nessun totale test inventato. Non si riaprono quei casi come
condizione obbligatoria per questa chiusura accettata.

## Patch documentale

File: PROJECT_STATUS.md, PROJECT_SPEC.md, PROJECT_NOTES.md, PHASE_15.md e
PHASE_15_BROWSER_CHECKLIST.md, tutti in docs/, piu' questa nota. Workflow verifica
i cinque blob, modifica intestazioni e sezioni mirate, conserva integralmente il
resto dei due documenti generali lunghi e aggiunge la specifica consolidata SSE.
Le sezioni storiche restano riconoscibili, non vengono riscritte da risposte
troncate del connettore. Data e titoli verificati, git diff --check e perimetro
applicativo intatto prima del commit bot. Arresto se basi o testa ramo cambiano,
nessun force push. La nota fase 14 post-merge conferma PR 13 unita il 2026-10-19;
si corregge la vecchia riga 14 ancora "da definire". Nessuna nuova regola di gioco.

Il commit preparatorio aggiunge solo workflow e nota; dopo il bot verificare il
riallineamento effettivo. Non esegue npm/pytest, app, setup, migrazioni o comandi
sul DB: il codice resta quello gia' verificato. Non attribuire nuove esecuzioni
applicative a questo aggiornamento; la CI ordinaria e' separata. I soli .md non
bloccano il seguito in attesa CI. Non rieseguire la patch su documenti gia' aggiornati.

## Esclusioni

Nessun cambiamento a codice, frontend/backend, schema, dati, immagini, dipendenze,
lockfile, regole del Negozio o formato Deck.cards. Nessun backup o migrazione reale.
Vulnerabilita' npm, backup/setup sicuro, cookie secure e percorso SQLite per online
restano attivita' distinte. Discrepanze di formato gia' documentate non risolte qui.
PR 14, descrizione/stato bozza e merge sono il successivo punto separato, non
modificati da questo incarico. Nessuna produzione, fase 15b o altra fase avviata.
