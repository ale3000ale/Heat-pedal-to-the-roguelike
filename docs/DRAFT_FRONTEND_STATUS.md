# Draft - incrementi frontend

Data: 25 ottobre 2026. Solo ramo draft, PR 18.

## Verifiche note

Log negativo fornito dall autore alle 03:47: npm run check con 25 errori e 0 warning in ordine/modal. Rename state -> sessionState in a854b28c9ea68444b216a45964925cad03fa6dd7, senza cambiare $state, store.state, port state o regole. Nessun nuovo esito positivo attestato per quel fix.

Nessuna installazione, formattazione o esecuzione locale check/lint/test/build; nessuna consultazione o attesa CI per questo incremento. Tutti i test sono predisposti, non dichiarati superati. Ok/prosegui non diventa un risultato di test. Le verifiche backend precedenti non attestano il frontend.

## Incrementi

1. DTO/client/validatori: 8d6f7cd62ef5058e0123e4acae5245bd62cd130a.
2. Controller: a243cc0f848c95b68c92f03d9923f83c7462464f.
3. Store: dd9c011f1b9dd6a6aadd68c69b9e25cecd8b43ea.
4. Modal/annullamento: 06afc3a44edb4619fb6dd1d0dd19ecbfbcfce64f.
5. Inizio/presenze: 3a17b7cb1aad0923f6f8e02643afde59ed3e0e9b.
6. Ordine: 4996f8baaf16a600a8ddb325f1cb47aa2bbda3b9.
7. Scelta carte: 1c912647c00fec1f134315005b948acd126f398c.
8. Mazzi/READY: 2fedefcb492cfc24eefa747f4a11c8630a0882e7.
9. Composizione delle schermate e blocchi esterni del modal: incremento corrente.

Le schermate sono ora composte da DraftFlow, ma il componente non e montato in layout o Nuova gara. Autenticazione, recupero globale, SSE, navigazione e collaudo end-to-end restano da integrare. Non viene dichiarata una funzionalita completa disponibile agli utenti.

Nuovi draft-flow.ts, draft-flow.spec.ts, components/draft-flow.svelte e draft-flow-ui.spec.ts sotto frontend/src/lib; components/draft-modal.svelte aggiornato con externalBusy facoltativo, default false. Documento aggiornato. Nessuna modifica al modal condiviso, ai servizi backend o agli endpoint.

## Contesto e composizione

DraftFlow riceve uno store principale per una preparazione. Crea senza rete il coordinatore del mazzo se esiste uno snapshot. Il contesto resta associato all identita dello store e ID della preparazione, non alla versione. Una nuova versione non ricrea context o i figli attivi: le bozze locali restano nei rispettivi componenti fino al loro cambio di fase o dismissione. Cambio store/ID sostituisce e dismette i dettagli precedenti; perdita dello snapshot li elimina.

La scelta iniziale e locale e scoping per owner/ID: Draft mostra le presenze senza inviare una transizione inesistente. Le altre schermate seguono phase del server. Dopo ricaricamento completo una preparazione ancora attendance parte dalla scelta iniziale, ma le presenze persistite non vengono azzerate; picking/decks vengono recuperate dalla fase server quando il futuro host carichera il DTO. Nessuna persistenza locale aggiunta per questa scelta iniziale.

Nessuna richiesta alla costruzione del contesto. Senza snapshot, Carica preparazione e esplicito. Il primo caricamento dettagli in decks resta quello del componente mazzi, non una seconda lettura del compositore. Nessun polling, retry automatico o EventSource.

Al cambio owner e allo smontaggio DraftFlow dismette lo store principale oltre ai dettagli. Il chiamante deve quindi fornire un istanza dedicata, non condividere quello store con un altro proprietario UI. I risultati terminali restano nello store finche il flusso e montato; il futuro host dovra acquisirli prima della dismissione se servono alla navigazione. Il compositore non inventa destinazioni o una gara da tutti READY: chiusura solo da finished/disposed e relativi esiti del controller.

## Blocchi del contenitore

DraftModal mantiene il comportamento preesistente senza externalBusy. DraftFlow gli passa busy del coordinatore mazzi anche durante GET. Questo blocca X, ingresso nella conferma di annullamento, invio cancel e rilettura della preparazione. Una conferma non inviata diventa inutilizzabile se parte una operazione esterna. Non annullare resta locale; nessuna cancellazione di HTTP gia inviati.

Il segnale esterno non aggiunge una coda o rende pronto il mazzo. La selezione locale di un altro pilota puo ancora superare una GET nei limiti del coordinatore; carte e comandi mantengono i propri blocchi. I gestori degli eventi ricontrollano i blocchi e non si affidano soltanto agli attributi disabled. Resta da coordinare con il futuro host la navigazione globale, l autenticazione e gli altri modal dell app.

## Contratti e regole conservati

DTO pubblici con copie indipendenti, validazione di forma/tipi/ID/nullable, senza replica completa del motore o nuovi permessi. Client condiviso autenticato, payload versionati e soli campi ammessi. slot_id distingue carte identiche. Nessuna conversione o nuove risorse; CardTile, CardEntry e totalCopies riusati.

Controller serializzato senza rete iniziale, versione server, risposte obsolete scartate. getContext deve includere generazione autenticata anche tra accessi dello stesso utente; user_id da solo non basta. AuthStore non modificato e host futuro responsabile di sync/dispose immediato ai cambi. dispose non annulla HTTP gia inviati o garantisce rollback.

409 conserva snapshot non aggiornato e blocca; rete/500/DTO inutilizzabile durante comando sono incerti; 422 consente correzione manuale; 401/403 eliminano snapshot. Solo lettura valida libera il blocco. 404 non prova creazione/annullo. READY intermedio conserva preparazione, race_id conclude gara, cancel conclude separatamente.

Modal condiviso con default X a destra; DraftModal con X a sinistra ed Escape/sfondo disabilitati. Creatore non completamente READY con i propri presenti; insieme vuoto non blocca per vacuita. Conferma annullamento legata a store/ID/versione, senza chiusura anticipata o falso ripristino, contenuti montati ma nascosti/inert durante conferma.

Gara gia disputata attende il comando dedicato senza controlli mazzi/READY. Presenti sopra Assenti, conteggio per pilota, cambi non ottimistici; il server decide order/decks e applica limite esistente 1-12. Ordine soltanto server, Prima gara centrato, riordino pointer/Su/Giu con bozza/versione/baseline. Bozza incompatibile conservata e bloccata; scarto esplicito senza rete. Avanti salva order se necessario e poi start: due HTTP, nessun rollback fittizio se il secondo fallisce.

Scelta carte per proprietario di current_pilot_id, non per can_manage. Copie distinte e riepilogo con pilota; verde/rosso e animazioni ridotte se richiesto. Zoom locale, preview solo dal proprietario utilizzabile e alone da DTO server. Conferma choice legata a contesto/versione/turno/slot; niente rimozione ottimistica. Ultima scelta passa a decks, non crea Race. Live tra dispositivi non ancora collegato.

## Mazzi e READY

Solo propri presenti, selezionato corrente o primo proprio al recupero. Creatore senza propri presenti in attesa. Coordinatore senza rete iniziale e con sottoscrizioni indipendenti. Alla prima attivazione client in decks un caricamento iniziale del proprio presente se non sono tutti pronti, non ripetuto implicitamente sugli errori.

GET e POST distinti, cambi pilota possono superare GET ma non POST. Contesto, ID, preparation_version e READY ricontrollati; dati non aggiornati non abilitano modifiche. Niente mazzo vuoto inventato o doppia sottrazione dall inventario. Dopo move riuscito una GET mirata, non retry o polling. Se GET fallisce, Operazione salvata; lettura mazzo non confermata: false non significa rollback. Dati precedenti readonly e 401/403 li eliminano; recupero esplicito preparazione/mazzo, senza inseguimento automatico delle versioni.

Conteggio per copie. Pronto con 15 esatte dalle gare successive, alla prima massimo 15. Un gia pronto non modifica carte. Non Pronto non impone il vecchio conteggio/DTO, ma serve contesto utilizzabile e coordinatore non bloccato; segue GET per editing. Dopo Pronto dettaglio invalidato, non inventato. Su race_id il controller conclude e i dettagli vengono eliminati; risultati locali tardivi non provano fallimento della creazione.

READY completo solo con tutti i propri presenti pronti e senza blocchi, non per insieme vuoto; nasconde inventari/selettori e offre solo non Pronto per selezionato o primo proprio. Testo diagonale/contornato/a scacchi, scala 0.95-1.05 e prefers-reduced-motion. Nessuna gara dedotta dal solo conteggio. Il blocco globale del sito non e ancora integrato o collaudato.

## Test predisposti e seguito

Helper flow: scelta locale/fasi server, busy principale/esterno, esiti e creazione/dismissione contesto senza rete. SSR: composizione iniziale/order/picking/decks e attributi disabled del modal, incluso il default e Rileggi dal server. Non sono clic, effetti client, prove di mantenimento istanze attraverso aggiornamenti DOM, focus, touch, navigazione, SSE o end-to-end. Test precedenti di helper/controller/coordinatore usano trasporti simulati, non DB reale concorrente. Nessun test dichiarato eseguito o superato.

Comandi previsti in frontend: npm run check, npm run lint, npm test, npm run build; nessuno eseguito localmente. I vecchi 503 GitHub erano errori di lettura risolti ritentando, non test applicativi.

Push diretto degli incrementi approvati sul solo draft, niente accumulo nei commenti o nuovi workflow. CI controllata/attesa solo su indicazione dell autore. Nessun merge implicito. Questo documento aggiorna lo stato tecnico; docs/DRAFT_SPEC.md conserva le regole. Setup, script, schema, risorse, dipendenze e lockfile invariati; nessun nuovo scaffold, API backend, migrazione o accesso al database reale.

Restano host globale, Nuova gara/layout, autenticazione, lifecycle/live e navigazione completa, focus/accessibilita e collaudo browser.
