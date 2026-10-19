# Fase 14 - Esito delle verifiche e indice per l'accorpamento

Aggiornamento: 2026-10-19. Ramo: phase-14. Documento riepilogativo per l'accorpamento a cura dell'autore; non modifica PROJECT_SPEC.md o PROJECT_STATUS.md.

## Stato verificato

PR #13 aperta e in bozza, non unita a main. Testa osservata: da48921f100a0053881b76e0984093ea100d8568. Nessun merge autorizzato o eseguito in questo aggiornamento.

L'assistente ha letto su GitHub i tre check run completati con esito success del run 39215475748:

- Backend (pytest): completato il 2026-10-19 alle 07:26:56 UTC.
- Migrazioni (database di test): completato alle 07:25:42 UTC.
- Frontend (check, lint, test, build): completato alle 07:26:07 UTC.

Questi risultati riguardano la testa osservata prima di questo aggiornamento documentale. Non vengono attribuiti automaticamente a commit successivi. L'assistente non ha eseguito quei comandi in locale: ha verificato l'esito pubblicato da GitHub.

## Riscontro dell'autore

Il 2026-10-19 alle 09:28 CEST l'autore ha riferito «apposto ora va», dopo la correzione della formattazione. Alle 09:33 CEST ha aggiunto «mi sembra vada tutto bene». Si registra quindi una prova manuale complessivamente positiva, senza attribuire verifiche puntuali non riferite e senza considerarla copertura esaustiva dei casi limite.

## Modifiche da accorpare

- 14i: etichette condivise dello stato gara; in_progress diventa in corso, in_review e to_review diventano in revisione, closed diventa terminata. La creazione della gara successiva considera anche le revisioni non concluse.
- 14j backend: lettura inventari sponsor con conteggi rimaste/totali e bonus S; validazione degli input; piano per carta con saldo aggregato su tutti i piloti e controllo delle carte omesse; salvataggio atomico, bozza in caso di conflitto e scadenza selettiva.
- 14j frontend: inventari per pilota in pannelli a scomparsa, +/− entro i limiti, Indietro/Prossimo, spunte, recupero della bozza e popup delle incongruenze.
- Migrazione a2e6c0d4f8b3: race.review_draft TEXT nullable, derivata da b4d8f2a6c0e3. La CI ha verificato migrazioni sul database di test; non è una prova di backup o migrazione del database locale dell'autore.

## Indice delle note

- PHASE_14.md: sezioni 14a–14h e contesto iniziale della fase.
- PHASE_14_REVIEW_MIGRATION.md: base dati e schemi dei conteggi.
- PHASE_14_REVIEW_PLAN.md: saldo aggregato e verifiche pure.
- PHASE_14_REVIEW_COMMIT.md: applicazione transazionale.
- PHASE_14_REVIEW_API.md: API bozza e conferma con conteggi.
- PHASE_14_REVIEW_EXPIRY.md: chiusura selettiva alla scadenza.
- PHASE_14_REVIEW_FRONTEND.md: client frontend e primi problemi di formattazione.
- PHASE_14_REVIEW_UI.md: pannello collegato e limiti dell'interfaccia.
- PHASE_14_FORMATTING.md e PHASE_14_FORMATTING_AUTOMATION.md: cronologia dei tentativi e automazione Prettier.

Le note sono state scritte durante lo sviluppo: le frasi «non ancora collegato» e «CI da verificare» descrivono il loro momento storico. Per lo stato complessivo delle verifiche osservate prevale questo documento; per il pannello attuale si veda PHASE_14_REVIEW_UI.md. Non si dichiarano aggiornati tutti i documenti generali del repository.

## Limiti e decisioni ancora aperte

- SSE e sincronizzazione dello stato tra dispositivi restano rinviati. Dopo le transizioni manuali della revisione la pagina viene ricaricata.
- Le spunte sono conservate nella scheda tramite sessionStorage; non sono persistite nel database né imposte dalle API.
- Il massimo della pool segue il prototipo: può cambiare se il prototipo viene modificato; se manca il dato, il limite superiore non viene verificato. Non è stato introdotto uno snapshot immutabile dei massimi.
- La scadenza è elaborata alla successiva chiamata del servizio; non esiste un job pianificato. Viene usata l'ultima bozza inviata al server, non le modifiche rimaste soltanto nel browser.
- In chiusura parziale la bozza e le carte incongruenti rimangono per la verifica amministrativa; manca una schermata dedicata di audit.
- Le rotte e lo store legacy restano per compatibilità. La conferma legacy non usa il nuovo percorso con conteggi.
- Le verifiche manuali dettagliate su permessi, concorrenza, recupero tra schede, mobile e casi limite non sono state documentate dall'autore.

L'eventuale rimozione dell'automazione di formattazione, l'accorpamento dei documenti e il merge richiedono operazioni separate: non sono inclusi in questo aggiornamento.
