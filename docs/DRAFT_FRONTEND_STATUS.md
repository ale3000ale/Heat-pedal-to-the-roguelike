# Draft - incrementi frontend

Data: 25 ottobre 2026. Solo ramo draft, PR 18.

## Verifiche documentate

Log npm test fornito dall autore alle 04:54: Vitest v4.1.12, 73 file, 71 superati e 2 falliti; 596 test, 594 superati e 2 falliti, exit code 1. Timestamp riportato dal runner: 03:54:23. Il messaggio non indica SHA o run ID: non attribuire il risultato a un commit specifico o a esecuzioni successive.

Fallimenti: draft-flow-ui.spec.ts cercava disabled anche nelle classi CSS; draft-order-ui.spec.ts usava un ordine duplicato rifiutato dal validatore e pretendeva il rendering della fase senza snapshot. Gli altri risultati positivi nel log sono evidenza di quella esecuzione, non una suite interamente verde o un collaudo browser.

Correzione corrente limitata ai due file di test e a questo documento: verifica dell attributo disabled dopo esclusione dei valori quotati, regressioni per classi/aria-disabled/data-disabled; casi distinti per non creatore, ordine incompleto con ID unici e DTO duplicato rifiutato. Nessuna modifica a componenti, store, controller, validatori o backend. Non viene indebolita la validazione per far passare il test.

Non e stata eseguita una nuova suite dopo la correzione, ne localmente ne tramite strumenti CI. Nessun check, lint, build o successo del fix dichiarato. Il log npm test non prova gli esiti degli altri comandi. Il precedente log delle 03:47 riportava npm run check con 25 errori e 0 warning; il rename state -> sessionState in a854b28c9ea68444b216a45964925cad03fa6dd7 non ha qui un nuovo esito check attestato. Nessuna installazione o formattazione locale eseguita.

## Incrementi pubblicati

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
11. Host nel layout: 2739251d889e821e39a1a407eef56232a95710ba.

## Perimetro corrente

Layout con registro a istanze, provider Svelte per i discendenti e DraftHost intorno al contenuto esistente. Il contesto usa sessionKey, utente e ruolo. Una lettura REST iniziale per generazione autenticata, nessuna rete alla costruzione o effect client eseguita in SSR. Il codice e montato ma non e dichiarato collaudato nel browser.

Nuova Gara resta sul percorso precedente e non apre ancora il registro. L unica connessione SSE del layout resta invariata: il draft non e ancora sottoscritto. Apertura da eventi, sincronizzazione tra dispositivi, riallineamento alla riconnessione e chiusura remota non sono ancora collegati. L integrazione resta sospesa per correggere prima i due test segnalati.

## Coda, modal e lifecycle

Politica approvata: mantenere il flusso aperto e accodare le altre preparazioni, sospendendo i modal sottostanti senza confermarli o considerarli chiusi. La coda conserva identita e ordine locale di ingresso; nuove versioni o riordini dell elenco non spostano lo store attivo. All avvio usa l ordine REST senza attribuirgli significato di gioco. I turni restano server. Termini, dismissioni, rimozioni o perdita di accesso liberano la coda; READY non e una conclusione.

Gestore visibile anche in attendance/order; partecipanti solo in picking/decks con propri presenti. Un solo DraftFlow montato, keyed per store. Pagina/header/modal sottostanti restano montati ma inert e aria-hidden durante il flusso. Escape e intercettato in cattura; i click draft non chiudono il menu admin sospeso. Nessun comando automatico agli altri dialoghi, nessun annullamento di HTTP gia inviati o redirect introdotto.

Action client dedicata a focus iniziale, Tab, contenimento del focus e ripristino differito solo su controllo connesso/non inert, senza sottrarlo a un altro draft. Non ancora verificata con browser, screen reader, touch o popup esterni al contenitore.

Pre-effect per acquisire gli esiti effettivi prima del cleanup di DraftFlow, che dismette lo store; il registro conserva anche gli esiti noti durante rimozione REST. takeCompletions consuma una volta per ID nel contesto corrente. Notifica dell ultimo gruppo quando non ci sono flussi bloccanti, senza cronologia persistente o navigazione automatica. Assenza da elenco non dimostra gara creata o annullamento.

Errori con recupero manuale Rileggi preparazioni, non reinvio dei POST. Il solo caricamento iniziale non blocca la pagina senza un flusso. Cambio contesto nasconde dati/esiti precedenti e dismette i controller. 401/403 svuotano i dati privati; 403 di risorsa non viene trasformato automaticamente in logout. L auth.expired esistente mantiene il comportamento precedente.

## Auth, registro e regole conservate

sessionEpoch/authenticating/sessionKey sono metadati locali, non token, autorizzazioni o dati persistiti/in URL. Chiave null prima di ready, durante init/login/register/logout o senza utente; nuova generazione anche per lo stesso account, ruolo nella chiave. Non risolve in generale gare fra richieste auth o cookie. Autorizzazione effettiva sempre server.

Registro senza rete iniziale, polling o connessioni proprie, con scarto delle risposte di contesti precedenti. Elenco validato; DTO riusati una volta dal loader senza GET duplicate, poi letture individuali reali. Store conservati per ID. Non riconcilia durante operazioni principali, non applica versioni inferiori o resuscita controller conclusi. Dati corrotti non diventano vuoto. Recupero multi-store non atomico e nessun retry implicito.

open solo esplicito per gestori, riuso preparazioni note e blocco doppi invii. Risposte incerte e 409 impongono recupero prima di un altro POST, senza equiparare conflitto a commit incerto. Un registro bloccato richiede refresh riuscito. Dispose non annulla effetti server. Busy del registro non sostituisce i blocchi dei dettagli mazzo; coordinamento con SSE ancora da collegare.

DraftFlow conserva contesto e bozze per store/ID, non per versione. Attendance riparte dalla scelta locale dopo reload senza azzerare presenze server; picking/decks seguono il DTO. Nessuna persistenza locale; GET iniziale mazzo appartiene al componente mazzi. DraftModal blocca X/cancel/rilettura anche durante busy esterno; conferme store/ID/versione ricontrollate dai gestori.

Modal condiviso con default conservati; draft X a sinistra, Escape/sfondo non chiudono. Creatore pronto coi propri presenti deve tornare non Pronto prima della X; insieme vuoto non blocca per vacuita. Controller serializzato e API versionate: 409 blocca, rete/500/DTO inutilizzabile dopo comando incerti, 422 correggibile, 401/403 eliminano snapshot. Lettura valida libera il blocco; 404 non prova esito. READY intermedio conserva preparazione, race_id conclude e cancel conclude separatamente.

Presenti per pilota, cambi non ottimistici e limite backend 1-12. Pool insufficiente porta a decks, non crea subito Race. Ordine server, Prima gara centrato, riordino con baseline e scarto locale esplicito; order/start sono due HTTP senza rollback fittizio. Gara gia disputata usa comando dedicato senza controlli mazzi/READY.

Scelta per proprietario del turno, copie distinte per slot_id, conferma versionata senza rimozione ottimistica, zoom locale e preview condivisa autorizzata. Ultima scelta passa a decks. Mazzi solo propri presenti, versioni/READY coerenti e GET mirata dopo POST; GET fallita non e rollback. Pronto richiede 15 esatte dopo la prima gara e massimo 15 sempre. Non Pronto revoca con contesto/coordinatore utilizzabili, poi GET. READY completo lascia solo non Pronto, senza dedurre Race dal conteggio. CardEntry/CardTile/totalCopies riusati, nessuna nuova risorsa o conversione.

## Verifiche da ripetere e seguito

Comandi frontend previsti: npm run check, npm run lint, npm test, npm run build. I nuovi casi sono predisposti e non rieseguiti. Test SSR/helper non equivalgono a clic, pointer, effect client, focus DOM, SSE reale, cookie o concorrenza DB.

Push diretto sul solo draft degli incrementi approvati. CI non consultata/attesa automaticamente, nessun workflow o merge aggiunto. Questo documento aggiorna lo stato tecnico, docs/DRAFT_SPEC.md conserva le regole. Script, database, risorse, dipendenze e lockfile invariati; nessun endpoint o migrazione nuova, nessun accesso al DB reale.

Prossimo passo: conferma di una nuova esecuzione dopo il fix, quindi Nuova Gara e integrazione draft nello stream SSE condiviso, riconnessione e coordinamento con i comandi. Restano collaudo browser end-to-end e accessibilita/focus.
