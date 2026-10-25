# Draft - incrementi frontend

Data: 25 ottobre 2026. Solo ramo draft, PR 18.

## Verifiche note e limiti generali

Log negativo fornito dall autore alle 03:47: npm run check con 25 errori e 0 warning nei componenti ordine/modal. Rename della variabile locale state in sessionState pubblicato in a854b28c9ea68444b216a45964925cad03fa6dd7. Runa $state, proprieta store.state e port state invariati. Il fix non e dichiarato verificato: nessun nuovo esito positivo fornito o letto autonomamente.

Nessuna installazione, formattazione, esecuzione locale check/lint/test/build o consultazione/attesa CI per questo incremento. I test sono predisposti, non dichiarati superati. Un ok/prosegui non e trasformato in un risultato di test. Le verifiche backend precedenti non attestano il frontend.

## Incrementi

1. DTO/client/validatori: 8d6f7cd62ef5058e0123e4acae5245bd62cd130a.
2. Controller: a243cc0f848c95b68c92f03d9923f83c7462464f.
3. Store: dd9c011f1b9dd6a6aadd68c69b9e25cecd8b43ea.
4. Modal/annullamento: 06afc3a44edb4619fb6dd1d0dd19ecbfbcfce64f.
5. Scelta iniziale/presenze: 3a17b7cb1aad0923f6f8e02643afde59ed3e0e9b.
6. Ordine/avvio sequenziale: 4996f8baaf16a600a8ddb325f1cb47aa2bbda3b9.
7. Scelta carte/preview: 1c912647c00fec1f134315005b948acd126f398c.
8. Preparazione mazzi/READY con coordinatore e test predisposti: incremento corrente.

Tutti i componenti sono ancora separati dal montaggio dell app: Nuova gara, layout, autenticazione e SSE non collegati. Non viene dichiarato disponibile un flusso end-to-end. Ottavo incremento: draft-deck-view.ts e spec, draft-deck-session.ts e spec, components/draft-decks.svelte, components/draft-ready.svelte, draft-decks-ui.spec.ts, sotto frontend/src/lib, oltre a questo documento.

## Fondazioni

DTO pubblici, slot_id per copie identiche, validatori di forma/tipi/ID/nullable e copie indipendenti, senza replicare l intero motore. API autenticata condivisa e payload versionati con soli campi previsti. CardEntry, CardTile e totalCopies riusati; nessuna conversione carte o nuove risorse.

Controller principale serializza i comandi, usa versione server e scarta risposte obsolete. getContext deve comprendere generazione autenticata e contesto, anche tra accessi dello stesso utente. Il futuro host deve integrare syncContext/dispose a cambi e smontaggio. AuthStore non modificato e solo user_id insufficiente. dispose definitivo, senza annullare HTTP gia inviati o garantire rollback.

409 blocca con snapshot precedente non aggiornato; rete/500/DTO inutilizzabile durante comando sono incerti; 422 consente correzione manuale; 401/403 rimuovono snapshot. Solo lettura valida libera il blocco principale. 404 non prova gara creata o annullamento. READY intermedio conserva preparazione, race_id conclude gara, cancel conclude separatamente. Store a istanze con $state.raw, copie indipendenti, aggiornamento avvio/finally e nessuna seconda coda.

## Modal e fasi precedenti

Modal condiviso mantiene default X visibile a destra e abilitata; nuove opzioni solo per X, closeOnOutside per Escape/sfondo. DraftModal: X a sinistra, Escape/sfondo disabilitati, solo creatore non completamente READY con i propri presenti. Conferma annullamento legata a store/ID/versione, ricontrollata al clic, senza chiusura anticipata o falso ripristino. Contenuti montati ma nascosti/inert durante conferma; rilettura esplicita. confirm-dialog e modal-close invariati.

Scelta iniziale Draft invoca il futuro padre, non start/apertura preparazione. Gara gia disputata attende il comando dedicato e race_id senza controlli mazzi/READY. Presenti sopra Assenti, conteggio per pilota, modifiche non ottimistiche; Avanti conferma presenze e il server sceglie order/decks con vincoli esistenti e limite 1-12.

Ordine soltanto server, senza casualita browser; Prima gara centrato, drag pointer e Su/Giu con bozza/versione/baseline. Bozza incompatibile conservata e bloccata, scarto esplicito senza rete o sblocco. Avanti salva se necessario e poi ricontrolla prima di start. Due HTTP, non una transazione: save puo essere riuscita quando start fallisce. Nessun retry o rollback inventato.

Scelta carte secondo current_pilot_id/my_pilot_ids e registro picks/chosen_by: can_manage non concede il turno. Copie distinte, sezione verde per proprietario e rossa per altri, testo turno e animazione ridotta con prefers-reduced-motion. Zoom locale, preview solo dal proprietario utilizzabile, alone solo dai dati server. Conferma choice legata a store/draft/campionato/versione/turno/slot/nome/percorso. Nessuna rimozione ottimistica; ultima choice passa a decks senza creare Race. La propagazione tra dispositivi resta da integrare via SSE, senza polling o nuovo stream.

## Mazzi e dati autorizzati

La vista incrocia my_pilot_ids con i presenti. Nessun accesso ai mazzi altrui per il solo fatto di essere gestore. Il pilota selezionato resta quello corrente se proprio/presente; al recupero senza selezione viene usato il primo proprio presente. Un creatore senza propri presenti resta in attesa, senza inventare un editor o READY per insieme vuoto.

Il coordinatore riceve store e draftId fissati e non legge alla costruzione. Espone una sottoscrizione Svelte con copie dei dati; DraftDecks riceve esplicitamente sia store sia coordinatore e ne verifica la corrispondenza. Alla prima attivazione client carica una volta il primo proprio presente quando non sono tutti pronti. Errori non azzerano la selezione per avviare retry impliciti. In SSR gli effetti non attivano quel caricamento.

Selezione e rilettura sono esplicite; una selezione diversa puo superare una GET precedente, mai un POST in corso. Risposte tardive vengono scartate tramite generazione. Dopo risposta vengono ricontrollati contesto autenticato, draft/pilota, preparation_version e READY. Modifiche al contesto o al roster invalidano dati; non si mostrano carte al nuovo proprietario. Stesso snapshot e dettaglio non aggiornato non abilitano movimenti o Pronto. Nessuna risposta corrotta o mancante viene presentata come mazzo vuoto valido.

Un clic sposta una copia con deck/move usando il controller principale. Non viene sottratto localmente il mazzo dall inventario, ne applicato un movimento ottimistico. Dopo POST riuscito si esegue una GET mirata del pilota, parte della stessa operazione esplicita: non e retry, polling o rilettura autonoma periodica. Se la GET fallisce, il coordinatore segnala Operazione salvata; lettura mazzo non confermata e blocca nuovi movimenti. false non significa rollback o mancato commit.

Se una versione cambia durante GET il risultato non viene adottato come aggiornato: prima si rilegge la preparazione tramite il contenitore se bloccata, poi il mazzo. Nessun ciclo automatico per inseguire le versioni. Dettagli precedenti possono restare visibili ma sono marcati come non aggiornati e non modificabili; 401/403 eliminano le carte locali. Blocchi locali richiedono lettura valida; non si invia non Pronto da un coordinatore bloccato.

## Pronto e non Pronto

Il conteggio somma copie, non nomi. Pronto richiede esattamente 15 dalle gare successive; prima gara non impone 15 ma conserva il massimo. Con mazzo oltre 15 non si aggiunge e non si conferma, mentre il modello consente rimozioni per correggerlo se lo snapshot e utilizzabile. Le altre regole restano server. Sponsorizzazioni e inventario sponsor non sono esposti.

Un proprio pilota gia pronto non puo modificare carte. Non Pronto non impone conteggio o disponibilita del vecchio DTO mazzo; richiede pero contesto globale utilizzabile e coordinatore non bloccato. Dopo revoca riuscita si rilegge il mazzo per tornare all editing. Dopo Pronto il dettaglio vecchio viene invalidato senza inventare nuove carte. Se la preparazione termina, il controller principale riceve race_id e il coordinatore elimina i propri dati; il suo risultato locale tardivo non prova fallimento della creazione.

READY completo appare solo quando tutti i propri presenti sono pronti e non si e in stato di errore/blocco. Nasconde selettori e inventari e offre un solo pulsante non Pronto, riferito al selezionato o al primo proprio presente. Testo diagonale a scacchi e contornato, animazione da scala 0.95 a 1.05 con rispetto di prefers-reduced-motion. La X e gia nascosta dalla politica READY del contenitore. Durante operazioni il pulsante e disabilitato.

Questa e una schermata confinata al componente, non una prova di blocco globale del sito. Il futuro host dovra coordinare anche le letture locali del mazzo con X, navigazione e altri modal: non si dichiara gia completo quel coordinamento. Errori e rilettura possono richiedere una schermata di recupero anziche mostrare READY come stato certo. Nessuna nuova gara viene inventata dal conteggio client o da tutti pronti: decide il server.

## Test predisposti e seguito

Helper: conteggio, inventario senza doppia sottrazione, proprieta, prima gara/15 copie, READY multipilota, versioni. Coordinatore: selezione, GET tardive, POST/GET distinti, errori, versione e dispose con trasporti simulati. SSR: propri presenti, 15 copie, READY completo/parziale e pulsante unico. Non sono interazioni DOM/browser, test di focus/animazioni, accessibilita completa, concorrenza DB reale o collaudo end-to-end.

Non attestati check, lint, Vitest o build per questo incremento. Comandi previsti in frontend: npm run check, npm run lint, npm test, npm run build; nessuno eseguito localmente. I vecchi 503 GitHub erano errori di lettura risolti ritentando, non test applicativi.

Push diretto degli incrementi approvati sul solo draft; niente accumulo nei commenti o nuovi workflow. La CI e controllata/attesa solo su indicazione dell autore. Nessun merge implicito. Questo documento aggiorna lo stato tecnico, docs/DRAFT_SPEC.md mantiene le regole. Setup, script, schema, risorse, dipendenze e lockfile invariati; nessun nuovo scaffold, API backend, migrazione o accesso al DB reale.

Restano montaggio Nuova gara/layout, autenticazione, lifecycle/live, coordinamento completo delle operazioni e collaudo browser.
