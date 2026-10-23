# Fase 16 - Bozza locale nella UI admin

Aggiornamento: 2026-10-23. Ramo phase-16-admin-pilot-inventory, PR 15 in bozza.
Documento sorgente generale: PHASE_16_ADMIN_SAVE_API.md. Nessun merge.

## Integrazione implementata

c950510 collega CardTile alla sessione locale nei quattro componenti admin.
Ogni clic aggiunge source/path per una copia e ricalcola dalla baseline; le cinque
destinazioni sono imposte dal dominio. Cinque sezioni distinte, mazzo N/15 per
copie e differenza tra pool assente e vuota restano. Il blocco iniziale e le
destinazioni assenti disabilitano i clic. Errori locali distinti da quelli REST
non sostituiscono la bozza; le risposte tardive sono ignorate, non cancellate.

Lo stato pendente risale alle impostazioni. Ripristino, ritorno ai piloti e
chiusura richiedono conferma prima dello scarto. Ripristino alla baseline senza
riletture REST, conservando il blocco. I dialog sono montati solo quando aperti
e il modal sottostante non apre un altro dialog su Escape mentre ne esiste uno
sopra. La navigazione viene proposta prima della ripresa; un errore di goto
conserva la bozza. Con componente riusato, ripristino dopo successo soltanto
sulla sessione originale. Ricarica e chiusura senza destinazione usano la
protezione browser di SvelteKit. Le interazioni restano da collaudare nel browser.

## Formattazione e CI

2cf25fd separa pubblicazione dello stile e controlli successivi; ceb12b1 formatta
i soli quattro componenti. 788e6f5 aggiunge l'eccezione ESLint motivata sulla
sola chiamata goto che riusa navigation.to.url.href, senza modificare il codice
eseguibile. Dettagli e limiti dell'eccezione in PHASE_16_FORMATTING.md.

La lettura del 2026-10-23 della CI 40003767478 sulla testa 788e6f5 riporta
successo per frontend (check, lint, test, build), job 120586341966, backend,
migrazioni su database di test e documenti dopo backend. Anche align-docs-pr
40003767471 e' riuscito. Non sono esecuzioni locali, conteggi letti dai log
o prove browser. La CI include la toolchain, non prova tutte le interazioni UI.

## Limiti e prossimo passo

PUT dalla UI, riepilogo per il salvataggio, conferma unica e live non sono ancora
implementati. Nessun autosalvataggio, polling o secondo stream SSE. Il blocco
iniziale non equivale al live della gara. Nessuna migrazione, dipendenza nuova
o modifica al database reale. Restano prove browser di clic ripetuti, annullamento,
Escape, chiusura, navigazione ed errori. Fase non completa e nessun merge.
Il documento sorgente viene riallineato dopo la CI riuscita; la propagazione nei
dieci documenti generali deve ancora essere verificata sul nuovo commit, senza
attendere test applicativi per i soli docs.
