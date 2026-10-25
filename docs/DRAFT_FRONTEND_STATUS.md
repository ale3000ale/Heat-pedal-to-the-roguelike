# Draft - incrementi frontend

Data: 25 ottobre 2026. Solo ramo draft, PR 18.

## Verifiche documentate

Log npm test fornito dall autore alle 04:54: Vitest v4.1.12, 71 file superati e 2 falliti su 73; 594 test superati e 2 falliti su 596, exit code 1, timestamp runner 03:54:23. SHA/run ID non indicati. Non attribuire questi risultati a un commit specifico o a verifiche successive.

Fix dei test SSR pubblicato in fc71aa6ce50501f8c9b18e8a9ecacf90b2b004fb: attributo disabled distinto dalle classi CSS e ordine incompleto distinto da DTO duplicato rifiutato. Alle 04:59 l autore ha autorizzato a continuare: non e un nuovo log positivo. Nessun nuovo npm test, check, lint o build eseguito localmente o letto in CI per questo incremento. Test nuovi predisposti, non dichiarati superati. Nessuna installazione o formattazione locale attestata.

Il precedente log delle 03:47 riportava check con 25 errori e 0 warning; rename state -> sessionState in a854b28c9ea68444b216a45964925cad03fa6dd7, senza un nuovo esito check qui documentato. Il log npm test non prova check/lint/build o collaudo browser.

## Incrementi

1. DTO/client/validatori: 8d6f7cd62ef5058e0123e4acae5245bd62cd130a.
2. Controller: a243cc0f848c95b68c92f03d9923f83c7462464f.
3. Store: dd9c011f1b9dd6a6aadd68c69b9e25cecd8b43ea.
4. Modal: 06afc3a44edb4619fb6dd1d0dd19ecbfbcfce64f.
5. Inizio/presenze: 3a17b7cb1aad0923f6f8e02643afde59ed3e0e9b.
6. Ordine: 4996f8baaf16a600a8ddb325f1cb47aa2bbda3b9.
7. Scelta carte: 1c912647c00fec1f134315005b948acd126f398c.
8. Mazzi: 2fedefcb492cfc24eefa747f4a11c8630a0882e7.
9. Composizione: a8b1c050401befc854b9feeb5b1ad71b78e62f8f.
10. Auth/registro: 48d59990c538db6e4c779e557126834be722e90b.
11. Host/layout: 2739251d889e821e39a1a407eef56232a95710ba.
12. Collegamento SSE condiviso e riconciliazione dettagli: incremento corrente.

## Perimetro del collegamento live

Il backend esistente signal_draft_changed pubblica draft.changed per destinatario, con payload del solo preparation_id e pilot_id nullo. In attendance/order riceve il creatore; in picking/decks anche i proprietari presenti, una volta per account. I segnali precedono la rimozione della preparazione e condividono la transazione. Nessuna modifica backend in questo incremento.

DOMAIN_EVENTS include draft.changed: EventClient registra automaticamente il listener nella connessione gia esistente. Il parser accetta soltanto un preparation_id positivo senza campi aggiuntivi o dettagli pilota. Dati malformati passano al meccanismo resync gia esistente, non diventano snapshot autorevoli. Non vengono trasferite carte via SSE.

DraftHost avvia startDraftLive per generazione autenticata. Il collegamento sottoscrive il singleton EventClient, non chiama connect, non crea EventSource e non introduce timer o polling. REST resta il canale dello stato autorizzato e dei comandi. Un recupero iniziale e ulteriori letture su draft.changed/resync; eventi degli altri domini non avviano questa coda.

La riconnessione nativa genera resync reconnected nel client condiviso; una nuova connessione senza cursore o con cursore non recuperabile riceve resync dal backend. Il collegamento rilegge l elenco, senza presumere di aver ricevuto ogni evento. Lo stream non disponibile lascia il recupero manuale: nessun nuovo fallback polling draft.

Il pulsante Nuova Gara resta sul precedente percorso: collegarlo al registro e il prossimo commit separato. Non dichiarare completo il flusso utente o collaudata la sincronizzazione tra browser solo perche il codice live e collegato.

## Accodamento, busy e mazzi

Un solo recupero principale per volta; nuove notifiche durante la lettura richiedono un altro giro accorpato. Busy di registro/store e dettagli mazzo rinvia la lettura conservando l invalidazione. DraftFlow espone facoltativamente identita del coordinatore e busy, senza copie di carte; i vecchi chiamanti restano validi. L host richiama wake quando cambia busy, senza polling e senza inviare POST. Errori di rete non creano un ciclo di retry senza nuove invalidazioni o richiesta manuale.

Il registro applica direttamente le GET, quindi non e usato come load pura del coalescer generico. I suoi controlli su busy, versioni e contesto restano autorevoli; il recupero multi-store non e atomico. Un risultato gia applicato puo precedere un altro recupero richiesto da una notifica successiva. Non viene dichiarato uno snapshot transazionale tra tutte le preparazioni.

Dopo un recupero riuscito, l host attende tick per aggiornare i figli e verifica il dettaglio del flusso attivo. Un dettaglio gia caricato ma obsoleto riceve una GET mirata tramite il coordinatore esistente, senza ricrearlo. Non duplica il caricamento iniziale di DraftDecks. Un tentativo per coordinatore/pilota/versione; dopo errore non ripete quella stessa versione automaticamente e resta Rileggi mazzo esplicito. Una nuova versione autorevole puo richiedere un nuovo tentativo, mai un reinvio della mutazione.

Cambio generazione disiscrive il vecchio collegamento, svuota i controller tramite il registro e scarta risposte tardive. auth.expired ferma la sottoscrizione; l autenticazione e la connessione restano gestite dal layout esistente. Dispose del collegamento non annulla HTTP o effetti server gia avviati. Nessun nuovo token, cookie o parametro URL.

## Lifecycle e regole conservate

Provider Svelte e registro a istanze per layout. Coda locale stabile per identita di store, flusso gia aperto non sostituito per nuove versioni; altri accodati. Gestore anche in attendance/order, partecipanti solo in picking/decks coi propri presenti. Una sola istanza DraftFlow montata. Turni, permessi e READY per pilota restano server.

Pagina/header/modal sottostanti restano montati ma inert/aria-hidden, Escape bloccato in cattura e click draft esclusi dalla chiusura del menu admin. Focus iniziale/Tab/ripristino dedicati non ancora collaudati nel browser. Nessuna conferma automatica di altri dialoghi o navigazione forzata.

Esiti effettivi acquisiti prima del cleanup DOM e consumati una volta per ID nel contesto corrente. La rimozione da elenco chiude il flusso ma non viene etichettata automaticamente come annullamento o gara creata: il segnale draft.changed non contiene quel risultato. Nessuna gara dedotta da tutti READY. Gli altri consumer esistenti ricevono race.started separatamente.

Auth usa generazione/utente/ruolo locali, non un token o un autorizzazione. Le API controllano permessi e versioni. 409 blocca; rete/500/DTO inutilizzabile dopo comando sono incerti; 422 e correggibile; 401/403 eliminano dati privati. Un 404 non prova l esito. Il registro richiede recupero prima di ritentare aperture incerte e non trasforma un 403 di risorsa in logout.

Presenze non ottimistiche e limite backend 1-12; pool insufficiente passa a decks. Ordine server e bozza con baseline; order/start sono due richieste senza rollback inventato. Gara gia disputata usa il comando dedicato senza READY/controllo mazzi. Scelta per proprietario del turno, slot_id per copie, conferma versionata e anteprima autorizzata. Ultima scelta non crea Race.

Mazzi solo propri presenti, DTO/versioni/READY coerenti, GET dopo POST riuscito senza sottrazioni ottimistiche. GET fallita non e rollback. Pronto con 15 esatte dopo la prima gara e massimo 15 sempre. Non Pronto e disponibile solo col contesto/coordinatore utilizzabili; lettura dopo revoca. Creatore pronto deve revocare prima della X; niente chiusura con Escape/sfondo. Componenti carte e risorse riusati.

## File e verifiche da eseguire

Aggiornati events/event-types.ts, events/event-validation.ts, events/event-validation.spec.ts, components/draft-flow.svelte e components/draft-host.svelte. Nuovi draft-events.spec.ts, draft-live.ts, draft-live.spec.ts, draft-live-deck.ts e draft-live-deck.spec.ts. Documento aggiornato. Tutti sotto frontend/src/lib salvo questo documento. Layout, pulsante campionato, client SSE, coalescer generico e backend invariati.

Test predisposti: protocollo privato e int64, client condiviso, invalidazioni durante GET/busy/POST, nessun doppio POST, resync, cambio contesto, errori senza ciclo, scadenza e dettaglio obsoleto con limite dei tentativi. Trasporti e sorgenti simulati, non due browser, cookie reali o concorrenza DB. Non attestati effect client, focus, touch, timing SSR/hydration o collaudo end-to-end.

Comandi previsti in frontend: npm run check, npm run lint, npm test, npm run build. Nessuno eseguito qui; nessuna CI consultata o attesa. Push diretto sul solo draft, nessun merge o nuovo workflow. docs/DRAFT_SPEC.md conserva le regole. Dipendenze, lockfile, immagini, script e database invariati; nessuna migrazione o accesso al DB reale.

Prossimo passo: collegare Nuova Gara al provider del layout, quindi verifica completa e collaudo multi-browser/reconnessione/modal/mazzi. La documentazione generale del progetto andra riallineata alla consegna verificata; non e dichiarata una release completa o uno ZIP finale.
