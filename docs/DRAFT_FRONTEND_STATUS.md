# Draft - incrementi frontend

Data: 25 ottobre 2026. Ramo: draft. PR: 18.

## Stato corrente

1. Contratti, validatori, client API e test predisposti: commit 8d6f7cd62ef5058e0123e4acae5245bd62cd130a.
2. Controller della sessione e test predisposti: commit a243cc0f848c95b68c92f03d9923f83c7462464f.
3. Store reattivo e test predisposti: commit dd9c011f1b9dd6a6aadd68c69b9e25cecd8b43ea.
4. Contenitore modal, politica di annullamento e opzioni del modal condiviso: commit 06afc3a44edb4619fb6dd1d0dd19ecbfbcfce64f.
5. Scelta iniziale Draft/Gara gia disputata, Presenti/Assenti, helper di vista, test unitari e test SSR predisposti: incremento corrente.

I componenti non sono ancora montati nell applicazione. Nuova gara, layout, autenticazione e SSE non sono collegati. Ordine, scelta carte, mazzi e READY non hanno ancora le rispettive schermate. Il flusso visuale completo non e disponibile.

File dei primi incrementi: frontend/src/lib/draft-types.ts, draft-validation.ts, draft-api.ts e relativi spec; draft-session.ts e relativo spec; stores/draft.svelte.ts e draft-store.spec.ts; components/modal.svelte, draft-close-policy.ts e relativo spec, components/draft-modal.svelte. Il quinto aggiunge components/draft-start.svelte, components/draft-attendance.svelte, draft-attendance-view.ts, draft-attendance-view.spec.ts e draft-attendance-ui.spec.ts. CardEntry e api.ts sono riusati senza modifiche.

## Contratti e trasporto

DTO da backend/app/schemas/draft.py e DraftCardSlot. Copie identiche distinte tramite slot_id. Validatori di forma, tipi, interi sicuri, nullable espliciti e ID duplicati; output indipendenti con soli campi pubblici. Non riproducono il motore, non autorizzano scritture e non richiedono 15 copie nel lettore del mazzo.

fetchDrafts, openDraft, fetchDraft e fetchDraftDeck leggono contesti autorizzati. sendDraftCommand usa i comandi versionati previsti dal backend con soli campi ammessi. Contesti confrontati quando il DTO contiene gli ID. Nessun retry, polling o rilettura implicita dopo scrittura. ApiError condiviso; rete interrotta o risposta POST inutilizzabile non provano rollback.

## Controller e store

Nessuna richiesta alla costruzione. refresh e command sono espliciti e serializzati dal controller, senza seconda coda nello store. Versione presa dallo snapshot server, non dal chiamante. Risposte obsolete o di contesti invalidati scartate; getState/state restituiscono copie. Draft e campionato non possono cambiare, ne la versione regredire.

getContext deve comprendere generazione autenticata e contesto, cambiando anche dopo logout/login dello stesso utente. Il chiamante deve integrare syncContext/dispose a cambio utente, ruolo, contesto e smontaggio. Non ci sono listener auth/SSE e AuthStore non viene modificato. Il solo user_id non basta. dispose e definitivo e non annulla richieste HTTP gia inviate o loro possibili effetti server.

409 blocca e conserva lo snapshot non aggiornato. Rete, 500 e risposte inutilizzabili durante comando sono esiti incerti. 422 permette correzione manuale senza reinvio automatico. 401/403 rimuovono lo snapshot. Solo una lettura server utilizzabile libera il blocco; 404 non prova annullamento o creazione gara. READY intermedio conserva preparazione; race_id conclude come gara creata, cancel riuscito conclude separatamente. Nessuna operazione dopo conclusione/dispose.

DraftStore e a istanze e usa $state.raw. Aggiorna la vista all avvio e nel finally; busy/blocked non sono permessi. syncContext va chiamato fuori dai getter di rendering. Il futuro host deve completare autenticazione e lifecycle.

## Modal e annullamento

Modal condiviso: X predefinita visibile, a destra e non disabilitata. showClose/closeDisabled/closePosition controllano solo la X; closeOnOutside governa Escape e sfondo. confirm-dialog.svelte e modal-close.ts invariati.

DraftModal usa X a sinistra e closeOnOutside falso. X solo al creatore non completamente READY con i propri presenti, come cancel_preparation; insieme vuoto non blocca per vacuita e un solo proprio pronto non basta se ne sono presenti altri. Disabilitata durante richieste, blocchi e conferma.

La X propone annullare la gara? senza scrivere. Conferma legata a istanza store, ID e versione, ricontrollata al clic e invalidata da cambiamenti. Non annullare non scrive. Contenuti sottostanti montati ma nascosti/inert durante conferma per conservare stato locale. Nessuna chiusura anticipata durante cancel; errore non equivale a ripristino riuscito. Gli esiti terminali o dispose nascondono il contenitore.

Rileggi dal server e esplicito. Le future bozze locali richiederanno protezione prima di eventuali riletture. Inert non sostituisce guardie server/controller. Non e un host globale: focus, tastiera, stacking, navigazione e lifecycle non sono dichiarati completi o collaudati.

## Scelta iniziale e presenze

DraftStart richiede uno store gia caricato. Draft chiama solo ondraft del futuro padre per cambiare schermata locale: non chiama start, non estrae carte e non apre preparazioni. Il padre dovra implementare questo passaggio. Gara gia disputata invia already-disputed nella fase attendance dal creatore e attende race_id prima della conclusione. Non controlla mazzi o READY e non inserisce risultati.

DraftAttendance deriva Presenti sopra Assenti, preservando l ordine ricevuto all interno dei gruppi e contando i piloti. Non deduplica nomi e non raggruppa per account. Escludi/Includi ricontrollano pilota e stato corrente e inviano attendance: nessuno spostamento ottimistico prima della risposta server.

Avanti e in basso a destra e invia attendance/confirm. L indicatore usa il limite esistente backend di 1-12 presenti; e possibile correggere la selezione quando zero o oltre limite. Il server mantiene i controlli su iscrizioni, mazzi nelle gare successive e pool; sceglie ordine o direttamente decks e non crea Race alla conferma presenze. Nessun calcolo pool client o salto di fase inventato.

I comandi sono disabilitati durante operazioni, blocchi, fase diversa o assenza di gestione. I gestori ricontrollano il contesto al clic. Queste sono schermate componibili, non il router/host del flusso: la selezione iniziale locale non viene ancora persistita dal frontend e il recupero globale resta da integrare. Errori e rilettura sono gestiti dal contenitore DraftModal quando verra montato.

## Verifiche

Test predisposti, non eseguiti localmente; type-check, lint, Vitest e build non dichiarati superati. Nessun nuovo risultato CI letto o atteso. Le verifiche backend precedenti non attestano questi incrementi frontend.

Test parser: forma, non coerenza di gioco completa. Controller/store: trasporti simulati e classi compilate in Node, non browser o concorrenza DB reale. Politica chiusura: READY multipilota e proposte obsolete, non clic/focus. Quinto incremento: helper puro e rendering server con svelte/server, senza attivare eventi. Non sono prove interattive di Escludi/Includi, Avanti, creazione gara, aggiornamenti DOM o integrazione del modal. Le nuove opzioni del modal non hanno ancora verifica browser attestata.

Comandi previsti in frontend: npm run check, npm run lint, npm test, npm run build. Nessuna installazione, formattazione o esecuzione di test dichiarata in questa preparazione. I precedenti errori 503 nelle letture GitHub erano stati risolti ritentando e non erano fallimenti applicativi.

## Metodo e allineamento

Pubblicare direttamente gli incrementi approvati sul solo draft, senza accumularli nei commenti o introdurre workflow. Non controllare/attendere CI autonomamente: decide l autore quando verificarla, intervenire o aspettare. Nessun merge implicito.

Questa nota aggiorna lo stato tecnico corrente; docs/DRAFT_SPEC.md conserva le regole funzionali. Note backend e manifest documentano verifiche precedenti, non nuovi verdi frontend. Setup, script, schema, risorse, dipendenze e lockfile invariati; nessun nuovo scaffold, API backend o migrazione, nessun accesso al database reale.

Restano ordine, scelta carte, mazzi, READY, montaggio in Nuova gara/layout, autenticazione, lifecycle e live, con test di integrazione e collaudo browser separati.
