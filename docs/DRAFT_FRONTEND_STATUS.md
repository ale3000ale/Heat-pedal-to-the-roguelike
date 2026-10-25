# Draft - stato dell'integrazione e correzioni

25 ottobre 2026. Solo Heat-pedal-to-the-roguelike, ramo draft, PR 18.

## Segnalazioni UI dell'autore alle 14:36

1. Rendere trascinabile l'intera scheda pilota e sostituire Su/Giu con frecce.
2. Mantenere lo zoom locale durante anteprime/aggiornamenti, senza indicare Anteprima di al proprietario nel proprio turno; preservare anche lo zoom degli utenti in attesa.
3. Evitare salti verticali durante la modifica dei mazzi.

Questo incremento riguarda soltanto il punto 1. I punti 2 e 3 restano aperti, non dichiarati risolti. Nessun cambiamento al backend, al database o alle regole del gioco.

## Primo fix: ordine delle schede

Nuovo frontend/src/lib/draft-order-drag.ts con action per iniziare il gesto dall'intera scheda, escludendo i controlli interni. La cattura del puntatore avviene sull'ol stabile, non sul pulsante/scheda riposizionato. Le posizioni iniziali e la distanza percorsa determinano l'indice senza leggere di nuovo il nodo sotto il puntatore dopo ogni riordino. Soglia minima, compensazione dello scroll del modal e limiti alle posizioni disponibili. Nessuna richiesta durante il trascinamento.

Pointerup conclude senza ripristinare la bozza: lo stato del gesto viene azzerato prima di rilasciare la cattura, cosi lostpointercapture non annulla un drop appena concluso. Pointercancel/perdita imprevista di cattura ripristinano la bozza iniziale del gesto. Frecce ↑/↓ con etichette accessibili restano l'alternativa da tastiera; il vecchio pulsante maniglia e rimosso.

Permessi, versioni e coerenza dell'ordine restano controllati da canEditDraftOrder. La bozza e locale e Avanti continua a salvare order se necessario e poi start, senza retry o rollback inventato. Stato server cambiato conserva una bozza incompatibile ma ne blocca l'invio. Messaggio locale con altezza minima riservata per non inserire una nuova riga al primo movimento.

File: nuovo draft-order-drag.ts e draft-order-drag.spec.ts; aggiornati components/draft-order.svelte e draft-order-ui.spec.ts, tutti sotto frontend/src/lib, oltre a questo documento. Nessuna modifica a modal condiviso, anteprime, focus, mazzi o stream in questo primo fix.

## Evidenze sui problemi ancora aperti

Il componente picking passa il nome dell'anteprima anche al proprietario del turno e lega lo zoom al pilota di turno; questo va distinto dalla conferma versionata della scelta. Non e stata riprodotta nel browser la chiusura immediata segnalata.

La schermata mazzi aggiunge/toglie messaggi di caricamento/verifica e il contenimento del focus usa focus senza preventScroll. Il modal e centrato con altezza variabile. Sono punti da correggere/verificare per la stabilita verticale, non una prova che il problema abbia una sola causa.

## Test e limiti

Predisposti test puri per soglia, direzioni, indice stabile, limiti e geometrie invalide; SSR per schede trascinabili, frecce, assenza della maniglia, permessi e dati incoerenti. Non sono test reali di drag, pointer capture, mouse/touch, scroll o layout browser.

Nessuna installazione, formattazione, esecuzione locale check/lint/test/build o consultazione/attesa CI per questo incremento. Test predisposti, non dichiarati superati. La prova browser resta necessaria anche dopo i controlli automatici.

## Correzioni e integrazione precedenti

Il controllo anticipato delle 15 carte e stato rimosso dalla conferma presenze in 0052c1d4680ebcba8f7afc3690fa9a589927aac1, con regressioni backend predisposte e specifica aggiornata. Il vincolo rimane dopo la modifica ai READY e nel ricontrollo finale. Nessun nuovo esito della patch backend attestato qui.

Nuova Gara usa il registro del layout (modulo 131612d667d132c23f9093ae9cec1d200fc33e30, pagina 16eb2df83e3fcca1239b70a83b8bc07d6720bb29). Host e SSE condiviso conservati; notifiche accorpate e recupero REST, un solo flusso montato e coda stabile. Nessuna gara dedotta da READY o sparizione REST, nessun nuovo polling o redirect.

Ultima verifica CI letta nella conversazione: sul commit 26c5faabd4427f790dbdab0cf367cce7466829c6 frontend, runtime e migrazioni superati, backend ancora in corso a quella lettura. Questi risultati storici non attestano i nuovi fix. Regole complete in docs/DRAFT_SPEC.md, non modificate da questo intervento UI.

## Seguito

Dopo pubblicazione: correzione zoom/anteprima e poi stabilita dei mazzi; controlli frontend completi e collaudo reale degli aggiornamenti SSE, del drag, di focus e scroll. Nessun merge, nuova dipendenza, modifica a schema/risorse/script o ZIP finale. Riallineamento generale dei documenti dopo verifiche effettive.
