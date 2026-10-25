# Draft - incrementi frontend

Data: 25 ottobre 2026. Solo ramo draft, PR 18.

## Verifiche note

Log negativo dell autore alle 03:47: npm run check con 25 errori e 0 warning in ordine/modal. Rename state -> sessionState in a854b28c9ea68444b216a45964925cad03fa6dd7; nessun nuovo esito positivo attestato. $state, store.state e port state invariati.

Nessuna installazione, formattazione, esecuzione locale check/lint/test/build o consultazione/attesa CI per questo incremento. Tutti i test sono predisposti, non dichiarati superati. Ok/prosegui non e un risultato di test; verifiche backend precedenti non attestano il frontend.

## Incrementi

1. DTO/client/validatori: 8d6f7cd62ef5058e0123e4acae5245bd62cd130a.
2. Controller: a243cc0f848c95b68c92f03d9923f83c7462464f.
3. Store: dd9c011f1b9dd6a6aadd68c69b9e25cecd8b43ea.
4. Modal/annullamento: 06afc3a44edb4619fb6dd1d0dd19ecbfbcfce64f.
5. Inizio/presenze: 3a17b7cb1aad0923f6f8e02643afde59ed3e0e9b.
6. Ordine: 4996f8baaf16a600a8ddb325f1cb47aa2bbda3b9.
7. Scelta carte: 1c912647c00fec1f134315005b948acd126f398c.
8. Mazzi/READY: 2fedefcb492cfc24eefa747f4a11c8630a0882e7.
9. Composizione: a8b1c050401befc854b9feeb5b1ad71b78e62f8f.
10. Generazione auth locale, registro host e test predisposti: incremento corrente.

DraftFlow compone tutte le schermate ma non e montato nel layout o in Nuova gara. Il registro e predisposto, non collegato all autenticazione o allo stream. Il pulsante Nuova gara usa ancora il percorso precedente fino al successivo incremento. Recupero all avvio, apertura automatica per partecipanti, navigazione e collaudo globale non sono dichiarati funzionanti.

File del decimo: auth.svelte.ts aggiornato, nuovi draft-host.ts, draft-host.spec.ts e auth-generation.spec.ts, sotto frontend/src/lib, oltre a questo documento. Nessuna modifica a layout, pagina campionato, stream, endpoint o backend.

## Generazione autenticata

AuthStore aggiunge sessionEpoch, un contatore interno delle operazioni auth, authenticating e sessionKey. Prima di init, durante init/login/register/logout e senza utente, sessionKey e null. Ogni operazione incrementa la generazione; ID e ruolo fanno parte della chiave. Anche un nuovo accesso dello stesso utente o un cambio ruolo invalidano il contesto precedente.

La chiave e locale e non e un token server: non viene inviata, usata come autorizzazione, persistita o inserita in URL. I metadati sono liberati nei finally. Endpoint, payload, cookie, ruoli, ritorni ed errori dei metodi restano quelli precedenti. Non viene introdotta una soluzione generale alle gare tra risposte di autenticazione o tra cookie: il nuovo perimetro isola i dati draft e sospende il relativo contesto durante le transizioni. Le autorizzazioni restano server.

## Registro host

createDraftHost e a istanze, senza rete, timer, polling o connessioni alla costruzione. Il futuro chiamante deve fornire getContext e collegare sync ai metadati autenticati; null sospende il contesto. Il confronto usa chiave, userId e ruolo. Cambio contesto/dispose elimina gli store, le carte e gli esiti della generazione precedente e invalida risposte tardive. Non annulla HTTP gia inviati o loro possibili effetti.

refresh fa una GET autorizzata dell elenco. DTO validati, duplicati di draft o campionato rifiutati; JSON o dati corrotti non diventano elenco vuoto. Gli store sono conservati per ID quando ancora utilizzabili. I DTO REST gia ricevuti alimentano una lettura iniziale o di recupero tramite il loader dello store, evitando una seconda GET duplicata; le successive riletture individuali usano fetchDraft. Il seme e consumato una volta e rimosso anche se non applicato.

Non si riconcilia mentre uno store principale e occupato, non si applicano versioni inferiori e non si resuscita un controller concluso da un elenco precedente. Una rilettura scartata richiede un nuovo comando esplicito, senza ciclo automatico. Il recupero multi-store non e una transazione atomica: DTO gia applicati possono essere aggiornati anche se una fase successiva di riconciliazione fallisce; la membership e sostituita soltanto alla fine riuscita.

open e esplicito e riservato a admin/giudice. Riusa una preparazione gia registrata per lo stesso campionato, blocca doppi invii e non crea Race. Una risposta di altro campionato non viene applicata. Rete, errori server o risposte inutilizzabili richiedono recupero prima di un altro POST; anche un 409 richiede recupero, ma non viene confuso con prova di commit incerto. recoveryChampionshipIds elenca i campionati da verificare, non una lista di gare create.

Il registro bloccato richiede refresh riuscito prima di altre aperture. 401/403 svuotano i dati e segnalano unauthorized, senza modificare autonomamente AuthStore. Gli esiti finished effettivi dei controller sono conservati una volta per ID nel contesto corrente e consumabili tramite takeCompletions prima di navigare o rimuovere il flusso. Sparizione da GET non viene interpretata come Race creata o annullamento. Il registro non sceglie una destinazione di navigazione.

Il busy del registro riguarda le proprie GET/POST; i blocchi delle operazioni dei singoli flussi restano nei controller e nei coordinatori. La gestione delle letture locali del mazzo, delle code SSE e delle priorita tra piu preparazioni richiede ancora integrazione nel futuro host UI.

## Composizione e regole conservate

DraftFlow mantiene contesto e figli per store/ID, non per versione. Scelta iniziale locale owner/ID: Draft mostra presenze, le altre schermate seguono phase. Un reload in attendance riparte dalla scelta iniziale senza azzerare presenze server; picking/decks seguono il DTO. Niente persistenza locale aggiunta.

Contesto senza GET alla costruzione; Carica preparazione e esplicito. Il caricamento iniziale del dettaglio in decks appartiene al componente mazzi. Cambio store/ID o perdita snapshot elimina i dettagli. Smontare DraftFlow dismette lo store principale: il futuro host deve usare istanze dedicate e acquisire gli esiti prima della dismissione; il registro offre una conservazione aggiuntiva degli esiti effettivi, non li deduce.

DraftModal usa externalBusy del mazzo per bloccare X, conferma cancel e rilettura principale anche durante GET. Default false conserva i chiamanti precedenti. Conferme diventano inutilizzabili se parte una lettura esterna; i gestori ricontrollano, non solo disabled. Il coordinamento globale con navigazione e altri modal resta da completare.

DTO pubblici e copie indipendenti, CardEntry/CardTile/totalCopies riusati, slot_id per copie distinte. Nessuna replica completa del motore. API autenticata condivisa, payload versionati e soli campi previsti. Nessun retry automatico, polling o nuovo stream.

Controller serializzato con versione server e risposte obsolete scartate. Il suo getContext dovra essere collegato alla nuova sessionKey, ma quel collegamento non e ancora montato. 409 blocca; rete/500/DTO inutilizzabile durante comando sono incerti; 422 consente correzione manuale; 401/403 eliminano snapshot; solo lettura valida libera il blocco. 404 non prova creazione/annullo. READY intermedio conserva preparazione, race_id conclude, cancel conclude separatamente.

Modal condiviso mantiene X a destra per default, DraftModal a sinistra con Escape/sfondo disabilitati. Creatore non completamente READY coi propri presenti, insieme vuoto non blocca per vacuita. Conferma annullamento store/ID/versione senza chiusura anticipata o falso ripristino; contenuti montati ma nascosti/inert durante conferma.

Gara gia disputata usa il comando dedicato senza controlli mazzi/READY. Presenze per pilota non ottimistiche, limite backend 1-12 e fase successiva decisa dal server. Ordine server, Prima gara centrato, drag/Su-Giu con baseline e scarto esplicito. order e poi start sono due HTTP, senza rollback inventato se il secondo fallisce.

Scelta carte per proprietario del turno, non per can_manage; copie distinte, verde/rosso, zoom locale e preview consentita solo al turno utilizzabile, alone da DTO server. Choice confermata e versionata senza rimozione ottimistica; ultima scelta passa a decks senza creare Race. Nessuna propagazione live ancora attestata.

Mazzi solo propri presenti, dati con versioni/READY coerenti, una copia per POST e GET mirata dopo successo. GET fallita dopo POST non e rollback; errore conserva blocco e dati precedenti readonly, 401/403 li elimina. Pronto con 15 esatte dopo la prima gara e massimo 15 sempre. Non Pronto puo revocare senza vecchio DTO/conteggio, ma richiede contesto utilizzabile e coordinatore non bloccato, poi GET. READY completo solo tutti i propri presenti, pulsante unico per selezionato o primo proprio, scala 0.95-1.05 e riduzione animazione. Nessuna gara dedotta dal conteggio.

## Test predisposti e seguito

Nuovi test: generazione auth, transizioni ed errori; registro senza rete iniziale, riuso store, recupero senza GET duplicate, aperture incerte, risposte tardive, stesso account con nuova chiave, ruolo player, dati corrotti, store occupati, conclusioni uniche e 401/dispose. Trasporti simulati, non sessioni/cookie browser reali o concorrenza DB. I test precedenti di helper/SSR non attestano clic, focus, touch, effetti client o end-to-end.

Non attestati check/lint/Vitest/build per questo incremento o un nuovo esito del fix precedente. Comandi previsti in frontend: npm run check, npm run lint, npm test, npm run build; nessuno eseguito localmente. I vecchi 503 e il 400 sulla directory dinamica erano errori di lettura GitHub risolti ritentando o leggendo il file diretto, non test applicativi.

Push diretto degli incrementi approvati sul solo draft; niente commenti-checkpoint o nuovi workflow. CI controllata/attesa soltanto su indicazione dell autore. Nessun merge implicito. Questo documento aggiorna lo stato tecnico, docs/DRAFT_SPEC.md conserva le regole. Setup, script, schema, risorse, dipendenze e lockfile invariati; nessun nuovo scaffold, endpoint, migrazione o accesso al database reale.

Restano componente host e layout, collegamento Nuova gara, integrazione auth/SSE/lifecycle, priorita dei modal, navigazione, accessibilita/focus e collaudo browser.
