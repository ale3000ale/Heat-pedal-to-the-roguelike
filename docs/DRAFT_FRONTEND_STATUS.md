# Draft - incrementi frontend

Data: 25 ottobre 2026. Ramo: draft. PR: 18.

## Stato corrente

Primo incremento: contratti TypeScript, validazione runtime, client API autenticato e test Vitest predisposti, pubblicati nel commit 8d6f7cd62ef5058e0123e4acae5245bd62cd130a. Corretto il refuso TypeScriptScript del documento precedente.

Secondo incremento: controller isolato della sessione e test predisposti per concorrenza, lifecycle e gestione degli errori. Non contiene ancora interfaccia, store reattivo, modal o collegamento SSE. Nuova gara non viene modificato. Nessuna funzionalita visuale draft dichiarata disponibile.

File del primo incremento: frontend/src/lib/draft-types.ts, draft-validation.ts, draft-api.ts, draft-validation.spec.ts e draft-api.spec.ts. CardEntry e api.ts sono riusati senza modificarli. Nuovi file del secondo incremento: frontend/src/lib/draft-session.ts e draft-session.spec.ts.

## Contratto e limiti dei DTO

I DTO seguono backend/app/schemas/draft.py e DraftCardSlot. Le carte identiche rimangono copie distinte tramite slot_id. I validatori verificano forma, tipi, interi sicuri, nullable espliciti e identificativi duplicati; restituiscono copie dei campi pubblici. Non riproducono il motore delle fasi, non decidono chi sia autorizzato e non impongono 15 copie nel lettore del mazzo.

fetchDrafts, openDraft, fetchDraft e fetchDraftDeck leggono i contesti autorizzati. sendDraftCommand usa comandi tipizzati per attendance, attendance/confirm, order, start, preview, choice, deck/move, ready, already-disputed e cancel. Il payload richiede versione e soli campi previsti. Le risposte vengono validate e confrontate con draft, campionato o pilota richiesto quando il DTO contiene tale identificativo.

Nessun retry automatico, polling o rilettura implicita dopo scrittura. ApiError preserva il comportamento del client condiviso. Un errore di rete o una risposta POST inutilizzabile non dimostrano rollback.

## Controller della sessione

createDraftSession non avvia richieste. refresh esegue una lettura soltanto su chiamata esplicita; command invia una sola operazione usando la versione dello snapshot server. Durante lettura o scrittura non accoda altre richieste. getState restituisce copie indipendenti; non e una sottoscrizione reattiva e non sostituisce il futuro store UI.

Il contesto e fissato alla creazione. getContext deve restituire una chiave che comprenda la generazione autenticata e il contesto, cambiando anche dopo logout e nuovo login dello stesso utente. Il futuro chiamante deve chiamare dispose a cambio utente/ruolo/contesto e smontaggio. Il controller ricontrolla inoltre la chiave quando si consulta lo stato o si gestiscono operazioni e risposte. Non ascolta autonomamente auth o SSE.

Le risposte tardive dopo invalidazione sono scartate. dispose svuota lo stato ed e definitivo: non annulla richieste HTTP gia inviate e non garantisce rollback sul server. La versione di una risposta non puo regredire, ne possono cambiare draft o campionato del contesto gia caricato.

HTTP 409 blocca le scritture conservando lo snapshot precedente, che non va mostrato come aggiornato. Errori di rete, 500 e risposte inutilizzabili durante un comando sono trattati conservativamente come esito incerto. Un 422 consente una successiva correzione manuale, senza reinvio automatico. Un 401/403 rimuove lo snapshot e blocca le scritture. Una rilettura fallita mantiene il blocco; solo una rilettura server utilizzabile lo libera. Un 404 non viene interpretato come prova di annullamento o creazione gara.

READY intermedio conserva la preparazione restituita dal server. Un esito con race_id conclude la sessione come gara creata; annullamento riuscito la conclude separatamente senza inventare una gara. Non sono consentiti altri comandi o refresh dopo conclusione o dispose. Il controller non sostituisce i permessi del server o le future conferme testuali dell interfaccia.

## Verifiche

Test di client, validatori e controller predisposti, non eseguiti localmente. Type-check, lint, Vitest e build non dichiarati superati per questi incrementi. Nessun nuovo risultato della CI letto o atteso dall assistente. I risultati backend precedenti non attestano questo codice frontend. I test delle fasi del parser verificano il discriminante del DTO, non la coerenza di gioco dello stato; i test controller usano trasporti simulati, non browser o concorrenza reale sul database.

Comandi previsti per la verifica, dalla cartella frontend: npm run check, npm run lint, npm test, npm run build. Nessun comando di installazione, formattazione o test dichiarato eseguito in questa preparazione.

## Metodo aggiornato dall autore

Pubblicare direttamente gli incrementi approvati sul solo ramo draft; non accumularli nei commenti e non introdurre altri workflow di ricostruzione o pubblicazione. Non controllare o attendere la CI autonomamente: l autore comunica quando verificarla, intervenire o aspettare. Nessun merge implicito.

## Allineamento documentale e seguito

Questa nota registra lo stato tecnico corrente e aggiorna, per questo perimetro, le precedenti descrizioni generiche di frontend non implementato: trasporto e controller sono predisposti, l interfaccia non lo e. Le regole funzionali di docs/DRAFT_SPEC.md restano invariate. Le note backend e il manifest documentano la verifica precedente, non un nuovo verde frontend.

README e documenti generali conservano validita su assenza dell interfaccia, setup, script, schema e risorse: tali aspetti non cambiano. Nessuna dipendenza, lockfile, scaffold, API backend o migrazione modificata. Nessun accesso al database reale. Restano store UI, modal iniziale, presenze, ordine, scelta carte, preparazione mazzi, READY, lifecycle integrato e live, con verifiche browser separate.
