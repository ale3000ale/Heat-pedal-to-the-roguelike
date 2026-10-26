# Draft - stato dell'integrazione e correzioni

26 ottobre 2026. Solo Heat-pedal-to-the-roguelike, ramo draft, PR 18.

## Correzione lint dell'identita del coordinatore

Il log dell'autore delle 04:51 mostra Prettier superato e tre errori svelte/require-store-reactive-access in draft-decks.svelte: confronto con current nel cleanup e confronto decks === target dopo await tick. Il log non attesta il superamento di test/build successivi o un nuovo esito runtime.

Il componente conserva nella cattura la funzione subscribe del coordinatore, confrontandola con current.subscribe nel cleanup e decks.subscribe prima del recupero scroll. La factory createDraftDeckSession crea questa closure una volta per istanza e non la sostituisce alle emissioni. Cio mantiene il controllo dell'identita del coordinatore senza confrontare direttamente store grezzi o confrontare erroneamente copie dei loro valori tramite $decks/get.

Restano le guardie sullo store principale, compatibilita, pilota, fase, versione dei dettagli, busy/blocco e identita della cattura. Cleanup, annullamento per input utente, gestione errori, sequenza POST/GET/tick e logica dati restano invariati. Nessuna soppressione ESLint, modifica alle regole, nuova sottoscrizione o richiesta aggiunta.

File di questa correzione: frontend/src/lib/components/draft-decks.svelte e questo documento. Nessuna esecuzione locale check/lint/test/build o nuova consultazione/attesa CI per questa correzione. Esito della patch ancora da verificare; collaudo manuale non ancora autorizzato come pronto.

## Correzioni e verifiche precedenti

Nullabilita di scroller nel cleanup corretta in df2e91a9e47db6d3b0ea3245d6f7259192b4e01c: cancel e una funzione freccia dopo la guardia, senza cast o asserzioni non-null. Il log precedente dell'autore identificava un errore di npm run check. Nessun test del cleanup e stato rimosso o indebolito.

Sul commit base 1f5075fec58b6c3f8134995b386c890293e2880d erano stati letti con successo frontend (check/lint/test/build), runtime, backend e migrazioni; due job documentali skipped. Questi esiti non attestano i successivi incrementi scroll. Sul commit 01cc4e51 erano stati letti frontend/runtime falliti, migrazioni superate e backend ancora in corso a quella lettura.

## Posizione della griglia dopo lo spostamento

L'incremento 01cc4e51cee295ecdc03c18b90a2f06613db4769 cattura la posizione della griglia di origine rispetto al dialog prima del move. Dopo successo di scrittura/rilettura e tick di Svelte compensa il delta residuo sullo scroll interno dello stesso contesto. La griglia permane anche quando scompare l'ultima copia. Non sposta focus, carte o scroll della pagina; nessun dato ottimistico o retry.

La cattura e monouso e viene annullata da wheel/touchstart/pointerdown/keydown nel dialog, nuovo move, cleanup o errore. Riferimenti disconnessi, nascosti o riparentati non vengono recuperati. Il delta relativo al dialog evita di compensare il semplice spostamento del modal e non raddoppia l'ancoraggio gia eseguito dal browser. La posizione e limitata alla nuova estensione del contenuto. Nessun recupero automatico sulle sole notifiche SSE o sulle operazioni fallite.

## Stato UI e limiti

Drag intera scheda/frecce: 9ceedd5d. Indicatore proprio: 20a29699. Zoom nello store: d5d21088. Focus automatico senza scroll: d80f2675. Spazio dei messaggi: ca5c682d. Viewport stabile: a19d4d8e. Correzione lint test focus: 1f5075fe.

I test dell'helper scroll usano geometrie/listener simulati; gli altri test UI includono SSR. Non attestano un ciclo Svelte client o il comportamento browser reale. Il terzo problema resta aperto fino ai controlli verdi del commit da provare e al collaudo clic/POST/GET/rendering su mobile e desktop. Documenti generali da riallineare alla chiusura verificata del ciclo, senza anticipare esiti positivi.

## Integrazione preservata

Controllo anticipato 15 carte rimosso in 0052c1d; vincoli READY/finale conservati. Nuova Gara usa registro del layout, host/SSE condivisi e recupero REST accodato; nessuna gara dedotta da READY o sparizione REST. Regole in docs/DRAFT_SPEC.md invariate. Nessuna modifica a backend, DB reale/schema, risorse, dipendenze, script o workflow; nessun merge o ZIP finale.
