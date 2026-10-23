# Fase 16 - Integrazione progressiva della bozza nella UI

Data: 2026-10-23. Solo ramo phase-16-admin-pilot-inventory, PR 15 in bozza.
Nessun merge, setup, migrazione o accesso al database reale.

## Baseline osservata

Il bot 08f3443 ha propagato lo stato di dominio e sessione nei dieci documenti
gestiti. La lettura della CI 39995224182 riporta successo per frontend
(check, lint, test, build), backend pytest, migrazioni su database di test
e documenti dopo backend. Non e' un'esecuzione locale ne' un collaudo browser.

## Primo sottoincremento: chiusura intercettabile

modal.svelte aggiunge onrequestclose opzionale. Senza intercettore mantiene
le chiusure esistenti: X sempre disponibile, Escape e sfondo rispettano
closeOnOutside. Con intercettore delega la richiesta senza impostare open=false:
il chiamante deve decidere se chiudere dopo la conferma. Un errore del callback
non autorizza la chiusura predefinita. Non sono introdotti dialog o confirm nativi.

La politica e' separata in lib/modal-close.ts. Dodici casi parametrizzati sono
preparati in modal-close.spec.ts. Il corpo della funzione, con annotazioni di tipo
rimosse in una copia temporanea, e' stato verificato con Node e assert in dodici
scenari: esito OK. Non sono esecuzioni di Vitest, type-check o rendering Svelte.
I nuovi file e il componente restano da verificare con la toolchain del repository.

Il formatter esistente format-review-ui.yml resta limitato al ramo fase 16 e
ora formatta soltanto modal-close.ts, modal-close.spec.ts e modal.svelte.
Conserva npm ci dal lockfile, controllo Prettier e check/lint/test/build completi
prima di un eventuale commit del bot. La CI ordinaria non e' modificata.

## Limiti e passo successivo

Questo sottoincremento non attiva ancora le carte cliccabili: i pannelli admin
restano in consultazione e non passano ancora onrequestclose. Il prossimo
collegamento dovra' usare la sessione locale, propagare lo stato pendente fino
al modal delle impostazioni e confermare ritorno all'elenco, ripristino e chiusura
prima di scartare dati. Anche la navigazione richiede una protezione dedicata.
Nessuna PUT, autosalvataggio, polling, evento nuovo o secondo stream SSE.

Dopo i controlli riusciti riallineare il documento sorgente della fase e verificarne
la propagazione nei documenti generali, senza attendere test applicativi per
i soli aggiornamenti documentali. Nessun collaudo browser gia' dichiarato PASS.
