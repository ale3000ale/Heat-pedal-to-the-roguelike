# Fase 15a-4b - Riconciliazione dei risultati gara

Data: 2026-10-21. Solo phase-15-sse-sistemazione, PR 14 in bozza.
Prima parte del collegamento gara: funzione pura e test, non ancora importata
nella pagina. Nessun merge o intervento sul database autorizzato.

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

## Test e stato reale

Suite preparata in race-result-reconcile.spec.ts: adozione remota e immutabilita',
sponsor per pilota con riordino remoto, ordine/assenti accoppiati, modifica della
sola lista assenti, sponsor protetto quando il remoto sposta il pilota, input
vuoto e conflitto sponsor, convergenza, base della PUT e duplicati.
Nessun npm, lint, type-check, test o build locale eseguito. Nessun nuovo test
ancora dichiarato superato: leggere la CI corretta prima del collegamento.

## Primo tentativo e correzione mirata

Commit implementativo: cebccebfbda69f8d9a1c24623f0c29fcfeefe905.
CI della PR 14: run 39509013765. Esiti dei job letti tramite GitHub.
https://github.com/ale3000ale/Heat-pedal-to-the-roguelike/actions/runs/39509013765

| Job | Esito | Conclusione CEST del 2026-10-21 |
|---|---|---|
| Frontend (check, lint, test, build) | failure | 00:34:08 |
| Migrazioni (database di test) | success | 00:34:10 |
| Backend (pytest) | success | 00:36:10 |

Il log fornito dall'autore alle 00:36 identifica prettier --check sul solo
src/lib/race-result-reconcile.ts. npm run lint usa prettier --check . && eslint .:
ESLint non parte dopo il fallimento Prettier. Non si dichiarano test o build
frontend superati nel job fallito, ne' conteggi numerici dei test.

La correzione modifica solo il workflow format-sse-client.yml e questa nota.
Entrambi gli elenchi del workflow, per Prettier e git add, contengono soltanto
race-result-reconcile.ts. Il runner usa npm ci e Prettier dal lockfile esistente,
senza cambiare versioni o configurazioni. Dopo --write e --check esegue lint
completo, check, test e build prima di un eventuale commit automatico.
Se il ramo cambia durante i controlli si ferma senza force push. Trigger sul
solo ramo fase 15 e sul workflow stesso, repository invariato.

Il modulo non viene riformattato manualmente da questo push e non si modifica
la sua logica o la suite. Dopo il push verificare esito del formatter, eventuale
commit del bot, diff e CI sulla testa risultante. Nessun successo del formatter
o risoluzione definitiva dichiarato prima dei controlli reali. Nessun comando
locale eseguito. Se emergono errori ulteriori, correggerli prima del collegamento.

## Seguito

La pagina gara e il pannello di revisione restano invariati in questo push:
non si dichiara risolto window.location.reload o implementata la vista in sola
lettura delle bozze quando i permessi cambiano. Il seguito deve collegare questa
funzione alla coda SSE, conservare la base server separata dal modulo e usare la
bozza inviata come base per il merge della risposta PUT. Sostituire il reload
del pannello con rilettura coordinata, proteggere uscita con modifiche pendenti
e mostrare conflitti senza salvare automaticamente. Validare ancora il payload
prima del salvataggio e rispettare stato gara/permessi autorevoli del backend.

Dopo i controlli del codice riallineare i documenti interessati. Commit solo .md
non bloccano il seguito in attesa della CI, per richiesta dell'autore alle 00:26.
Questa correzione include invece un workflow eseguibile e richiede verifica.
PROJECT_SPEC.md e PROJECT_STATUS.md protetti. Nessuna modifica a dipendenze,
lockfile, API, migrazioni, immagini o dati. Nessun test browser richiesto ora:
avviso manuale finale solo dopo completamento dei collegamenti e relativa CI
verde. Nessuna garanzia di concorrenza lato server introdotta dal merge frontend.
