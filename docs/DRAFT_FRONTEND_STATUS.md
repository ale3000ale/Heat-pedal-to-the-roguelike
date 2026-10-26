# Draft - stato dell'integrazione e correzioni

26 ottobre 2026. Solo Heat-pedal-to-the-roguelike, ramo draft, PR 18.

## Correzione mirata lint del test focus

Il log fornito dall'autore alle 04:02 identifica il blocco: Prettier ha completato il controllo con successo, mentre ESLint segnala @typescript-eslint/no-this-alias per activeElement = this in draft-host-focus.spec.ts. Non si deduce dal log che test o build successivi siano passati, ne che la causa del job runtime sia la stessa.

Il DOM simulato ora conserva l'elemento attivo nella proprieta di un oggetto focusState, aggiornando il mock focus, l'inizializzazione, il getter document.activeElement e setActive. Non viene creato un alias locale di this e non vengono aggiunte soppressioni, eccezioni ESLint o modifiche alla configurazione. Due asserzioni verificano che document.activeElement simulato segua il focus iniziale e il recupero del focus esterno. Gli altri casi restano invariati.

File di questo incremento: frontend/src/lib/draft-host-focus.spec.ts e questo documento. Nessuna modifica al focus applicativo, al modal o alla logica mazzi. Nessuna esecuzione locale lint/check/test/build o nuova consultazione/attesa CI: patch predisposta, non dichiarata verificata. Il terzo problema dei salti verticali resta aperto fino al collaudo reale. Riallineamento generale dei documenti dopo verifiche effettive, non anticipato con esiti inventati.

Le sezioni seguenti conservano il riepilogo dell'incremento contenitore del 25 ottobre.

## Incremento contenitore stabile

Modal riceve stableViewport opzionale, false per default. Solo DraftModal lo abilita nelle fasi picking/decks, comprese le viste READY e le conferme mostrate dentro quelle fasi. Presenze e ordine mantengono il layout naturale. Non vengono cambiati open, Escape, sfondo, X, conferma annullamento, inert, busy o permessi.

La classe locale viewport-stable assegna altezza 90vh con successivo 90dvh per i browser che lo supportano. Il limite massimo sottrae 2rem al viewport per rispettare il padding esterno anche su schermi bassi; box-sizing e border-box. Rimane lo stesso contenitore overflow-y-auto. scrollbar-gutter: stable riserva lo spazio della scrollbar dove supportato. L'altezza del riquadro non dipende piu dalla quantita di contenuto in quelle fasi; puo comunque cambiare con il viewport o all'ingresso/uscita delle fasi.

File: components/modal.svelte, components/draft-modal.svelte e nuovo draft-modal-layout.spec.ts sotto frontend/src/lib; questo documento. Gli altri chiamanti non ricevono un nuovo comportamento se non attivano l'opzione. Nessuna nuova gestione JavaScript dello scroll o ricostruzione intenzionale del dialog.

## Stato UI

1. Drag intera scheda e frecce: 9ceedd5d; da collaudare nel browser.
2. Indicatore proprio nascosto: 20a29699; zoom per copia nello store: d5d21088. Difetto visivo completo non ancora collaudato.
3. Focus automatico senza scroll: d80f2675. Spazio dei due messaggi transitori riservato in ca5c682df1b1f3fbc54fe2eb8d4d8f9c0d18b279. Riquadro delle fasi carte/mazzi stabilizzato in a19d4d8e36e2a54f59298ebc3f38bbb3c479259c. Le griglie, gli errori e i riepiloghi interni possono ancora variare: non si dichiara assenza di tutti i movimenti verticali.

## Verifiche e limiti

Per l'incremento contenitore erano stati riletti modal condiviso, wrapper draft e test della policy di chiusura; due letture iniziali con 503 ripetute con successo. Predisposti test SSR per default invariato, opt-in con contenuti corti/lunghi, attivazione per fase, modal chiuso, showClose e assenza di comandi dal rendering. Non misurano CSS calcolato, viewport, scrollTop, focus o geometrie reali.

Esiti CI letti nella conversazione sul commit a19d4d8e: backend/migrazioni superati, frontend/runtime falliti. Il log dell'autore documenta il singolo errore ESLint del test focus; non attesta un nuovo esito dopo questa correzione e non identifica il primo errore del runtime.

## Seguito e integrazione

Prossimo passo: verifiche automatiche, correzione di eventuali fallimenti e collaudo browser mobile/desktop di focus, scroll interno, zoom, drag e SSE. Controllo anticipato 15 carte rimosso in 0052c1d; vincoli READY/finale conservati. Nuova Gara usa registro del layout, host/SSE condivisi e recupero REST accodato; nessuna gara dedotta da READY o sparizione REST. Regole in docs/DRAFT_SPEC.md invariate. Nessuna modifica a backend, DB reale/schema, risorse, dipendenze o script; nessun merge o ZIP finale.
