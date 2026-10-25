# Draft - incrementi frontend

Data: 25 ottobre 2026. Ramo: draft. PR: 18.

## Correzione dei diagnostici riportati dall autore

Il 25 ottobre 2026 alle 03:47, l autore ha fornito il log di npm run check: svelte-check ha riportato 25 errori e 0 warning in components/draft-order.svelte e components/draft-modal.svelte. Questo e un esito negativo del controllo, non un nuovo verde o un esito dei test Vitest. Il log non e stato recuperato autonomamente dall assistente tramite Actions.

Nei due componenti la variabile locale state interferisce con il riconoscimento di $state, interpretato come accesso automatico a uno store. La correzione corrente rinomina solo quella variabile e i suoi riferimenti in sessionState, lasciando invariati la runa $state, la proprieta store.state e il campo state del port di advanceDraftOrder. Non aggiunge subscribe a DraftSessionState, non modifica il controller e non cambia regole o flussi.

Correzione predisposta dopo lettura dei file correnti. Nessuna installazione, formattazione o esecuzione locale di check/lint/test/build. Il nuovo npm run check e ancora da verificare; non si dichiara che tutti i diagnostici siano gia scomparsi. La lettura o attesa della CI resta a indicazione dell autore.

## Stato corrente

1. Contratti, validatori, client e test predisposti: 8d6f7cd62ef5058e0123e4acae5245bd62cd130a.
2. Controller e test predisposti: a243cc0f848c95b68c92f03d9923f83c7462464f.
3. Store e test predisposti: dd9c011f1b9dd6a6aadd68c69b9e25cecd8b43ea.
4. Modal e politica annullamento: 06afc3a44edb4619fb6dd1d0dd19ecbfbcfce64f.
5. Scelta iniziale e presenze, helper e test predisposti: 3a17b7cb1aad0923f6f8e02643afde59ed3e0e9b.
6. Ordine locale con trascinamento, salvataggio prima di start e test puri/SSR predisposti: 4996f8baaf16a600a8ddb325f1cb47aa2bbda3b9.

Componenti non montati nell applicazione: Nuova gara, layout, autenticazione e SSE non collegati. Mancano schermate di scelta carte, mazzi e READY. Il flusso completo non e disponibile.

File precedenti: draft-types.ts, draft-validation.ts, draft-api.ts e spec; draft-session.ts e spec; stores/draft.svelte.ts e draft-store.spec.ts; components/modal.svelte, draft-close-policy.ts e spec, components/draft-modal.svelte; components/draft-start.svelte, components/draft-attendance.svelte, draft-attendance-view.ts e spec, draft-attendance-ui.spec.ts, tutti sotto frontend/src/lib. Il sesto aggiunge draft-order.ts, draft-order.spec.ts, components/draft-order.svelte e draft-order-ui.spec.ts. CardEntry e api.ts riusati senza modificarli.

## Trasporto e sessione

DTO dai contratti backend pubblici. slot_id distingue copie identiche. Validatori di forma/tipi, interi sicuri, nullable espliciti e ID duplicati, con copie dei campi pubblici. Non replicano l intero motore, non autorizzano scritture e non richiedono 15 copie nel lettore del mazzo.

Client autenticato e comandi versionati con soli campi ammessi, confronti di contesto quando il DTO contiene gli ID. Nessun retry, polling o rilettura implicita dopo POST. ApiError condiviso; rete interrotta o risposta inutilizzabile non provano rollback.

Controller senza rete iniziale. refresh/command espliciti, una operazione alla volta, versione dallo snapshot server. Risposte obsolete o di contesti invalidati scartate; copie indipendenti. Draft/campionato non cambiano e versioni non regrediscono.

getContext deve comprendere generazione autenticata e contesto, cambiando anche al nuovo accesso dello stesso utente. Il chiamante deve integrare syncContext/dispose a cambi e smontaggio. AuthStore non modificato; il solo user_id non basta. dispose e definitivo ma non annulla HTTP gia inviati o effetti server.

409 blocca conservando snapshot non aggiornato; rete, 500 e risposte inutilizzabili durante comando sono incerti. 422 permette correzione manuale, 401/403 rimuovono snapshot. Solo rilettura server utilizzabile libera il blocco; 404 non prova annullamento/creazione. READY intermedio conserva preparazione, race_id conclude gara, cancel conclude separatamente. Nessuna operazione dopo conclusione/dispose.

DraftStore a istanze con $state.raw, aggiorna vista all avvio/finally, senza seconda coda. busy/blocked non sono permessi. syncContext fuori dai getter di rendering. Autenticazione, layout e listener SSE non integrati.

## Modal e presenze

Modal condiviso mantiene X visibile a destra e abilitata per default; opzioni nuove governano solo X. closeOnOutside governa Escape/sfondo. confirm-dialog e modal-close invariati.

DraftModal usa X a sinistra e closeOnOutside falso. Solo creatore, bloccato quando tutti i propri presenti sono READY; insieme vuoto non blocca per vacuita. Conferma annullare la gara? legata a istanza store, ID/versione e ricontrollata al clic. Non annullare non scrive. Contenuti montati ma nascosti/inert durante conferma. Nessuna chiusura anticipata o falso ripristino su errore. Esito terminale/dispose nasconde il contenitore.

Rileggi dal server e esplicito. Le bozze delle schermate devono essere protette: l ordine locale ora conserva la propria baseline e diventa inutilizzabile se una lettura la cambia. Le future altre bozze richiedono integrazione analoga. Inert non sostituisce guardie server. Focus trap, stacking, tastiera e navigazione globale non dichiarati completi.

DraftStart richiede store caricato. Draft invoca solo ondraft del futuro padre, non start o apertura preparazioni. Gara gia disputata usa il comando dedicato e attende race_id, senza controlli mazzo/READY o risultati.

Presenze da snapshot server, Presenti sopra Assenti, ordine interno ricevuto, conteggio per pilota senza deduplicare nomi/account. Escludi/Includi non ottimistici. Avanti conferma presenze, con indicatore del limite backend 1-12; il server controlla mazzi/pool e sceglie order o decks senza creare Race. Il padre e il recupero della selezione iniziale locale non sono ancora integrati.

## Ordine di scelta

L ordine iniziale e solo quello ricevuto dal server: nessun sorteggio o inversione dell arrivo nel browser. Prima gara appare come strong centrato quando first_race e vero. Il creatore puo usare la maniglia pointer con cattura del puntatore o i pulsanti Su/Giu; la maniglia disabilita il pan touch soltanto sulla propria area. Al pointercancel o perdita di cattura si ripristina l ordine locale precedente al gesto, non si scrive sul server.

La bozza e indipendente e conserva ID draft/campionato, versione, baseline e piloti presenti. Tutti e soli i presenti, senza duplicati; nessuna riparazione silenziosa di ordini errati. Cambi incompatibili rendono la bozza non inviabile e mostrano un avviso; non ne sostituiscono le modifiche. Il comando Scarta ordine locale richiede conferma esplicita, non fa rete e non libera blocchi del controller. La conferma di scarto verifica l identita della bozza e dello store.

Avanti esegue un solo tentativo esplicito: salva order se modificato; se save fallisce non chiama start. Dopo salvataggio controlla snapshot utilizzabile, identita, versione, ordine richiesto e disponibilita prima di start. Non e una transazione unica tra due HTTP e non c e rollback fittizio: se start fallisce dopo save, l ordine puo gia essere salvato. Nessun retry automatico. Un ordine confermato puo essere ricostruito dalla baseline server, senza conservare una falsa bozza ancora non salvata.

La serializzazione locale protegge l invio Avanti; il controller mantiene le proprie guardie e il server ricontrolla versione e permessi. Una pool divenuta insufficiente al momento di start e un errore server, non un salto client a decks. La scelta carte non e implementata in questo incremento.

## Verifiche e limiti

Test predisposti, non eseguiti localmente. Nessun type-check, lint, Vitest o build dichiarato superato per gli incrementi frontend. Il fallimento di check fornito dall autore e descritto sopra; nessun nuovo risultato Actions e stato letto autonomamente. Verifiche backend precedenti non attestano questi incrementi.

Helper ordine: spostamenti immutabili, insiemi, baseline e coordinamento save/start con port simulato. Test SSR: etichette, ordine iniziale, stato prima gara e controlli; non generano eventi pointer, tastiera o clic. Non sono verifiche di trascinamento touch, focus, conferme, reattivita DOM o comportamento end-to-end. Controller/store testati soltanto nei casi predisposti con trasporti simulati, non DB concorrente reale. Le opzioni del modal non hanno ancora prova browser attestata.

Comandi previsti in frontend: npm run check, npm run lint, npm test, npm run build. Nessuna installazione, formattazione o esecuzione test dichiarata in questa preparazione. I precedenti 503 GitHub erano errori di lettura risolti ritentando, non test falliti.

## Metodo e seguito

Push diretto degli incrementi approvati sul solo draft; niente accumulo nei commenti o nuovi workflow. La CI viene controllata o attesa solo su indicazione dell autore. Nessun merge implicito.

Questa nota aggiorna lo stato tecnico; docs/DRAFT_SPEC.md conserva le regole. Note backend e manifest sono prove precedenti, non nuovi verdi frontend. Setup, script, schema, risorse, dipendenze e lockfile invariati; niente scaffold, API backend, migrazioni o accesso al DB reale.

Restano scelta carte, mazzi/READY, montaggio Nuova gara/layout, autenticazione, lifecycle/live e collaudo browser.
