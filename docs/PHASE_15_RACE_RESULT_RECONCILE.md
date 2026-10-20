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
ancora dichiarato superato: leggere la CI del codice prima del collegamento.

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
PROJECT_SPEC.md e PROJECT_STATUS.md protetti. Nessuna modifica a workflow,
dipendenze, lockfile, API, migrazioni, immagini o dati in questo blocco.
Nessun test browser richiesto ora: avviso manuale finale solo dopo completamento
dei collegamenti e relativa CI verde. Nessuna garanzia di concorrenza lato server
introdotta da questo merge del solo modulo frontend.
