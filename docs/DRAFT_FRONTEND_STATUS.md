# Draft - stato dell'integrazione e correzioni

25 ottobre 2026. Solo Heat-pedal-to-the-roguelike, ramo draft, PR 18.

## Incremento focus e scroll automatico

Primo intervento circoscritto sulla terza segnalazione: draftHostFocus passa preventScroll: true soltanto al focus automatico iniziale/di contenimento e al ripristino differito del focus precedente. La navigazione esplicita Tab/Shift Tab conserva focus() normale, cosi il browser puo rendere visibile il controllo raggiunto. Filtri dei controlli, listener, guardie alive/moving, cleanup e protezione del flusso successivo restano invariati.

File: frontend/src/lib/draft-host-focus.ts; nuovo frontend/src/lib/draft-host-focus.spec.ts; questo documento. Nessuna modifica ai modal, al layout delle carte, ai messaggi dei mazzi o ai protocolli di rete. La modifica impedisce la richiesta di scroll implicita di quelle chiamate automatiche; non prova che tutte le cause del salto siano eliminate.

## Stato UI

1. Drag intera scheda e frecce pubblicati in 9ceedd5d49bf8ed05fdbf27cad79a459844d9b08; collaudo browser necessario.
2. Indicatore della propria anteprima nascosto in 20a29699a2ef64bed4e4e85d964f3bc12a0b3601. Zoom per copia conservato nell'istanza DraftStore in d5d21088be06e63ee0258246ab9e999352c92c4b, indipendente da turno/versione/preview e con pulizia a fine fase, perdita accesso o dispose. Difetto visivo completo non ancora collaudato.
3. Scroll: focus automatico trattato in questo incremento; stabilita verticale dei mazzi ancora parziale. Messaggi di operazione/verifica aggiunti e rimossi, modal centrato ad altezza variabile e variazioni delle griglie restano da verificare/correggere. Non dichiarato risolto l'intero problema.

## Verifiche e limiti

Esaminati draft-modal.svelte, draft-decks.svelte, modal.svelte e draft-host-focus.ts. I dati delle carte non vengono sostituiti da questa modifica. Predisposti test con DOM minimo simulato per ingresso/recupero focus, fallback al contenitore, Tab/Shift Tab, ripristino, rimozione listener, flusso successivo e autofocus pendente dopo destroy/disconnessione.

I test verificano chiamate e opzioni focus, non scrollTop, geometrie, eventi nativi o browser reale. Nessuna installazione, formattazione, esecuzione locale lint/check/test/build o nuova lettura/attesa CI per questo incremento. Nessun test dichiarato superato. Ultimi esiti letti alle 15:58 sul commit 9ceedd5: backend e migrazioni superati, frontend e runtime falliti; causa non verificata dai log. Non attestano gli incrementi successivi.

## Seguito e integrazione

Prossimo intervento mirato: spazio dei messaggi transitori nei mazzi e stabilita del contenitore, poi verifiche automatiche e collaudo reale di focus/scroll/zoom/drag/SSE. Documenti generali da riallineare dopo verifiche effettive. Controllo anticipato 15 carte rimosso in 0052c1d, vincoli READY/finale conservati. Nuova Gara usa registro del layout, host/SSE condivisi e recupero REST accodato; nessuna gara dedotta da READY o sparizione REST. Regole in docs/DRAFT_SPEC.md invariate. Nessuna modifica a backend, DB reale/schema, risorse, dipendenze o script; nessun merge o ZIP finale.
