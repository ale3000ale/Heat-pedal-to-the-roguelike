# Draft - stato dell'integrazione e correzioni

25 ottobre 2026. Solo Heat-pedal-to-the-roguelike, ramo draft, PR 18.

## Incremento ridotto: indicatore di anteprima

Su richiesta dell'autore delle 19:55 il fix 2 viene diviso in commit piccoli e autonomi. Questo incremento cambia soltanto l'indicatore visuale: draftPickingView restituisce previewSlotId solo a chi non possiede il pilota del turno. Nome Anteprima di e alone non vengono quindi mostrati al proprietario, neppure durante loading/writing/blocked. Il DTO server, preview_slot_id, la coerenza dei riferimenti e i permessi dei comandi non vengono modificati.

File: frontend/src/lib/draft-picking.ts; nuovo frontend/src/lib/draft-preview-indicator.spec.ts; questo documento. Nessuna modifica ai componenti picking/card, quindi Scelta da resta invariato. Nessun modello zoom o collegamento parziale fra componenti viene introdotto.

## Stato delle tre segnalazioni UI

1. Drag dall'intera scheda e frecce: pubblicato in 9ceedd5d49bf8ed05fdbf27cad79a459844d9b08, da collaudare nel browser. Cattura del puntatore sull'ol stabile, soglia e geometrie iniziali, compensazione scroll; drop mantiene la bozza e cancel la ripristina. Nessuna scrittura durante il gesto; Avanti salva order se necessario e poi start, con permessi e versioni invariati.
2. Anteprima propria: modifica visuale predisposta in questo incremento. Conservazione dello zoom locale durante aggiornamenti, cambi turno o rimontaggio: ancora aperta. Il refactoring esteso proposto in conversazione non e stato pubblicato. La chiusura immediata non e stata riprodotta nel browser.
3. Salti verticali nei mazzi: ancora aperti. Messaggi transitori, focus senza preventScroll e modal centrato ad altezza variabile sono punti da verificare, non una causa unica accertata.

## Test e limiti

Nuove regressioni predisposte per indicatore proprio durante idle/writing/loading/blocked, DTO immutato e comandi preview invariati; SSR per nome/alone propri assenti e indicatore altrui presente anche per un gestore che non possiede il turno. Non sono prove di clic, zoom, SSE reale, drag, touch, focus o layout browser.

Nessuna installazione, formattazione, esecuzione locale di lint/check/test/build o nuova consultazione/attesa CI per questo incremento. Nessun test dichiarato superato. Ultimi esiti letti alle 15:58 sul commit 9ceedd5d49bf8ed05fdbf27cad79a459844d9b08: backend e migrazioni superati, job frontend e runtime falliti; causa non verificata dai log. Quegli esiti non attestano questa modifica.

## Integrazione precedente e seguito

Controllo anticipato delle 15 carte rimosso in 0052c1d4680ebcba8f7afc3690fa9a589927aac1; vincolo dopo modifica ai READY e ricontrollo finale conservati. Nuova Gara usa il registro del layout, host e SSE condiviso, notifiche accorpate e recupero REST accodato; nessuna gara dedotta da READY o sparizione REST, nessun nuovo polling o redirect. Regole in docs/DRAFT_SPEC.md.

Prossimo incremento: zoom locale, poi stabilita dei mazzi; verifiche automatiche e collaudo reale restano necessari. Riallineamento generale dei documenti dopo verifiche effettive. Nessuna modifica a backend, DB reale/schema, risorse, dipendenze o script; nessun merge o ZIP finale.
