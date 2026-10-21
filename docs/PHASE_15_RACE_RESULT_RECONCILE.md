# Fase 15a-4b - Riconciliazione dei risultati gara

Aggiornamento: 2026-10-21. Solo phase-15-sse-sistemazione, PR 14 in bozza.
Funzione pura verificata su 3c860d2 in CI 39509635060, ora usata dalla pagina gara:
collegamento 4833a8d, fix 44bb4dd, testa 4978f73 e CI 39596834057 verde.
Nessun merge o intervento sui dati autorizzato da questo riallineamento.

## Decisione e contratto

Scelta dopo proposta delle 00:27: ordine/assenti unica assegnazione coerente,
sponsor riconciliati per pilota. Assegnazione locale modificata conservata, non
importare separatamente liste remote che duplicano piloti. Se il remoto rimuove
dalla classifica un pilota con sponsor modificati, preservare il locale e segnalare
conflitto. race-result-reconcile.ts espone ResultForm, hasResultChanges e reconcileResults.

Tre vie: base server, copia locale, nuovo remoto nello stesso contesto. Nomi non
editabili, undefined conserva input sponsor vuoto senza anticipare normalizzazione
zero. Restituisce nuove righe/liste, conflitto, assegnazione preservata e modifiche
residue. Duplicati generano RangeError, non correzioni silenziose. Niente REST,
timer, dipendenza Svelte o autorizzazione nel modulo. Nessuna nuova garanzia di
concorrenza lato server dal merge frontend.

## Cronologia e verifiche

Implementazione cebccebfbda69f8d9a1c24623f0c29fcfeefe905, prima CI 39509013765:
frontend failure 00:34:08 CEST, migrazioni success 00:34:10, backend success 00:36:10
il 2026-10-21. Log autore 00:36: Prettier del solo race-result-reconcile.ts. ESLint
non parte dopo prettier --check fallito, nessun test/build frontend certificato
per quel tentativo. Workflow 823572fcd165b67a76250460098edc430969ca5e limitato al modulo,
con npm ci/Prettier dal lockfile e lint/check/test/build prima di pubblicare.
Protezione da ramo cambiato e nessun force push, trigger sul solo ramo previsto.

Bot 3c860d2f9c576146a1867ca0da65634d0dc1d138 alle 00:38:52: diff letto, sola espressione
conflict su una riga, nessun cambio logico o alla suite. CI 39509635060 tutta verde.
https://github.com/ale3000ale/Heat-pedal-to-the-roguelike/actions/runs/39509635060

| Job | Esito | Conclusione CEST del 2026-10-21 |
|---|---|---|
| Migrazioni (database di test) | success | 00:40:00 |
| Frontend (check, lint, test, build) | success | 00:40:28 |
| Backend (pytest) | success | 00:41:44 |

Suite passata: adozione remota, immutabilita', sponsor con riordino, assegnazione
accoppiata, sola lista assenti modificata, pilota spostato dal remoto, input vuoto,
conflitto, convergenza, base PUT e duplicati. Esiti/commit/diff verificati, non log
completi o conteggi. Nessun comando locale. Prove pure, non DOM o autorizzazione.

## Uso corrente e limiti

La pagina gara importa ora il modulo e tiene base server separata dal lavoro locale.
La copia preinvio e' base del merge della risposta PUT per conservare nuove modifiche.
Il pannello usa rilettura coordinata, non reload completo. Bozza risultati in sola
lettura quando permessi cambiano, uscita protetta con modifiche o richiesta in corso.
Il collegamento ha superato la CI su 4978f73: dettagli in PHASE_15_RACE_LIVE.md.
Non confondere codice presente/CI verde con guardie e rendering collaudati nel browser.

Store inventari ancora da collegare al proprio helper, non a questo merge risultati:
sono dati e bozze distinti. Politica conservativa degli inventari nella nota
PHASE_15_REVIEW_INVENTORY_RECONCILE.md. Prossimo blocco: integrazione interna con
spunte, blocchi, conferma della rilettura e test mirati. Nessun nuovo prerequisito backend.

Solo riallineamento di documenti in questo push, niente codice, workflow, dipendenze,
lockfile, API, schema, immagini o dati. PROJECT_SPEC.md e PROJECT_STATUS.md protetti.
Commit solo .md non bloccano il seguito in attesa CI, come richiesto alle 00:26.
Nessuna prova browser richiesta ora: avviso e checklist finale dopo completamento
dei collegamenti restanti e relativi controlli verdi. Nessun merge autorizzato.
