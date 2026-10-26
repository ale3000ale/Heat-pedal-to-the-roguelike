# Draft - stato dell'integrazione e correzioni

26 ottobre 2026. Solo Heat-pedal-to-the-roguelike, ramo draft, PR 18.

## Correzione check nel cleanup scroll

Il log fornito dall'autore alle 04:21 sul nuovo incremento scroll identifica un errore di npm run check: scroller is possibly null in draft-deck-scroll.ts, nella rimozione dei listener dentro function cancel. Il controllo termina con un errore e zero warning; non attesta il superamento dei passaggi successivi.

La correzione definisce cancel come const con funzione freccia dopo la guardia che esclude il dialog nullo. Mantiene il narrowing del riferimento nella closure senza cast, asserzioni non-null, optional chaining sul cleanup o disattivazione dei controlli. Corpo del cleanup, idempotenza, listener, calcolo del delta e integrazione nei mazzi restano invariati. I test esistenti del cleanup non vengono rimossi o indeboliti.

File di questa correzione: frontend/src/lib/draft-deck-scroll.ts e questo documento. Nessuna esecuzione locale lint/check/test/build, nuova lettura o attesa CI per questa correzione. Esito della patch ancora da verificare; nessun via libera al collaudo manuale prima dei controlli verdi sul commit corretto. Il terzo problema resta aperto.

## Verifica della base e incremento scroll

Controlli esistenti letti il 26 ottobre dopo il messaggio dell'autore delle 04:07: sul commit 1f5075fec58b6c3f8134995b386c890293e2880d risultano completati con successo frontend (check/lint/test/build), runtime, backend pytest e migrazioni. I due job documentali di fase 16 sono skipped. Questi esiti validano quella base, non il successivo incremento scroll 01cc4e51cee295ecdc03c18b90a2f06613db4769 o la correzione corrente, e non sono una prova browser dello scroll.

Sull'incremento 01cc4e51 la lettura successiva ha mostrato frontend/runtime falliti, migrazioni superate e backend ancora in corso a quella lettura. Il log dell'autore identifica il blocco del controllo tipi; non viene attribuita senza un log la causa esatta del job runtime.

## Posizione della griglia dopo lo spostamento

Il componente mazzi cattura la posizione della griglia di origine rispetto al dialog prima di chiamare il coordinatore move esistente. Dopo successo di scrittura e rilettura attende tick di Svelte e compensa il delta residuo su scrollTop del medesimo dialog. Il riferimento e la griglia, non la singola carta che puo scomparire quando si sposta l'ultima copia. InventorySection mantiene il contenitore anche se la griglia diventa vuota.

Non corregge se cambiano store, coordinatore, pilota, fase, disponibilita dei dati o busy/blocco. Wheel, touchstart, pointerdown e keydown nel dialog segnalano una nuova intenzione utente e impediscono il recupero. Un nuovo move cancella la cattura precedente; finally e cleanup del componente rimuovono i listener, anche in caso di errore o smontaggio. Handle monouso, senza timer o rete.

Il delta e relativo al dialog, quindi il solo spostamento del modal nel viewport non provoca una correzione. Non raddoppia un ancoraggio gia applicato dal browser. Rispetta i nuovi limiti di scorrimento: se il contenuto diventa troppo corto la posizione precedente puo non essere fisicamente mantenibile. Non sposta il focus, non ripristina carte, non modifica dati ottimisticamente, non cambia permessi e non ritenta richieste. Non viene applicato automaticamente alle sole notifiche SSE o alle operazioni fallite.

File dell'incremento: frontend/src/lib/draft-deck-scroll.ts e draft-deck-scroll.spec.ts; components/draft-decks.svelte sotto frontend/src/lib e questo documento. Controller e coordinatore dei mazzi restano invariati.

## Stato UI e limiti

Drag intera scheda/frecce: 9ceedd5d. Indicatore proprio: 20a29699. Zoom nello store: d5d21088. Focus automatico senza scroll: d80f2675. Spazio dei messaggi transitori: ca5c682d. Viewport stabile del modal: a19d4d8e. Correzione lint test focus senza soppressioni: 1f5075fe.

Test predisposti dell'helper per delta, ancoraggio nativo gia applicato, posizione relativa al dialog, limiti superiori/inferiori, input utente, riferimenti disconnessi/nascosti/riparentati, cleanup e geometrie invalide. Sono mock di geometrie e listener, non un browser o un ciclo Svelte client. Non attestano i tempi reali di focus, eventi o layout.

Il terzo problema resta aperto fino alla verifica del ciclo clic/POST/GET/rendering in browser mobile e desktop. I documenti generali vanno riallineati alla chiusura verificata del ciclo, senza anticipare successi della nuova patch.

## Integrazione preservata

Controllo anticipato 15 carte rimosso in 0052c1d; vincoli READY/finale conservati. Nuova Gara usa registro del layout, host/SSE condivisi e recupero REST accodato; nessuna gara dedotta da READY o sparizione REST. Regole in docs/DRAFT_SPEC.md invariate. Nessuna modifica a backend, DB reale/schema, risorse, dipendenze, script o workflow; nessun merge o ZIP finale.
