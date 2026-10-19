# Fase 14 - Formattazione con il formatter reale

Il 2026-10-19 l'autore ha riportato un nuovo arresto di npm run lint su quattro file: race-review-panel.svelte, review-incongruence-dialog.svelte, review-pilot-inventory.svelte e review-draft.spec.ts. Il precedente tentativo manuale non ha risolto completamente il problema.

Il workflow format-review-ui.yml usa Node 22, npm ci e il binario Prettier installato dal package-lock.json, con configurazione e plugin del repository. Non sostituisce né modifica ci.yml. Si avvia solo su phase-14 quando cambia il proprio file, quindi il successivo commit di formattazione non crea un ciclo.

L'automazione ha contents: write per pubblicare soltanto i quattro file elencati. Non esegue force push: se il ramo avanza durante l'operazione si ferma senza sovrascrivere altri commit. Dopo la pubblicazione esegue check, lint, test e build del frontend; un errore ferma i passaggi successivi ed è visibile nei log. Il push del bot non è considerato una garanzia di riavvio della CI ordinaria della PR: i controlli del workflow vanno letti separatamente e, se necessario, va rieseguita la CI sulla nuova testa.

Il commit di aggiunta del workflow non è una prova che il formatter abbia già girato. Esito Actions e SHA dell'eventuale commit automatico da verificare dopo l'esecuzione. Se le impostazioni di GitHub impediscono la scrittura, il push fallisce esplicitamente; nessun successo viene dichiarato in anticipo.

Nessuna modifica intenzionale alla logica applicativa, alle dipendenze, al backend o al database. Il workflow rimane nel ramo finché non viene rimossa esplicitamente l'automazione. Questa nota aggiorna PHASE_14_FORMATTING.md e le note UI sulla verifica ancora pendente.
