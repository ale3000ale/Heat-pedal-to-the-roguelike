# Draft - stato dell'integrazione e correzioni

25 ottobre 2026. Solo Heat-pedal-to-the-roguelike, ramo draft, PR 18.

## Incremento zoom locale

Lo zoom passa dal componente picking all'istanza esistente di DraftStore. Non vengono aggiunti coordinatori, singleton, persistenza o nuove richieste. Il riferimento include preparazione, campionato, slot_id, nome e percorso. Versione, turno, preview e chosen_by non lo invalidano; la carta puo restare ingrandita anche passando alle copie scelte. Il solo rimontaggio del picking con lo stesso store non elimina il valore.

sync conserva lo zoom durante loading/writing con snapshot valido e lo elimina a fine fase, perdita di accesso, cambio identita carta o dispose. toggleZoom e soltanto locale e rifiuta busy, blocchi e slot assenti. La preview viene proposta dal clic solo con i permessi gia esistenti; nessun invio automatico al cambio turno. Scelta e conferma restano vincolate a proprietario, versione e copia correnti.

File: stores/draft.svelte.ts, components/draft-picking.svelte, nuovo draft-zoom-store.spec.ts sotto frontend/src/lib; questo documento. DraftFlow, controller, CardTile, componente carta, backend e stream invariati. Scelta da preservato.

## Stato UI

1. Drag intera scheda e frecce pubblicati in 9ceedd5d49bf8ed05fdbf27cad79a459844d9b08; collaudo browser ancora necessario.
2. Indicatore della propria anteprima nascosto in 20a29699a2ef64bed4e4e85d964f3bc12a0b3601. Questo incremento aggiunge la conservazione dello zoom nello store, non il refactoring esteso precedentemente proposto. Difetto visivo completo non ancora collaudato.
3. Salti verticali dei mazzi ancora aperti: messaggi transitori, focus senza preventScroll e modal ad altezza variabile da verificare.

## Verifiche e limiti

Controller esaminato: refresh/command mantengono lo snapshot mentre lavorano; 401/403 lo svuotano. CardTile non contiene un reset dello zoom. Non e una riproduzione della chiusura immediata nel browser.

Regressioni predisposte per toggle senza rete, preview POST simulato, loading e preview altrui, rendering SSR ripetuto con lo stesso store, cambio turno/copia scelta, identita immagine diversa, fine fase, cambio contesto, risultati tardivi, isolamento istanze, dispose e 401/403. SSR non prova clic, reattivita DOM o rimontaggio client effettivo.

Nessuna installazione, formattazione, esecuzione locale lint/check/test/build o nuova lettura/attesa CI per questo incremento. Nessun test dichiarato superato. Ultimi esiti letti alle 15:58 sul commit 9ceedd5: backend e migrazioni superati, frontend e runtime falliti; causa non verificata dai log. Non attestano questi nuovi incrementi.

## Seguito e integrazione

Restano verifiche automatiche, collaudo reale di zoom/drag/SSE e correzione dello scroll dei mazzi. Documenti generali da riallineare dopo verifiche effettive. Controllo anticipato 15 carte rimosso in 0052c1d, vincoli READY/finale conservati. Nuova Gara usa il registro del layout, host/SSE condivisi e recupero REST accodato; nessuna gara dedotta da READY o sparizione REST. Regole in docs/DRAFT_SPEC.md invariate. Nessuna modifica a DB reale/schema, risorse, dipendenze o script; nessun merge o ZIP finale.
