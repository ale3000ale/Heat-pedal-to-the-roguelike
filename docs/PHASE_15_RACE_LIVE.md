# Fase 15a-4b - Collegamento gara e callback revisione

Aggiornamento: 2026-10-21. Solo phase-15-sse-sistemazione, PR 14 in bozza.
Riepilogo abbreviato; cronologia dettagliata nella versione fcead0f e nella storia Git.

## Gara collegata e verificata

Implementazione 4833a8d, fix nullable 44bb4dd, bot formattazione 4978f73.
CI 39596834057 verde: migrazioni 14:06:53 CEST, frontend 14:07:09,
backend pytest 14:08:53 del 2026-10-21. Il primo tentativo 4833a8d falli' il
frontend/type-check; nessun test/build riuscito attribuito a quel tentativo.
Il fix usa knownPilotIds da race?.results o [], non race!, cast o soppressioni.

La pagina gara usa startLiveRefresh condiviso per gara/campionato/piloti propri;
eventi campionato/resync coprono anche is_last. Fallback solo senza stream open.
Base server separata da ordine/assenti/sponsor, merge puro verificato in 3c860d2.
Risultati ufficiali/permessi aggiornati; bozza locale preservata e in sola lettura
se non modificabile, solo in memoria fino all'uscita. Nessun autosalvataggio.
PUT esplicita con copia preinvio, controllo piloti/duplicati/ID e massimo 12;
normalizzazione sponsor preesistente. Letture durante PUT non applicate, nuova
lettura accorpata dopo esito anche fallito. Nessun lock ottimistico backend.

Uscita interna/unload protetti con bozza o PUT in corso; uscire non annulla HTTP.
Sessione scaduta non blocca autenticazione; errori conservano dati, 401 svuota auth.
Cleanup e risposte vecchie gestiti per contesto. Pannello usa onchanged, non reload,
ricreato per campionato/gara/utente/stato, non a ogni snapshot risultati.

## Store revisione: aggiornamento distinto

Non e' piu' corretto dire che review-counts.svelte.ts sia invariato.
Dal bot 01c567a usa ownReviewKey, controlla utente e inizio revisione prima di
inviare conteggi e ricontrolla il contesto fra PUT e DELETE di rinuncia.
CI ordinaria 39636047244: frontend, backend e migrazioni di test tutti success.
Dettagli e sei test in PHASE_15_REVIEW_SESSION_GUARD.md.

Questo NON collega ancora inventari/bozze alla coda SSE interna: il merge
reconcileReviewInventory, verificato su 6aa7fe6, non e' usato dallo store/pannello.
Il pannello e la sua apertura automatica non sono cambiati nel blocco guardie.
La ricreazione per stato puo' smontarlo: lifecycle, conservazione copie e recupero
restano da affrontare nel collegamento effettivo, non certificati dai test guardie.
Verifica preinvio e richiesta successiva non sono una transazione atomica.

## Limiti e seguito

Warning canvas role img non corretto. CI verde non significa assenza di warning,
prova DOM, callback/guardie uscita o modifiche durante PUT collaudate nel browser.
Nessun comando locale o nuovo collaudo manuale dell'assistente.

Workflow review-session-guard applica una patch deterministica allo store originale,
formatta store/test e pubblica solo dopo tutti i controlli. Il vecchio formatter
format-sse-client resta una configurazione di un blocco precedente, non il nuovo
collegamento SSE del pannello.

Questo riallineamento e' solo documentale: codice, workflow, API, schema, immagini,
lockfile e dati intatti. PROJECT_SPEC.md e PROJECT_STATUS.md protetti. Non attendere
CI dei soli .md. Seguito: coda live interna, merge conservativo, revoca spunte,
blocchi e recupero confermato, con test lifecycle/permessi; poi collaudo browser.
Avviso manuale finale solo dopo collegamenti restanti e CI verde. Nessun merge.
