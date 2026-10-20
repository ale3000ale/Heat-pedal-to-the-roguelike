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
Il verde della base non certifica i nuovi file. Esiti del primo tentativo sotto:
nessun successo dei nuovi test frontend dichiarato prima della CI corretta.

Nessuna modifica a dipendenze, lockfile, immagini, dati o migrazioni.
Il primo blocco del servizio non modificava workflow. La correzione descritta
sotto aggiorna soltanto il workflow formatter esistente e questa nota.
card-poll.svelte.ts e le pagine restano invariati: il nuovo servizio non e'
ancora importato dalle schermate. Il vecchio wrapper continua quindi ad avere
il comportamento precedente fino al collegamento, non dichiarato risolto qui.

## Primo tentativo e correzione di formattazione

Commit implementativo: 493a3fbde86573ae7373a081e2195972dc7d486d.
CI ordinaria della PR 14: run 39491830284.
https://github.com/ale3000ale/Heat-pedal-to-the-roguelike/actions/runs/39491830284

| Job | Esito | Conclusione CEST del 2026-10-20 |
|---|---|---|
| Migrazioni (database di test) | success | 22:25:51 |
| Frontend (check, lint, test, build) | failure | 22:25:56 |
| Backend (pytest) | success | 22:27:25 |

Esiti dei job letti tramite GitHub. Il log fornito dall'autore alle 22:43 CEST
segnala Prettier su src/lib/gift-notifications-api.spec.ts. npm run lint usa
prettier --check . && eslint .: ESLint non parte dopo il fallimento Prettier.
Non si dichiarano superati test e build del job fallito ne' conteggi numerici.

La correzione aggiorna .github/workflows/format-sse-client.yml: entrambi gli
elenchi, per Prettier e git add, includono soltanto gift-notifications-api.spec.ts.
Il workflow usa npm ci e Prettier dal lockfile, senza cambiarne la configurazione.
Dopo --write e --check esegue lint completo, check, test e build sulla copia
formattata. Solo se tutti riescono pubblica il singolo file sul ramo fase 15.
Se il ramo cambia durante i controlli, si ferma senza force push. Trigger e
perimetro del repository restano invariati; main e phase-14 non sono coinvolti.

Nessuna modifica logica prevista ai test o al servizio. Il formatter non e'
ancora dichiarato eseguito o riuscito: dopo il push controllare il job, il commit
bot effettivamente pubblicato e la CI sulla nuova testa. Non presumere che il
push del bot avvii automaticamente altri workflow; leggere i check disponibili.
Nessun comando locale eseguito dall'assistente. Nessuna prova browser richiesta.

## Seguito

Dopo la CI riallineare tutte le note di fase interessate, senza toccare
PROJECT_SPEC.md e PROJECT_STATUS.md protetti. Poi usare il servizio nel lifecycle
delle pagine, riconciliare i regali anche con popup aperto e separare la chiusura
volontaria dall'annullo remoto, che non deve invocare una conferma automatica.
Completare il merge dei risultati non modificati e il fallback solo senza stream
open. Avviso e checklist dei test manuali finali soltanto dopo il collegamento
e la relativa CI verde. Nessun merge autorizzato.
