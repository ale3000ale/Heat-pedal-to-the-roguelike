# Draft - stato dell'integrazione e correzioni

25 ottobre 2026. Solo Heat-pedal-to-the-roguelike, ramo draft, PR 18.

## Incremento feedback stabile nei mazzi

I messaggi Operazione in corso e Il mazzo deve essere caricato o verificato restano nel layout della schermata mazzi con pilota selezionato. Quando non pertinenti usano invisible e aria-hidden, non hidden/display:none o rimozione condizionale. Lo spazio segue il wrapping del testo alla larghezza disponibile, senza altezza fissa o clipping. Un contenitore space-y-1 raccoglie le due righe prima del pulsante di rilettura e delle carte.

La variazione di busy/current cambia la visibilita, non la presenza di quelle righe. Errori e blocchi restano visibili secondo la logica precedente. Dati vecchi, carte, conteggi, READY, permessi, selezione pilota, lifecycle, chiamate e serializzazione restano invariati. Non e un congelamento dell'intero layout: griglie, messaggi di errore, riepiloghi e modal possono ancora cambiare altezza.

File: frontend/src/lib/components/draft-decks.svelte, frontend/src/lib/draft-decks-ui.spec.ts e questo documento. Modal condiviso, controller, coordinatore mazzi, focus e backend non modificati qui.

## Stato UI

1. Drag intera scheda e frecce: 9ceedd5d; collaudo browser ancora necessario.
2. Indicatore proprio nascosto: 20a29699. Zoom per copia nello store, indipendente da turno/versione/preview: d5d21088. Difetto visivo completo non ancora collaudato.
3. Focus automatico con preventScroll, Tab normale: d80f2675374386830dc279a1e6f1599c125cf62a. Questo incremento riserva lo spazio dei due messaggi transitori. Stabilita del contenitore e variazioni delle griglie ancora da trattare/verificare; problema complessivo non dichiarato risolto.

## Verifiche e limiti

Esaminati componente, coordinatore e vista dei mazzi. Predisposte regressioni SSR prima/durante/dopo rilettura simulata, mantenimento delle carte e delle righe, visibilita/aria-hidden di busy e verifica, dati obsoleti e recupero esplicito. I casi precedenti su proprietari, conteggi e READY restano nel file.

Queste verifiche non misurano altezza, scrollTop, reattivita DOM o annunci reali di un lettore di schermo. Nessuna installazione, formattazione, esecuzione locale lint/check/test/build o nuova lettura/attesa CI per questo incremento. Nessun test dichiarato superato. Ultimi esiti letti alle 15:58 su 9ceedd5: backend/migrazioni superati, frontend/runtime falliti; causa non verificata dai log. Non attestano gli incrementi successivi.

## Seguito e integrazione

Prossimo intervento: stabilita del contenitore senza alterare gli altri modal, poi verifiche automatiche e collaudo browser di focus/scroll/zoom/drag/SSE. Documenti generali da riallineare dopo verifiche effettive. Controllo anticipato 15 carte rimosso in 0052c1d, vincoli READY/finale conservati. Nuova Gara usa registro del layout, host/SSE condivisi e recupero REST accodato; nessuna gara dedotta da READY o sparizione REST. Regole in docs/DRAFT_SPEC.md invariate. Nessuna modifica a DB reale/schema, risorse, dipendenze o script; nessun merge o ZIP finale.
