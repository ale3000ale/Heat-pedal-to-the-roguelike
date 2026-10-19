# Fase 14 - Verifiche di formattazione UI

Il 2026-10-19 l'autore ha riportato npm run lint fallito su Prettier nei sei file della nuova UI: race-review-panel.svelte, review-incongruence-dialog.svelte, review-pilot-inventory.svelte, review-draft.spec.ts, review-draft.ts e stores/review-counts.svelte.ts. ESLint non è stato eseguito perché concatenato con &&.

Correzione di sola formattazione predisposta manualmente per tutti i sei file, senza modifiche intenzionali alla logica o alle dipendenze. Le funzioni e i test restano quelli del commit a5f06f0.

Diagnostica effettivamente eseguita nell'ambiente dell'assistente: Node, npm e npx disponibili; Prettier non installato. npm exec --offline --package=prettier -- prettier --version è fallito con ENOTCACHED. Pertanto Prettier, ESLint, Vitest, type-check e build non sono stati eseguiti. Non si dichiara la correzione verificata: serve il nuovo esito CI.

Questa nota integra PHASE_14_REVIEW_UI.md, senza dichiarare completata la validazione end-to-end. Nessun cambiamento a backend, schema o database reale.
