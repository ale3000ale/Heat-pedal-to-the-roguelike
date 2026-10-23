# Fase 16 - Formattazione UI e navigazione gia' risolta

Aggiornamento: 2026-10-23. Ramo phase-16-admin-pilot-inventory. Nessun merge.
Documento sorgente generale: PHASE_16_ADMIN_SAVE_API.md.

## Correzioni pubblicate

Il primo log dell'autore mostrava Prettier fermato sui quattro componenti admin.
2cf25fd separa pubblicazione dello stile e controlli applicativi successivi;
il bot ceb12b1 formatta soltanto admin-card-container, admin-championship-pilots,
admin-pilot-cards-panel e championship-settings. Il log successivo mostra
Prettier riuscito e un errore ESLint svelte/no-navigation-without-resolve su goto.

788e6f5 aggiunge due commenti ad admin-pilot-cards-panel.svelte: provenienza della
URL completa da navigation.to.url.href e una sola direttiva eslint-disable-next-line
svelte/no-navigation-without-resolve prima di goto(target.url). Non disabilita
la regola per il file o il progetto, non aggiunge cast o dipendenze e non cambia
il codice eseguibile, le conferme o la conservazione della bozza su errore.
L'eccezione vale per la ripresa di questa URL gia' risolta, non per nuove rotte.

## Riscontro successivo effettivo

La lettura del 2026-10-23 della CI 40003767478 sulla testa 788e6f5 riporta
successo per Frontend (check, lint, test, build), job 120586341966, Backend
(pytest), Migrazioni (database di test) e Documenti fase 16 dopo backend.
Anche align-docs-pr 40003767471 risulta riuscito. Il blocco del lint segnalato
e' quindi superato nella toolchain osservata; non e' un collaudo browser.
Nessuna nuova esecuzione locale e nessun conteggio complessivo di test o warning
dai singoli log viene dichiarato.

Il formatter conserva npm ci, Prettier dal lockfile e i controlli completi dopo
la pubblicazione dello stile; stampa la SHA controllata e mantiene la protezione
del ramo remoto e dei percorsi estranei. Un commit del bot non prova da solo
il verde globale ne' garantisce una nuova CI ordinaria: verificare SHA e job.

## Limiti

Nessuna modifica applicativa in questo riallineamento documentale, al database
o alle dipendenze. PUT dalla UI, autosalvataggio e live restano esclusi.
Il documento sorgente e quello della UI vengono riallineati alla CI osservata;
verificare poi la propagazione nei documenti generali senza attendere altri
test applicativi per il solo commit docs. Fase non completa e nessun merge.
