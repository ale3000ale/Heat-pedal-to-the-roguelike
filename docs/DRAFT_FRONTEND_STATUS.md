# Draft - incrementi frontend

Data: 25 ottobre 2026. Ramo: draft. PR: 18.

## Stato corrente

Primo incremento: contratti TypeScript, validazione runtime, client API autenticato e test predisposti, commit 8d6f7cd62ef5058e0123e4acae5245bd62cd130a. Il refuso TypeScriptScript e stato corretto nel secondo incremento.

Secondo incremento: controller isolato della sessione e test predisposti per concorrenza, lifecycle ed errori, commit a243cc0f848c95b68c92f03d9923f83c7462464f.

Terzo incremento: store a istanze con rune Svelte sopra il controller e test predisposti, commit dd9c011f1b9dd6a6aadd68c69b9e25cecd8b43ea.

Quarto incremento: contenitore modal draft con conferma di annullamento, politica UI separata e opzioni retrocompatibili del modal condiviso. Il componente riceve uno store e contenuti dal chiamante, ma non e ancora montato nell applicazione. Non contiene le schermate delle fasi e non e collegato a Nuova gara, layout, autenticazione o SSE. Il flusso visuale completo non e disponibile.

File iniziali: frontend/src/lib/draft-types.ts, draft-validation.ts, draft-api.ts, draft-validation.spec.ts, draft-api.spec.ts, draft-session.ts, draft-session.spec.ts, stores/draft.svelte.ts e draft-store.spec.ts. CardEntry e api.ts sono riusati senza modificarli. Quarto incremento: components/modal.svelte aggiornato; nuovi draft-close-policy.ts, draft-close-policy.spec.ts e components/draft-modal.svelte.

## Contratto e limiti dei DTO

I DTO seguono backend/app/schemas/draft.py e DraftCardSlot. Le carte identiche rimangono distinte tramite slot_id. I validatori verificano forma, tipi, interi sicuri, nullable espliciti e ID duplicati e restituiscono copie dei campi pubblici. Non riproducono il motore delle fasi, non decidono permessi server e non impongono 15 copie nel lettore del mazzo.

fetchDrafts, openDraft, fetchDraft e fetchDraftDeck leggono i contesti autorizzati. sendDraftCommand usa attendance, attendance/confirm, order, start, preview, choice, deck/move, ready, already-disputed e cancel con versione e soli campi previsti. Le risposte vengono validate e confrontate con i contesti richiesti quando il DTO contiene gli identificativi.

Nessun retry automatico, polling o rilettura implicita dopo scrittura. ApiError preserva il client condiviso. Errore di rete o risposta POST inutilizzabile non dimostrano rollback.

## Controller della sessione

createDraftSession non avvia richieste. refresh legge solo su chiamata esplicita; command usa la versione dello snapshot server. Durante lettura o scrittura non accoda richieste. getState restituisce copie indipendenti. Il contesto e fissato alla creazione: getContext deve comprendere generazione autenticata e contesto, cambiando anche dopo logout/login dello stesso utente.

Il chiamante deve dismettere la sessione a cambio utente/ruolo/contesto e smontaggio. Il controller ricontrolla la chiave durante consultazioni, operazioni e risposte; non ascolta auth o SSE. Risposte tardive vengono scartate; dispose e definitivo e non annulla HTTP gia inviati. Versione, draft e campionato dello snapshot non possono regredire o cambiare contesto.

409 blocca conservando lo snapshot non aggiornato; rete, 500 o risposte inutilizzabili durante comando sono esiti incerti. 422 permette una correzione manuale senza retry; 401/403 rimuovono lo snapshot. Solo una lettura server utilizzabile libera il blocco; 404 non prova annullamento o creazione gara. READY intermedio conserva la preparazione, race_id conclude come gara creata, cancel riuscito conclude separatamente. Nessun comando o refresh dopo conclusione/dispose.

## Store reattivo

DraftStore e a istanze, non singleton; usa $state.raw. state restituisce copie; busy e blocked sono indicatori tecnici, non permessi. Aggiorna la vista all avvio e nel finally senza seconda coda. Nessuna rete alla costruzione, nessun timer, retry o polling. dispose svuota la vista e risultati tardivi non la riattivano.

syncContext pubblica senza rete le invalidazioni; il futuro host deve chiamarlo a cambio contesto fuori dai getter di rendering, oppure dismettere l istanza. Non ci sono listener auth/SSE. AuthStore espone utente/ruolo, non una generazione autenticata: non viene modificato, e il solo user_id non basta per la chiave di contesto.

## Modal e annullamento

modal.svelte conserva i valori predefiniti: X visibile a destra e non disabilitata. Le nuove opzioni showClose, closeDisabled e closePosition riguardano la X. closeOnOutside continua a governare Escape e sfondo; nascondere o disabilitare la X non cambia implicitamente quei due canali. confirm-dialog.svelte e modal-close.ts non sono modificati.

DraftModal riusa Modal con closeOnOutside falso e X a sinistra. X nascosta ai non creatori e quando tutti i propri piloti presenti sono READY; insieme proprio vuoto non blocca per vacuita. Questa politica segue cancel_preparation: con piu propri presenti, uno solo pronto non basta. X disabilitata senza snapshot utilizzabile, durante operazioni, blocchi o conferma.

La X propone annullare la gara? senza inviare richieste. La conferma cattura istanza dello store, ID e versione e ricontrolla tutto al clic. Una variazione invalida la conferma; Non annullare non scrive. Il contenuto sottostante resta montato, nascosto e inert durante la conferma per non perdere stato locale. Durante invio il contenitore non viene chiuso anticipatamente; si nasconde dopo esito terminale o dismissione dello store. Un errore non chiude il modal e non viene presentato come ripristino riuscito.

I blocchi mostrano Rileggi dal server, azione esplicita. Questo contenitore non gestisce ancora bozze delle schermate successive: la protezione di eventuali modifiche locali prima delle future riletture dovra essere integrata con quelle schermate. Inert impedisce interazioni dei contenuti durante blocchi e operazioni, ma non sostituisce le guardie del controller e del server.

Il componente non e un host globale e non apre da solo modal per i partecipanti. La gestione completa di focus, tastiera, stacking con altri modal, navigazione e lifecycle deve ancora essere verificata e integrata. Non viene dichiarato un focus trap o un collaudo accessibilita completo.

## Verifiche

Test di DTO, API, controller, store e politica di chiusura predisposti, non eseguiti localmente. Type-check, lint, Vitest e build non dichiarati superati; nessun nuovo risultato CI letto o atteso. Risultati backend precedenti non attestano questi incrementi frontend.

I test parser verificano discriminanti, non coerenza di gioco completa. Controller/store usano trasporti simulati e proprieta di classi compilate nell ambiente Node Vitest, non DOM/browser o concorrenza DB reale. I test della politica verificano disponibilita X, READY multipilota, versioni obsolete e delega Escape/sfondo del helper esistente; non provano clic, rendering, focus o funzionamento end-to-end dei nuovi componenti. I nuovi attributi del modal condiviso non hanno ancora una verifica visuale o browser attestata.

Comandi previsti in frontend: npm run check, npm run lint, npm test, npm run build. Nessun comando di installazione, formattazione o test eseguito in questa preparazione. Due precedenti letture GitHub fallite con 503 erano riuscite al tentativo successivo: non erano fallimenti dei test.

## Metodo aggiornato dall autore

Pubblicare direttamente gli incrementi approvati sul solo ramo draft, senza accumularli nei commenti o introdurre altri workflow. Non controllare o attendere la CI autonomamente: l autore comunica quando verificarla, intervenire o aspettare. Nessun merge implicito.

## Allineamento e seguito

Questa nota aggiorna lo stato tecnico: trasporto, controller, store e contenitore modal sono predisposti, ma il flusso non e montato o completo. docs/DRAFT_SPEC.md conserva le regole funzionali. Note backend e manifest documentano le verifiche precedenti, non un nuovo verde frontend.

Le parti generali su setup, script, schema e risorse restano invariate. Nessuna dipendenza, lockfile, scaffold, API backend o migrazione modificata; nessun accesso al database reale. Restano schermate iniziale/presenze/ordine/scelta/mazzi/READY, integrazione Nuova gara, autenticazione/layout/lifecycle e live, con verifiche browser separate.
