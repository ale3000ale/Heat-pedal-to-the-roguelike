# Draft - stato dell'integrazione e correzioni

<!-- draft-validation-current:start -->

## Draft - stato verificato del 26 ottobre 2026

Questa sezione prevale esclusivamente sulle precedenti note di stato e verifica del flusso draft. Regole, specifiche delle altre fasi e contenuti storici restano conservati.

Base funzionale: commit 8ba03aa1aa8a20f8c346b3e20b4f1352d9b2d74a, ramo draft, PR #18 ancora in bozza e senza merge in main. Correzione delle chiavi del flusso e della proprieta delle risorse UI, non una nuova modifica di regole o API.

Verifiche lette: frontend (check, lint, test, build), runtime, backend pytest e migrazioni su database di test tutti success. Run CI 40269135082 e runtime 40269135447. I due job documentali di fase 16 sono skipped, non falliti.

Collaudo manuale positivo riferito dall autore il 26 ottobre alle 05:31: ora funziona tutto senza errori. Il riscontro segue i reset di presenze, zoom e mazzi e la correzione lifecycle. Non e un test browser automatizzato o una certificazione di tutti i dispositivi.

Il collaudo negativo delle 05:09 e superato dal riscontro positivo delle 05:31 dopo la correzione lifecycle 8ba03aa1; le sezioni precedenti restano checkpoint storici.

Questo riallineamento non cambia codice applicativo, dipendenze, lockfile o dati e non esegue nuovi test dell applicazione. Nessun rilascio, ZIP finale o merge implicito. Interventi grafici successivi sospesi fino alla scelta dell autore.

[Evidenze, cronologia e limiti della validazione](DRAFT_VALIDATION.md).
<!-- draft-validation-current:end -->

26 ottobre 2026. Solo Heat-pedal-to-the-roguelike, ramo draft, PR 18.

## Collaudo negativo dell'autore e cambio di intervento

Alle 05:09 l'autore ha confermato che zoom e mazzi non sono risolti. Nuovo riscontro: escludere un pilota dalle presenze riporta alla scelta draft/partita gia disputata. I controlli automatici verdi precedenti non provavano continuita del modal o funzionamento browser. Tutti questi difetti restano aperti; le patch di focus, layout e scroll non sono considerate una soluzione verificata.

L'analisi ha riletto registro, host UI, flusso, coordinatore mazzi, coda, live, provider del layout, autenticazione e wrapper modal. Il registro gia riusa store per ID: non si assume che ogni GET crei uno store nuovo. La pista di lavoro e la perdita del lifecycle UI e la dismissione di risorse prese in prestito; il punto di innesco effettivo non e stato riprodotto in un browser dagli strumenti disponibili.

## Correzione di chiavi e proprieta delle risorse

In draft-host.svelte la chiave del flusso diventa generazione autenticata piu ID preparazione, non l'oggetto store. Il cambio account/generazione o preparazione continua a ricreare il flusso; una nuova versione dei DTO non entra nella chiave.

In draft-flow.svelte la chiave interna diventa draftId, non l'oggetto contesto. Il cleanup reattivo che chiamava owner.dispose sullo store principale viene rimosso. onDestroy dismette solo il contesto locale; l'effetto di riconciliazione conserva il contesto per stesso owner/ID e lo dismette se cambia davvero, manca lo snapshot o la sessione termina. La dismissione dello store principale resta al registro host, che gia gestisce rimozioni, perdita di autorizzazione, generazione e fine vita.

In draft-decks.svelte la vista non chiama piu dispose sul coordinatore ricevuto dal contesto. Il cleanup segue la sua funzione subscribe stabile e cancella solo la cattura scroll locale. La dismissione definitiva dei dettagli resta al contesto creato da createDraftFlowContext. Nessuna persistenza artificiale della scelta iniziale, nessuna modifica a turno, versione, comando o dati.

File: components/draft-host.svelte, components/draft-flow.svelte, components/draft-decks.svelte sotto frontend/src/lib e questo documento. Nessuna modifica a store, controller, registro, API, SSE, backend, database, immagini, dipendenze o workflow.

## Verifiche e limiti

Nessuna installazione, formattazione, esecuzione locale check/lint/test/build o nuova lettura/attesa CI per questo incremento. Non sono stati aggiunti o eseguiti test client del montaggio; le suite esistenti non sono dichiarate sufficienti a riprodurre questo difetto. Nessuna riuscita browser o risoluzione definitiva attestata.

Nella lettura precedente sul commit e6302a0d risultavano frontend e runtime superati, migrazioni superate e backend ancora in corso. Questo dato storico non attesta la correzione corrente e non contraddice il collaudo negativo dell'autore. Correzioni precedenti: 9ceedd5d drag; 20a29699 indicatore proprio; d5d21088 zoom nello store; d80f2675 focus; ca5c682d feedback; a19d4d8e viewport; 1f5075fe lint test focus; 01cc4e51 compensazione scroll; df2e91a9 narrowing; e6302a0d identita coordinatore.

## Prossima prova e integrazione

Dopo i controlli verdi dell'esatto commit, prima prova sentinella: entrare nelle presenze ed escludere un pilota senza tornare alla scelta iniziale. Poi zoom locale del giocatore di turno e di un osservatore durante preview condivise, infine spostamento carte senza reset di sezioni/scroll. Se il reset permane occorre osservare montaggi, dismissioni e identita durante gli eventi reali, non aggiungere altre correzioni di CSS alla cieca. Documenti generali da riallineare alla chiusura verificata del ciclo.

Controllo anticipato 15 carte rimosso in 0052c1d; vincoli READY/finale conservati. Nuova Gara usa registro del layout, host/SSE condivisi e recupero REST accodato; nessuna gara dedotta da READY o sparizione REST. Regole in docs/DRAFT_SPEC.md invariate. Nessun merge o ZIP finale.
