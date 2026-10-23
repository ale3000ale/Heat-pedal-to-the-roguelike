# Fase 16 - Bozza locale nella UI admin

Aggiornamento: 2026-10-23. Solo ramo phase-16-admin-pilot-inventory, PR 15 in bozza.
Nessun merge, migrazione, modifica di dipendenze o accesso al database reale.
Documento sorgente generale: PHASE_16_ADMIN_SAVE_API.md.

## Baseline verificata

La chiusura intercettabile del modal in d9ee662 ha superato la CI 39997899845.
Il riallineamento documentale 013948f e' stato propagato dal bot e2fbdea nei dieci
documenti generali, senza attendere nuovi test applicativi per il commit docs.
Questi riscontri non costituiscono un collaudo browser.

## Integrazione proposta in questo incremento

I quattro componenti admin collegano CardTile alla sessione locale esistente.
Ogni clic aggiunge una sola operazione source/path e ricalcola dalla baseline.
La destinazione e' imposta dal pianificatore, non scelta dall'utente. Le cinque
sezioni, il conteggio N/15 e la distinzione tra pool assente e vuota restano.
Il blocco iniziale e le destinazioni assenti disabilitano i clic. Gli errori locali
non sostituiscono la bozza e sono distinti dagli errori della lettura REST.

Lo stato pendente risale al modal delle impostazioni. Ripristino, ritorno
all'elenco e chiusura richiedono conferma prima dello scarto. I dialog di
conferma sono montati solo mentre aperti; una conferma gia' sopra il pannello
gestisce Escape senza aprire un secondo dialog dal modal sottostante.
Il ripristino conserva la baseline e l'eventuale blocco, senza riletture REST.

La navigazione con destinazione viene prima annullata e proposta nel dialog
dedicato; dopo conferma viene ripresa con goto o location.assign. I clic sono
disabilitati durante l'uscita. Un errore di goto conserva la bozza; se il componente
e' riusato viene ripristinato solo dopo il successo e solo se la sessione e' ancora
quella originale. Per ricarica o chiusura scheda senza destinazione interviene
la protezione di uscita gestita dal browser tramite SvelteKit, non window.confirm.

## Verifiche e limiti

Nessuna nuova esecuzione locale di npm, Vitest o browser in questo incremento.
La toolchain deve ancora verificare i componenti modificati; non si dichiara PASS.
Il formatter esistente e' limitato ai quattro componenti e conserva npm ci,
Prettier dal lockfile e check/lint/test/build completi prima del commit del bot.
La CI ordinaria non cambia. I test del dominio, della sessione e della politica
di chiusura gia' presenti non equivalgono a test delle interazioni Svelte.

Non sono implementati PUT dalla UI, riepilogo per il salvataggio, conferma unica
del salvataggio o integrazione live. Il blocco iniziale non e' un aggiornamento
live della gara. Nessun autosalvataggio, polling o secondo stream SSE.
Dopo i controlli riusciti riallineare il documento sorgente e i documenti generali
allo stato verificato; per le sole modifiche docs non attendere test applicativi.
Restano da collaudare nel browser clic ripetuti, annullamento delle conferme,
Escape, chiusura, navigazione e conservazione della bozza in caso di errore.
