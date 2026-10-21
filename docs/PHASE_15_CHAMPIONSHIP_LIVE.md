# Pagina campionato e iscrizioni live

Aggiornamento: 2026-10-21. Solo phase-15-sse-sistemazione, PR 14 in bozza.
Collegamento df7edf5/dc97fcf, CI 39502927035 verde. Cronologia estesa in Git e nella
versione precedente della nota. Nessun merge autorizzato.

## Collegamento corrente

championship-live.ts legge campionato/classifica/gare/piloti propri e notifiche
solo dei propri iscritti. Snapshot completo o errore, mai [] fittizio; piu' REST,
non singola transazione SQL. Campionato chiuso senza popup, API storica conservata.
Coda SSE condivisa e fallback con intervallo admin soltanto senza open, nessun
secondo stream o polling di sicurezza. Apply aggiorna pagina, popup e sezioni sponsor.
Ack solo /seen-selected sugli ID resi alla chiusura volontaria; annulli o chiusure
remote non scrivono. Dopo ack nuova lettura; limiti batch parziali e HTTP in corso
conservati. Nessun retry automatico delle scritture.

Contesto legato a campionato/utente, cleanup per avvii tardivi e risposte vecchie.
401 ferma il modulo prima di auth; errori conservano dati e popup. Reload delle
azioni locali passa dalla stessa coda. I CRUD senza eventi non diventano per questo
immediati tra utenti; non si dichiara tutta l'applicazione real-time.

## Iscrizioni remote corrette

L'iscrizione prima aggiornava solo la sessione che eseguiva POST. Dal bot 1226172,
CI 39674942800 tutta verde, championship.pilots_changed viene registrato con
iscrizione/reset. Solo ID campionato, pilot_id nullo e payload vuoto: nessun nome,
carta o conteggio. Il segnale canonico e' visibile a tutti gli autenticati, anche
non iscritti, coerentemente col dettaglio REST. Altri eventi e dati privati mantengono
i filtri precedenti. Non e' un'estensione generale della visibilita' SSE.

Registro tipi e validatore frontend riconoscono il segnale; il coordinatore gia'
presente rilegge campionato/classifica/gare e soli dati propri autorizzati, senza
nuovi polling, stream, POST o ack in risposta all'evento. Test backend su consegna,
privacy, rollback e rifiuti; parser e aggiornamento snapshot testati nel frontend.
Nessuna modifica a pagina, endpoint, modello SQL o dipendenze per questo fix.

## Riscontri e seguito

Autore 22:39: casi 1/4/5/6/7/9 PASS, 2/3 non verificabili, 8/10 non eseguiti.
Autore 22:41: difetto iscrizioni per membri e osservatori autenticati; 23:24:
"funziona" dopo richiesta di riprova del fix. Conferma complessiva, non log separati
dei due scenari. Browser/commit locale non registrati; nessuna riproduzione manuale
dell'assistente. Dettagli in PHASE_15_ENROLLMENT_LIVE.md e checklist aggiornata.

Proxy/buffering, carico e i casi non eseguiti restano non verificati. Nessun altro
fix in questo riallineamento solo documentale. Non attendere CI dei soli .md.
Documenti protetti, codice, workflow, schema e dati intatti; nessun merge o intervento
sul database reale autorizzato.
