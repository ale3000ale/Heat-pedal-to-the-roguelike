# Fase 15a-4b - Riconciliazione dei risultati gara

Aggiornamento: 2026-10-21. Solo phase-15-sse-sistemazione, PR 14 in bozza.
Funzione pura e test verificati sulla testa formattata 3c860d2, CI 39509635060 verde.
Non ancora importata nella pagina gara. Nessun merge o intervento sul database.

## Decisione e implementazione

Confermata nel seguito della proposta delle 00:27: ordine/assenti come unica
assegnazione coerente; sponsor riconciliati per pilota. Se l'assegnazione locale
cambia, non si importa separatamente una lista remota che potrebbe duplicare
piloti. Se il remoto rimuove dalla classifica un pilota con sponsor modificati,
si conserva l'assegnazione locale e si segnala il conflitto.

race-result-reconcile.ts espone ResultForm, hasResultChanges e reconcileResults.
Merge a tre vie: base autorevole, modulo locale e nuovo modulo remoto nello
stesso contesto. Nomi non considerati campi editabili. Sponsor undefined conserva
un input numerico svuotato, senza convertirlo prematuramente in zero. Restituisce
nuove liste/righe, conflitto, assegnazione preservata e modifiche residue.
Assegnazioni duplicate negli input generano RangeError, non una correzione silenziosa.
Nessuna rete, timer, dipendenza Svelte, scrittura o validazione dei permessi.
Il merge frontend non introduce una garanzia di concorrenza lato server.

## Primo tentativo e correzione mirata

Commit implementativo: cebccebfbda69f8d9a1c24623f0c29fcfeefe905.
CI della PR 14: run 39509013765. Esiti dei job letti tramite GitHub.
https://github.com/ale3000ale/Heat-pedal-to-the-roguelike/actions/runs/39509013765

| Job | Esito | Conclusione CEST del 2026-10-21 |
|---|---|---|
| Frontend (check, lint, test, build) | failure | 00:34:08 |
| Migrazioni (database di test) | success | 00:34:10 |
| Backend (pytest) | success | 00:36:10 |

Log dell'autore alle 00:36: prettier --check sul solo race-result-reconcile.ts.
Lint usa prettier --check . && eslint .: ESLint non parte dopo Prettier fallito.
Non si dichiarano test/build frontend superati nel primo job fallito.

Correzione 823572fcd165b67a76250460098edc430969ca5e: workflow formatter e nota.
Entrambi gli elenchi per Prettier e git add limitati a race-result-reconcile.ts.
Runner con npm ci e Prettier dal lockfile, senza versioni/configurazioni nuove.
Lint completo, check, test e build prima di un eventuale commit automatico;
se il ramo cambia si ferma senza force push. Trigger solo sul ramo fase 15 e sul
workflow stesso nel repository previsto. Nessuna modifica manuale alla logica.

## Testa formattata e verifiche effettive

Il bot ha pubblicato 3c860d2f9c576146a1867ca0da65634d0dc1d138 alle 00:38:52 CEST.
Letto il diff: solo race-result-reconcile.ts, espressione conflict su una riga
invece di due. Nessun cambiamento logico o modifica alla suite nel commit bot.

CI ordinaria sulla nuova testa della PR 14: 39509635060, tutti i job success.
https://github.com/ale3000ale/Heat-pedal-to-the-roguelike/actions/runs/39509635060

| Job | Esito | Conclusione CEST del 2026-10-21 |
|---|---|---|
| Migrazioni (database di test) | success | 00:40:00 |
| Frontend (check, lint, test, build) | success | 00:40:28 |
| Backend (pytest) | success | 00:41:44 |

Errore Prettier risolto sulla testa formattata, non dichiarato risolto sulla
prima CI fallita. Verificati commit bot, diff ed esiti dei job ordinari, non log
completi del formatter o conteggi numerici dei test. Nessun comando locale.

La suite passata comprende adozione remota e immutabilita', sponsor per pilota
con riordino, assegnazione accoppiata, modifica della sola lista assenti, sponsor
protetto quando il remoto sposta il pilota, input vuoto e conflitto sponsor,
convergenza, base della PUT e duplicati. Sono prove della funzione pura, non
DOM, browser, permessi o integrazione della pagina. Il verde non certifica ancora
bozza in sola lettura, protezione uscita, SSE gara o sostituzione del reload.

## Seguito e metodo

Questo push riallinea solo questa nota e PHASE_15.md. Per richiesta dell'autore
alle 00:26, commit esclusivamente .md non bloccano il seguito in attesa dei test.
Nessun nuovo esito CI viene presunto per il commit documentale. Codice e workflow
continuano invece a richiedere i controlli pertinenti prima della conclusione.
PROJECT_SPEC.md e PROJECT_STATUS.md protetti. Nessuna nuova modifica a codice,
workflow, dipendenze, lockfile, API, migrazioni, immagini o dati in questo push.

Prossimo blocco: collegare pagina gara e pannello alla coda SSE; conservare base
server separata dal modulo e usare la bozza inviata per il merge della risposta
PUT, senza perdere modifiche fatte durante la richiesta. Sostituire il reload
completo del pannello con rilettura coordinata; mostrare conflitti senza salvataggi
automatici, proteggere uscita con modifiche pendenti e mantenere una copia in sola
lettura quando lo stato remoto toglie il permesso di modifica. Validare payload,
ID e permessi autorevoli prima di salvare. Nessun ulteriore prerequisito backend.
Nessuna prova browser richiesta ora: avviso e checklist manuale finale soltanto
dopo completamento dei collegamenti e relativa CI verde. Nessun merge autorizzato.
