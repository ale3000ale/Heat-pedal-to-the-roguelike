# Fase 15a-4b - Riconciliazione conservativa degli inventari di revisione

Data: 2026-10-21. Solo phase-15-sse-sistemazione, PR 14 in bozza.
Primo sottoinsieme della sincronizzazione interna: funzione pura e test.
Store e pannello non la usano ancora; nessun collegamento SSE nuovo dichiarato.

## Politica approvata e modulo

Proposta seguita alle 14:15: conservare conteggi locali incompatibili, bloccare
conferma senza clamp, revocare spunte interessate, non trasferire bozze a un altro
revisore/inizio e richiedere conferma per una rilettura che abbandona modifiche.
Questo modulo calcola il risultato; blocchi UI, spunte e dialogo saranno nello store.

review-inventory-reconcile.ts lavora su base server, copia locale e nuovo remoto
con bozza server gia' applicata, nella medesima revisione propria. ownReviewKey
identifica gara/revisore/inizio soltanto per il proprio stato attivo; non autorizza
richieste o sostituisce la verifica server della scadenza. Il chiamante deve
confrontare le chiavi prima di applicare il merge.

Restano locali i remaining modificati, con nuovi metadati e carte dal remoto.
changedPilotIds segnala differenze dei dati carte rispetto alla base, non riordini
o cambi del solo nome pilota. conflictingPilotIds segnala conteggi concorrenti
validi da ricontrollare. Carte/piloti rimossi con modifiche o conteggi oltre il
nuovo totale producono issues e blocked: l'intera copia locale resta intatta.
Nessuna riduzione automatica o scarto silenzioso. Duplicati normalizzati e fonti
server non valide generano RangeError; il chiamante non deve convertirli in [].
Le liste e le carte restituite sono copie indipendenti, nessuna scrittura REST.

## Fonti verificate e limiti

Rilette API review_counts.py e race_review.py: inventario giudice/admin in lettura,
bozza solo titolare attivo; GET stato puo' gia' elaborare scadenze sul server.
Il futuro client non deve aggiungere conferme/salvataggi automatici agli eventi.
Un cambio di proprietario durante le letture puo' dare 403/409: rileggere lo stato,
non interpretare una bozza non leggibile come bozza vuota o autorizzazione a scrivere.

Test preparati: chiave propria/nuovo inizio, aggiornamenti puliti, conteggi locali,
nuove carte e immutabilita', totale ridotto, carta/pilota rimosso, conflitto valido,
snapshot vuoto riuscito e input invalidi. Sono test puri, non dello store o DOM.
Nessun npm, formatter, lint, check, test o build locale eseguito. Nuova CI da leggere:
nessun successo del nuovo codice dichiarato prima dei controlli.

Workflow formatter limitato ai due nuovi file TypeScript, con lockfile invariato.
Esegue lint completo/check/test/build prima di eventuale commit, si ferma se il
ramo cambia, senza force push. Verificare eventuale bot, diff e nuova testa.
Dopo esiti verdi riallineare le note interessate, poi collegare realmente store,
pannello e recupero esplicito delle bozze, con test del lifecycle e dei permessi.
Commit solo .md non bloccano il seguito, come richiesto. PROJECT_SPEC.md e
PROJECT_STATUS.md protetti. Nessuna nuova dipendenza, API, migrazione, immagine
o dato modificato. Warning canvas e prove browser ancora separati e pendenti.
Nessun merge o intervento sui dati reali autorizzato; nessun test manuale finale
richiesto ora. Il merge frontend non introduce concorrenza protetta lato server.
