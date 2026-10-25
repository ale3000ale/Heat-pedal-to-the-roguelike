# Draft - incrementi frontend

25 ottobre 2026. Solo Heat-pedal-to-the-roguelike, ramo draft, PR 18.

## Verifiche documentate

Ultimo log npm test fornito alle 04:54: 594 superati e 2 falliti su 596 test; 71 file superati e 2 falliti su 73, exit code 1, Vitest 4.1.12. SHA/run ID non indicati. Fix SSR in fc71aa6ce50501f8c9b18e8a9ecacf90b2b004fb: attributi disabled distinti dalle classi e ordine incompleto distinto da DTO duplicato rifiutato. Il successivo via libera non e un nuovo esito positivo.

Nessuna esecuzione locale o consultazione/attesa CI di check, lint, test o build per questo incremento. Nessuna installazione o formattazione attestata. I test nuovi sono predisposti, non dichiarati superati. Il vecchio log check con 25 errori/0 warning e il rename a854b28c9ea68444b216a45964925cad03fa6dd7 non hanno qui un nuovo risultato check documentato.

## Avanzamento

Incrementi 1-8: DTO/client, controller, store, modal, presenze, ordine, scelta e mazzi. Composizione: a8b1c050401befc854b9feeb5b1ad71b78e62f8f. Auth/registro: 48d59990c538db6e4c779e557126834be722e90b. Host/layout: 2739251d889e821e39a1a407eef56232a95710ba. SSE condiviso: e8daa23d8de734abfca9b72cddf9779e190111b0. Modulo apertura e test: 131612d667d132c23f9093ae9cec1d200fc33e30. Incremento corrente: collegamento pagina Nuova Gara e stato.

I precedenti tentativi di pubblicazione dei quattro file sono stati respinti dal controllo di approvazione e non hanno creato commit. Dopo suddivisione e stato pubblicato soltanto il modulo con test; questo secondo commit contiene pagina e documento. Gli errori di approvazione non sono test applicativi e non provano problemi del codice.

## Nuova Gara

La pagina recupera getDraftHost durante l inizializzazione, non nel clic. createRace delega a openChampionshipDraft e host.open: POST /championships/{id}/draft, non POST /races. Il registro e quello del layout. Il modal viene mostrato dalla sottoscrizione dell host, senza istanza locale duplicata o navigazione automatica.

Guardie locali: ID, sessione, permessi, campionato chiuso e gara non conclusa. Il backend resta autorevole. Registro occupato non genera secondo invio; registro bloccato richiede recupero. Il pulsante riflette busy locale/globale, sessione e blocco. Gara non conclusa conserva il messaggio precedente. Nessun controllo preliminare locale dei mazzi aggiunto al percorso Gara gia disputata.

Dopo await, errori e busy della pagina vengono aggiornati solo se coincidono coda campionato, parametro e generazione autenticata catturati. Il lifecycle live della pagina dipende da sessionKey, cosi un nuovo accesso dello stesso account pulisce i dati precedenti. Risposte tardive non vengono applicate al nuovo contesto; HTTP gia inviati possono avere avuto effetti server.

Non si rilegge l elenco gare alla sola apertura della preparazione: nessuna Race e stata creata. race.started e i consumer esistenti aggiornano l elenco quando la gara esiste davvero. Nessun fallback al vecchio endpoint o retry automatico dopo risposta incerta.

File del secondo commit: frontend/src/routes/championships/[id]/+page.svelte e questo documento. Modulo/test del primo commit non modificati. Iscrizioni, sponsor, classifica e dialoghi conservati salvo il collegamento della generazione autenticata al lifecycle della pagina.

## Live, coda e garanzie conservate

Un solo stream SSE del layout. draft.changed contiene solo preparation_id; parser senza carte o snapshot. REST su avvio, draft.changed e resync; segnali accorpati durante GET/POST e busy dettagli. Generazioni precedenti scartate, nessun nuovo polling o connessione. Errori senza nuove invalidazioni non creano cicli. Stream indisponibile: recupero manuale.

Dettagli caricati ma obsoleti: GET mirata dopo recupero principale, senza duplicare il primo caricamento. Un tentativo per coordinatore/pilota/versione, poi Rileggi mazzo manuale; nuova versione puo richiedere nuova lettura, mai reinvio di POST. Recupero multi-store non atomico, versioni e blocchi restano necessari.

Coda stabile per identita, un solo DraftFlow montato, modal sottostanti montati ma inert/aria-hidden. Escape non chiude, X creatore con conferma e vincolo READY. Focus/Tab/ripristino non collaudati nel browser. Esiti effettivi acquisiti prima del cleanup, consumati una volta; sparizione REST non etichettata arbitrariamente come annullamento o gara creata.

Presenze per pilota, ordine e turni server, copie distinte per slot_id, scelta confermata, pool insufficiente verso decks e nessuna gara all ultima scelta. READY per propri presenti, 15 esatte dopo la prima gara e massimo 15 sempre; non Pronto prima della X del creatore pronto. GET fallita dopo POST non significa rollback. Regole complete in docs/DRAFT_SPEC.md, non modificate qui.

## Verifiche successive

Test del modulo predisposti con trasporto simulato: endpoint draft/riuso store, guardie senza rete, doppio invio, nessun fallback dopo 500 e risposta tardiva. Non sono clic sulla pagina, cambi rotta DOM, focus, browser multipli, cookie o concorrenza SQLite.

Comandi da verificare: npm run check, npm run lint, npm test, npm run build. Nessun nuovo esito attestato. Collegamento end-to-end nel codice, non dichiarato collaudato o pronto al rilascio.

Backend, schema, DB reale, risorse, dipendenze, lockfile, script e workflow invariati. Nessun merge, migrazione o ZIP finale. Seguono verifiche complete e collaudo multi-browser di apertura, turni, anteprima, mazzi/READY, annullamento, riconnessione/sessioni, poi riallineamento generale dei documenti alla consegna verificata.
