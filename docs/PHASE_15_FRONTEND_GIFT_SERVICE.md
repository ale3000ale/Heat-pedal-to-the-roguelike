# Fase 15a-4b - Servizio frontend delle notifiche, preparazione commit 2

Data: 2026-10-20. Solo ramo phase-15-sse-sistemazione, PR 14 in bozza.
Base: 9ea0cb0, CI 39479071828 interamente verde. Backend selettivo cda06a9.
Servizio verificato sulla testa formattata de29e70, CI 39497343267 tutta verde.
Questo sottoinsieme prepara il collegamento; nessuna schermata ancora modificata.

## File e motivazione

- frontend/src/lib/gift-notifications-api.ts: servizio dedicato.
- frontend/src/lib/gift-notifications-api.spec.ts: test con fetch simulato.
- Questa nota: perimetro, limiti e verifiche effettive.

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

Test inclusi nella suite frontend passata in CI: associazione pilota/DTO,
deduplicazione, snapshot completo, propagazione errori e 401, lista vuota,
validazione preventiva degli ID, corpo/endpoint/cookie, batch 100/100/1 e
interruzione dopo errore parziale. Non vengono dichiarati conteggi dei test.
Nessun npm, lint, type-check, test o build eseguito localmente dall'assistente.

Nessuna modifica a dipendenze, lockfile, immagini, dati o migrazioni.
Il primo blocco del servizio non modificava workflow. La correzione descritta
sotto ha aggiornato soltanto il workflow formatter esistente e questa nota;
il successivo commit del bot modifica il solo file di test segnalato.
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

La correzione ae161cc7c94129ff8e146fafb2c8bc25d4b583e4 aggiorna il workflow
.github/workflows/format-sse-client.yml: entrambi gli elenchi, per Prettier e
git add, includono soltanto gift-notifications-api.spec.ts. Il workflow usa
npm ci e Prettier dal lockfile, senza cambiarne la configurazione. Dopo --write
e --check esegue lint completo, check, test e build sulla copia formattata.
Solo se tutti riescono pubblica il singolo file sul ramo fase 15. Se il ramo
cambia durante i controlli, si ferma senza force push. Trigger e perimetro del
repository restano invariati; main e phase-14 non sono coinvolti.

## Testa formattata e CI verde verificata

Commit pubblicato da github-actions[bot]:
de29e7000aa5ad9bc6c313817178622b9844f903, alle 23:04:11 CEST del 2026-10-20.
Messaggio: style: formatta test notifiche con Prettier del lockfile.
Letti dettagli e diff: modifica esclusivamente gift-notifications-api.spec.ts,
con riadattamenti delle righe, senza cambiamenti alla logica dei test.
Il servizio gift-notifications-api.ts resta invariato.

CI ordinaria verificata sulla nuova testa della PR 14: run 39497343267.
https://github.com/ale3000ale/Heat-pedal-to-the-roguelike/actions/runs/39497343267

| Job | Esito | Conclusione CEST del 2026-10-20 |
|---|---|---|
| Migrazioni (database di test) | success | 23:05:19 |
| Frontend (check, lint, test, build) | success | 23:05:42 |
| Backend (pytest) | success | 23:06:47 |

Errore Prettier risolto e tutti i job della nuova testa completati con successo.
Verificati commit bot, diff ed esiti dei job ordinari; non log completi del job
formatter o conteggi numerici. Non si e' presunto che il push del bot avviasse
altri workflow: sono stati letti i check effettivamente presenti.
Questo risultato non certifica le schermate non ancora collegate, il rendering
dei popup, il database reale o una prova browser. Nessuna nuova prova manuale
richiesta e nessun comando locale eseguito dall'assistente.

## Seguito e riallineamento

Questo riallineamento modifica soltanto questa nota e PHASE_15.md, registrando
la disponibilita' del servizio verificato e i limiti ancora presenti.
Il nuovo commit documentale richiede una verifica CI separata. PROJECT_SPEC.md
e PROJECT_STATUS.md restano protetti. Database, comandi di setup e requisiti
non cambiano; nessuna nuova modifica a codice, workflow o dati in questo push.

Passo successivo: usare il servizio nel lifecycle delle pagine, riconciliare i
regali anche con popup aperto e separare la chiusura volontaria dall'annullo
remoto, che non deve invocare una conferma automatica. Completare il merge dei
risultati non modificati e il fallback solo senza stream open.
Avviso e checklist dei test manuali finali soltanto dopo il collegamento e la
relativa CI verde, come richiesto dall'autore. Nessun merge autorizzato.
