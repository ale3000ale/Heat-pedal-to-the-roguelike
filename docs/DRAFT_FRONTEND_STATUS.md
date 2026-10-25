# Draft - primo incremento frontend

Data: 25 ottobre 2026. Ramo: draft. PR: 18.

## Stato corrente

Primo incremento approvato: contratti TypeScriptScript, validazione runtime delle risposte, client API autenticato e test Vitest predisposti. Non contiene ancora interfaccia, store, modal o collegamento SSE. Nuova gara non viene modificato. Nessuna funzionalita visuale draft dichiarata disponibile.

File: frontend/src/lib/draft-types.ts, draft-validation.ts, draft-api.ts, draft-validation.spec.ts e draft-api.spec.ts. CardEntry e api.ts sono riusati senza modificarli.

## Contratto e limiti

I DTO seguono backend/app/schemas/draft.py e DraftCardSlot. Le carte identiche rimangono copie distinte tramite slot_id. I validatori verificano forma, tipi, interi sicuri, nullable espliciti e identificativi duplicati; restituiscono copie dei campi pubblici. Non riproducono il motore delle fasi, non decidono chi sia autorizzato e non impongono 15 copie nel lettore del mazzo.

fetchDrafts, openDraft, fetchDraft e fetchDraftDeck leggono i contesti autorizzati. sendDraftCommand usa comandi tipizzati per attendance, attendance/confirm, order, start, preview, choice, deck/move, ready, already-disputed e cancel. Il payload richiede versione e soli campi previsti. Le risposte vengono validate e confrontate con draft, campionato o pilota richiesto quando il DTO contiene tale identificativo.

Nessun retry automatico, polling o rilettura implicita dopo scrittura. ApiError preserva il comportamento del client condiviso. Un errore di rete o una risposta POST inutilizzabile non dimostrano rollback; l interfaccia futura dovra gestire esplicitamente l esito incerto e la rilettura autorizzata.

## Verifiche

Test predisposti, non eseguiti localmente. Type-check, lint, Vitest e build non dichiarati superati per questo incremento. Nessun nuovo risultato della CI letto o atteso dall assistente. I risultati backend precedenti non attestano questo codice frontend. I test delle fasi del parser verificano il discriminante del DTO, non la coerenza di gioco dello stato.

Comandi previsti per la verifica, dalla cartella frontend: npm run check, npm run lint, npm test, npm run build. Nessun comando di installazione, formattazione o test dichiarato eseguito in questa preparazione.

## Metodo aggiornato dall autore

Pubblicare direttamente gli incrementi approvati sul solo ramo draft; non accumularli nei commenti e non introdurre altri workflow di ricostruzione o pubblicazione. Non controllare o attendere la CI autonomamente: l autore comunica quando verificarla, intervenire o aspettare. Nessun merge implicito.

## Allineamento documentale e seguito

Questa nota registra lo stato tecnico del primo incremento e aggiorna, per questo perimetro, le precedenti descrizioni generiche di frontend non implementato: il trasporto e predisposto, l interfaccia non lo e. Le regole funzionali di docs/DRAFT_SPEC.md restano invariate. Le note backend e il manifest documentano la verifica precedente, non un nuovo verde frontend.

README e documenti generali conservano validita su assenza dell interfaccia, setup, script, schema e risorse: tali aspetti non cambiano in questo incremento. Nessuna dipendenza, lockfile, scaffold, API backend o migrazione modificata. Nessun accesso al database reale. Restano da realizzare modal iniziale, presenze, ordine, scelta carte, preparazione mazzi, READY, lifecycle e live, con verifiche browser separate.
