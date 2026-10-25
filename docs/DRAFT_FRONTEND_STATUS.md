# Draft - stato dell'integrazione e correzioni

25 ottobre 2026. Solo Heat-pedal-to-the-roguelike, ramo draft, PR 18.

## Incremento contenitore stabile

Modal riceve stableViewport opzionale, false per default. Solo DraftModal lo abilita nelle fasi picking/decks, comprese le viste READY e le conferme mostrate dentro quelle fasi. Presenze e ordine mantengono il layout naturale. Non vengono cambiati open, Escape, sfondo, X, conferma annullamento, inert, busy o permessi.

La classe locale viewport-stable assegna altezza 90vh con successivo 90dvh per i browser che lo supportano. Il limite massimo sottrae 2rem al viewport per rispettare il padding esterno anche su schermi bassi; box-sizing e border-box. Rimane lo stesso contenitore overflow-y-auto. scrollbar-gutter: stable riserva lo spazio della scrollbar dove supportato. L'altezza del riquadro non dipende piu dalla quantita di contenuto in quelle fasi; puo comunque cambiare con il viewport o all'ingresso/uscita delle fasi.

File: components/modal.svelte, components/draft-modal.svelte e nuovo draft-modal-layout.spec.ts sotto frontend/src/lib; questo documento. Gli altri chiamanti non ricevono un nuovo comportamento se non attivano l'opzione. Nessuna nuova gestione JavaScript dello scroll o ricostruzione intenzionale del dialog.

## Stato UI

1. Drag intera scheda e frecce: 9ceedd5d; da collaudare nel browser.
2. Indicatore proprio nascosto: 20a29699; zoom per copia nello store: d5d21088. Difetto visivo completo non ancora collaudato.
3. Focus automatico senza scroll: d80f2675. Spazio dei due messaggi transitori riservato in ca5c682df1b1f3fbc54fe2eb8d4d8f9c0d18b279. Questo incremento stabilizza il riquadro delle fasi carte/mazzi. Le griglie, gli errori e i riepiloghi interni possono ancora variare: non si dichiara assenza di tutti i movimenti verticali.

## Verifiche e limiti

Riletti modal condiviso, wrapper draft e test della policy di chiusura; due letture iniziali con 503 sono state ripetute con successo. Predisposti test SSR per default invariato, opt-in con contenuti corti/lunghi, attivazione per fase, modal chiuso, showClose e assenza di comandi dal rendering. Non misurano CSS calcolato, viewport, scrollTop, focus o geometrie reali.

Nessuna installazione, formattazione, esecuzione locale lint/check/test/build o nuova lettura/attesa CI per questo incremento. Nessun test dichiarato superato. Ultimi esiti letti alle 15:58 su 9ceedd5: backend/migrazioni superati, frontend/runtime falliti; causa non verificata dai log. Non attestano gli incrementi successivi.

## Seguito e integrazione

Prossimo passo: verifiche automatiche, correzione di eventuali fallimenti e collaudo browser mobile/desktop di focus, scroll interno, zoom, drag e SSE. Riallineamento generale dei documenti dopo verifiche effettive. Controllo anticipato 15 carte rimosso in 0052c1d; vincoli READY/finale conservati. Nuova Gara usa registro del layout, host/SSE condivisi e recupero REST accodato; nessuna gara dedotta da READY o sparizione REST. Regole in docs/DRAFT_SPEC.md invariate. Nessuna modifica a backend, DB reale/schema, risorse, dipendenze o script; nessun merge o ZIP finale.
