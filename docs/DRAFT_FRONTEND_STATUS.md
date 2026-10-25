# Draft - incrementi frontend

Data: 25 ottobre 2026. Solo ramo draft, PR 18.

## Verifiche note

Log negativo dell autore alle 03:47: npm run check con 25 errori e 0 warning in ordine/modal. Rename state -> sessionState in a854b28c9ea68444b216a45964925cad03fa6dd7; nessun nuovo esito positivo attestato. $state, store.state e port state invariati.

Nessuna installazione, formattazione, esecuzione locale check/lint/test/build o consultazione/attesa CI per questo incremento. I test sono predisposti, non dichiarati superati. Ok/prosegui non e un risultato di test. Le verifiche backend precedenti non attestano il frontend.

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
10. Generazione auth e registro: 48d59990c538db6e4c779e557126834be722e90b.
11. Host nel layout, coda stabile e sospensione dei modal: incremento corrente.

## Perimetro corrente

Il layout crea un registro per propria istanza e lo espone con il contesto Svelte, non tramite singleton. DraftHost avvolge il contenuto esistente, collega sessionKey/utente/ruolo e richiede una lettura REST iniziale per generazione autenticata. La costruzione non fa rete e le effect client non vengono eseguite in SSR. Il provider e registrato dal layout prima di inizializzare i discendenti.

Il codice monta il flusso delle preparazioni recuperate; questo non e un collaudo del montaggio. Il pulsante Nuova Gara resta sul percorso precedente, non ancora collegato al registro. La connessione SSE condivisa del layout resta invariata e il draft non e ancora sottoscritto: niente notifiche live draft, apertura da eventi, recupero alla riconnessione o chiusura remota attestati. Questi collegamenti costituiscono il prossimo incremento.

File undicesimo: nuovi draft-host-context.ts, draft-host-view.ts, draft-host-view.spec.ts, draft-host-focus.ts e components/draft-host.svelte sotto frontend/src/lib; aggiornati frontend/src/routes/+layout.svelte e questo documento. Nessuna modifica al modal condiviso o alle regole server.

## Coda, modal e lifecycle

Politica approvata in conversazione: mantenere il flusso gia aperto, accodare le altre preparazioni e sospendere i modal sottostanti senza confermarli o considerarli chiusi. La coda e per identita di store, mantiene l ordine locale di ingresso anche se il server riordina l elenco e non cambia per nuove versioni. Al recupero iniziale usa l ordine dell elenco autorizzato, senza attribuirgli significato di gioco. I turni restano esclusivamente server. Termini, dismissioni, rimozioni o perdita di accesso liberano la coda.

Il gestore puo vedere attendance/order; i partecipanti vengono mostrati solo in picking/decks con propri presenti. READY non e una condizione di conclusione e non fa avanzare la coda. Il flusso attivo e keyed per store, non per oggetto dell elenco o versione. Le istanze accodate non hanno un secondo proprietario DraftFlow montato.

Il contenuto della pagina, header e modal gia aperti resta montato dentro un contenitore inert e aria-hidden durante il flusso. Escape e intercettato in cattura prima dei listener window dei modal sospesi, senza inviare cancel. I click nel draft non chiudono il menu admin sottostante. Cambi pagina e autenticazione conservano i loro comportamenti precedenti; il draft non forza navigazioni, non conferma altri dialoghi e non annulla HTTP gia partiti.

Il modulo focus e un action client con focus iniziale, contenimento di Tab/focus e ripristino differito solo se il vecchio controllo e connesso, non inert e nessun altro controllo ha preso il focus. Il ripristino non deve sottrarre focus al draft successivo. Non e un collaudo browser di focus, touch, screen reader o popup renderizzati fuori dal contenitore.

Una pre-effect acquisisce gli esiti reali nel registro prima del cleanup DOM di DraftFlow, che dismette lo store. La rimozione REST conserva a sua volta eventuali esiti gia noti. takeCompletions consuma una sola volta per ID nel contesto corrente. Il contenitore mostra l ultimo gruppo di esiti quando non ci sono flussi bloccanti, senza cronologia persistente o redirect automatico. Assenza da elenco non diventa gara creata o annullamento.

Errori del registro o degli store hanno un recupero manuale Rileggi preparazioni, non un reinvio dei POST. Le pagine non vengono bloccate da un semplice caricamento iniziale senza flusso. Perdita di contesto nasconde subito dati e notifiche precedenti e dismette i controller. 401/403 svuotano i dati privati; il contenitore non trasforma autonomamente un 403 di risorsa in logout. L auth.expired dello stream esistente mantiene il comportamento precedente.

## Auth e registro conservati

AuthStore espone sessionEpoch, authenticating e sessionKey. Chiave null prima di ready, durante init/login/register/logout o senza utente; generazione diversa anche al nuovo accesso dello stesso account e ruolo nella chiave. Solo metadati locali, nessun token, persistenza o URL. Non e una soluzione generale alle gare fra richieste di autenticazione/cookie. Endpoint, payload, ruoli e autorizzazioni server non cambiano.

Il registro e a istanze, confronta chiave/utente/ruolo e scarta risposte tardive. refresh legge l elenco autorizzato, valida e riusa i DTO tramite un seme consumato una volta dal loader, evitando GET duplicate. Gli store restano gli stessi per ID. Non riconcilia durante operazioni principali, non applica versioni inferiori o resuscita controller conclusi da un elenco precedente. I dati corrotti non diventano vuoto. Il recupero multi-store non e atomico; una rilettura scartata richiede altra richiesta esplicita. Nessun polling o retry automatico.

open resta esplicito per admin/giudice, riusa preparazioni note, blocca doppi invii e non crea Race. Rete, errori server o DTO inutilizzabili impongono recupero prima di altro POST; anche 409 impone recupero senza essere dichiarato commit incerto. recoveryChampionshipIds indica verifiche necessarie, non gare create. Un registro bloccato richiede refresh riuscito prima di altre aperture. Dispose non annulla scritture gia inviate.

Il busy del registro copre le proprie richieste, non sostituisce i blocchi dei dettagli mazzo. Le versioni e i controlli dei coordinatori restano necessari. Coordinamento delle notifiche SSE con letture/mutazioni e ripresa dopo disconnessione non ancora collegati.

## Composizione e regole conservate

DraftFlow conserva contesto e figli per store/ID, non per versione. Scelta iniziale locale: attendance riparte dalla scelta dopo reload senza azzerare presenze server; picking/decks seguono il DTO. Nessuna persistenza locale. Il caricamento iniziale del mazzo resta del componente mazzi, non viene duplicato dall host.

DraftModal usa externalBusy del mazzo per bloccare X, conferma cancel e rilettura principale durante GET. Conferme legate a store/ID/versione diventano inutilizzabili se cambia lo stato. I gestori ricontrollano i blocchi, non solo disabled. Il modal condiviso conserva i default, X a destra; draft a sinistra, Escape/sfondo non chiudono. Creatore pronto coi propri presenti deve prima tornare non Pronto; insieme vuoto non blocca per vacuita.

Controller serializzato, API autenticata, versione server e risultati obsoleti scartati. 409 blocca; rete/500/DTO inutilizzabile dopo comando sono incerti; 422 consente correzione; 401/403 eliminano snapshot; lettura valida libera il blocco. 404 non prova annullo o creazione. READY intermedio conserva preparazione, race_id conclude, cancel conclude separatamente.

Presenti/Assenti per pilota non ottimistici e limite backend 1-12. Il server decide order/decks se pool insufficiente. Ordine server, Prima gara centrato, drag/Su-Giu con baseline e scarto esplicito. order e start restano due HTTP senza rollback inventato. Gara gia disputata usa il comando dedicato senza controlli mazzi/READY.

Scelta per proprietario del turno, non per can_manage; slot_id distingue copie, conferma versionata senza rimozione ottimistica, zoom locale e preview consentita soltanto al turno utilizzabile. Ultima scelta porta a decks e non crea Race. Nessuna propagazione live ancora attestata.

Mazzi soltanto propri presenti, DTO/versioni/READY coerenti, GET mirata dopo POST riuscito. GET fallita non e rollback; dati precedenti readonly e recupero esplicito. Pronto con 15 esatte dopo la prima gara, massimo 15 sempre. Non Pronto puo revocare senza vecchio DTO/conteggio ma con contesto utilizzabile e coordinatore non bloccato, poi GET. Tutti i propri presenti pronti nasconde editing e lascia non Pronto; nessuna gara dedotta da quel conteggio. CardEntry/CardTile/totalCopies riusati, nessuna nuova risorsa o conversione.

## Test predisposti e seguito

Nuovi test helper: coda stabile anche con elenco riordinato, identita conservate, visibilita per fase e proprietario dei presenti, READY non terminale, passaggio dopo conclusione reale, rimozioni/dismissioni, duplicati di identita ed Escape simulato. Non sono test DOM di focus/action, effect client, SSR del layout, navigazione, sospensione di dialoghi reali o SSE. Restano i test predisposti degli incrementi precedenti, non dichiarati superati. Nessuna concorrenza DB o sessione browser reale verificata.

Comandi previsti in frontend: npm run check, npm run lint, npm test, npm run build. Nessuno eseguito localmente; nessun risultato CI letto o atteso. Formattazione e accessibilita non dichiarate validate. I precedenti 503/400 GitHub erano letture fallite e poi recuperate, non test applicativi.

Push diretto sul solo draft degli incrementi approvati, niente checkpoint nei commenti o nuovi workflow. CI controllata/attesa soltanto su indicazione dell autore. Nessun merge. Questo documento aggiorna lo stato tecnico; docs/DRAFT_SPEC.md conserva le regole. Setup, script, database, risorse, dipendenze e lockfile invariati. Nessuna migrazione, nuovo endpoint o accesso al database reale.

Restano Nuova Gara, collegamento draft allo stream SSE condiviso e alla riconnessione, coordinamento aggiornamenti/comandi e collaudo browser end-to-end, focus/accessibilita e verifica completa.
