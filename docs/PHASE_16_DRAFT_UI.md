# Fase 16 - Integrazione progressiva della bozza nella UI

Aggiornamento: 2026-10-23. Ramo phase-16-admin-pilot-inventory, PR 15 in bozza.
Nessun merge, setup, migrazione o accesso al database reale.
Documento sorgente generale: PHASE_16_ADMIN_SAVE_API.md.

## Baseline e verifiche osservate

Il bot 08f3443 ha propagato lo stato di dominio e sessione nei dieci documenti
gestiti. La CI 39995224182 risultava riuscita per frontend, backend, migrazioni
e documenti. Il sottoincremento seguente e' stato pubblicato con d9ee662.

La lettura del 2026-10-23 della CI 39997899845 su d9ee662 riporta successo per
Frontend (check, lint, test, build), job 120566109552, Backend (pytest),
Migrazioni (database di test) e Documenti fase 16 dopo backend. Anche
align-docs-pr 39997899981 e format 39997890111 risultano riusciti.
Il ramo osservato resta su d9ee662: nessun ulteriore commit di formattazione
osservato. Questi riscontri non sono nuove esecuzioni locali o prove browser;
non vengono inventati conteggi complessivi di test o warning dai soli stati.

## Primo sottoincremento: chiusura intercettabile

modal.svelte aggiunge onrequestclose opzionale. Senza intercettore mantiene
le chiusure esistenti: X sempre disponibile, Escape e sfondo rispettano
closeOnOutside. Con intercettore delega la richiesta senza impostare open=false:
il chiamante deve decidere se chiudere dopo la conferma. Un errore del callback
non autorizza la chiusura predefinita. Non sono introdotti dialog o confirm nativi.

La politica e' separata in lib/modal-close.ts. Dodici casi parametrizzati sono
presenti in modal-close.spec.ts. Prima del commit il corpo della funzione, con
annotazioni di tipo rimosse in una copia temporanea, e' stato verificato con
Node e assert in dodici scenari: esito OK. Quel controllo non era Vitest,
type-check o rendering Svelte; la successiva CI frontend e' riuscita.

Il formatter esistente format-review-ui.yml resta limitato al ramo fase 16 e
formatta soltanto modal-close.ts, modal-close.spec.ts e modal.svelte. Conserva
npm ci dal lockfile, controllo Prettier e check/lint/test/build completi prima
di un eventuale commit del bot. La CI ordinaria non e' modificata.

## Limiti e passo successivo

Questo sottoincremento non attiva ancora le carte cliccabili: i pannelli admin
restano in consultazione e non passano ancora onrequestclose. Il collegamento
successivo deve usare la sessione locale, propagare lo stato pendente fino
al modal delle impostazioni e confermare ritorno all'elenco, ripristino e chiusura
prima di scartare dati. Anche la navigazione richiede una protezione dedicata.
Nessuna PUT, autosalvataggio, polling, evento nuovo o secondo stream SSE.

Con i controlli applicativi riusciti si riallinea il documento sorgente della fase;
la propagazione nei documenti generali resta da verificare dopo il relativo
commit. Nessuna ulteriore attesa dei test applicativi per aggiornamenti solo
documentali. Nessun collaudo browser gia' dichiarato PASS e fase non completa.
