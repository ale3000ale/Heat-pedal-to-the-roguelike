# Fase 15a-4b - Servizio frontend delle notifiche, preparazione commit 2

Data: 2026-10-20. Solo ramo phase-15-sse-sistemazione, PR 14 in bozza.
Base: 9ea0cb0, CI 39479071828 interamente verde. Backend selettivo cda06a9.
Questo sottoinsieme prepara il collegamento; nessuna schermata ancora modificata.

## File e motivazione

- frontend/src/lib/gift-notifications-api.ts: servizio dedicato.
- frontend/src/lib/gift-notifications-api.spec.ts: test con fetch simulato.
- Questa nota: perimetro, limiti e verifiche da completare.

Il DTO CardGift non contiene pilot_id. Il servizio conserva l'associazione con
il pilota della richiesta REST tramite PilotGiftNotification {pilotId, gift},
senza cambiare backend, DTO, database o formato delle carte.
fetchGiftNotifications legge tutti i piloti indicati, deduplicandoli. Se una
lettura fallisce, rifiuta l'intero snapshot, propagando anche il 401: nessuna
lista vuota fittizia deve cancellare popup o regali validi durante la riconciliazione.

acknowledgeGiftNotifications riceve soltanto lo snapshot gia' mostrato che il
chiamante deve conservare. Raggruppa gli ID per pilota e li deduplica, poi invia
batch sequenziali da massimo 100 a /card-gifts/seen-selected. Non usa /seen
legacy, non rilegge la coda e non modifica lo snapshot o la UI. Con lista vuota
non invia richieste. Tutti gli ID sono validati prima della prima richiesta.

Il contratto backend ammette int64 SQLite, ma il client TypeScript usa number:
si accettano solo interi positivi rappresentabili esattamente da JavaScript.
Si rifiutano ID non sicuri invece di rischiare la conferma di un ID arrotondato.
Non viene introdotta una conversione bigint o una modifica del contratto JSON.

Un errore interrompe i batch successivi, ma quelli gia' riusciti possono essere
persistiti. Non si dichiara atomicita' tra richieste: un tentativo successivo con
lo stesso snapshot e' compatibile con l'idempotenza del backend. Non si avviano
retry automatici. Le richieste di lettura gia' partite non vengono cancellate.

## Verifiche e limiti

Test preparati: associazione pilota/DTO, deduplicazione, snapshot completo,
propagazione errori e 401, lista vuota, validazione preventiva degli ID,
corpo/endpoint/cookie, batch 100/100/1 e interruzione dopo errore parziale.
Nessun npm, lint, type-check, test o build eseguito localmente dall'assistente.
Questi test non sono ancora dichiarati superati: leggere la CI del nuovo commit
ed eventualmente correggere gli errori prima di collegare le schermate.
Il verde della base non certifica i nuovi file.

Nessuna modifica a dipendenze, lockfile, workflow, immagini, dati o migrazioni.
card-poll.svelte.ts e le pagine restano invariati: il nuovo servizio non e'
ancora importato dalle schermate. Il vecchio wrapper continua quindi ad avere
il comportamento precedente fino al collegamento, non dichiarato risolto qui.

## Seguito

Dopo la CI riallineare le note di fase interessate, senza toccare PROJECT_SPEC.md
e PROJECT_STATUS.md protetti. Poi usare il servizio nel lifecycle delle pagine,
riconciliare i regali anche con popup aperto e separare la chiusura volontaria
dall'annullo remoto, che non deve invocare una conferma automatica.
Completare il merge dei risultati non modificati e il fallback solo senza stream
open. Avviso e checklist dei test manuali finali soltanto dopo il collegamento
e la relativa CI verde. Nessun merge autorizzato.
