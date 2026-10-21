# Collegamento effettivo inventari revisione

Aggiornamento: 2026-10-21. Applicato e verificato, non collaudo browser completo.
Solo phase-15-sse-sistemazione, PR 14 in bozza. Nessun merge autorizzato.

## Verifica riuscita

Preparazione 23b6bda, fix lint dbe8204, bot
1145a9af097b839a06e10e7bd22df9e742a4520f alle 20:10:11 CEST del 2026-10-21.
Bot modifica soltanto store, pannello, sette test e stato della nota.
CI ordinaria 39650297363 sulla nuova testa, tutti i job success:
- Migrazioni (database di test): 20:12:09 CEST.
- Frontend (check, lint, test, build): 20:12:36 CEST.
- Backend (pytest): 20:14:01 CEST.

Primo job connect 39646853375 fermato al lint: log autore delle 20:03 CEST,
sette errori e zero warning, niente check/test/build riusciti attribuiti a quel
tentativo. La sua CI ordinaria 39646861530 verde verificava il codice precedente.
Fix mirato: autoOpen usato per GET accorpata, tre chiavi each e tre SvelteSet.
Nessuna regola disattivata, cast aggiunto o aggiornamento dipendenze.

Workflow review-live-lint-fix verifica blob, riapplica il Python approvato del
workflow precedente e pubblica solo dopo formatter/lint/check/test/build. Stesso
gruppo concurrency, niente force push se cambia il ramo. Non rieseguire queste
patch sulla base gia' modificata: i vincoli di blob le faranno interrompere.
Esiti e file modificati letti, non log completi o conteggio totale della suite.
Nessun npm locale eseguito dall'assistente.

## Comportamento corrente

Mount senza POST, ripresa GET propria, client SSE condiviso e fallback solo senza
open con intervallo admin. Nessun nuovo EventSource o polling lento di sicurezza.
Load legge stato, inventario/bozza propri e stato finale; 403/409 verificano contesto,
non diventano []. Apply scarta snapshot durante scritture o di generazioni vecchie;
nuova lettura dopo azioni esplicite. Base distinta, remaining locali preservati e
metadati remoti applicati; spunte interessate revocate. Incompatibilita' conserva
copia e blocca editing/conferma; titolare/inizio diversi non trasferiscono lavoro.
Guardie preinvio mantenute, ma verifica e scrittura restano REST distinte.
Countdown senza riarmare timer per scadenze trascorse. 401/auth.expired fermano
contesto e sottoscrizioni senza svuotare un diverso utente sopraggiunto.

Rilettura/apertura che sostituisce lavoro: dialogo e backup browser obbligatorio,
copie distinte mai eliminate e precedente visibile. Se storage fallisce si ferma.
Progresso legacy revoca spunte; non applicabile conservato come testo. Recupero
confermato di bozza server incompatibile riparte dall'inventario e ignora solo
quell'esatto contenuto nella stessa revisione; nuovo contenuto incompatibile
riblocca. Nessuna scrittura REST dei conteggi agli eventi. HTTP in corso non annullate.

Sette test simulati: evento/merge, blocco/recupero, proprietario/nuovo inizio,
bozza incompatibile, errori/401, risposta dopo dispose, fallback/open. Suite guardie
preesistente mantenuta. Nessun nuovo test DOM/browser.

## Limiti e seguito

Il genitore ricrea/nasconde il pannello per stato/permessi: copia visibile fino
allo smontaggio, progresso sotto chiave propria. Cambio fase, dialoghi, permessi,
callback e chiusure durante richieste richiedono valutazione e collaudo browser.
Warning canvas ancora pendente; nessun avviso manuale finale prima di valutare
questi confini. SSE complessivo non dichiarato concluso dalla sola CI.

npm ci ha segnalato 10 vulnerabilita' (6 low, 2 moderate, 2 high), distinte dal
fallimento lint e non risolte qui. Nessun audit fix/force o analisi impatto.
Nessun backend, API, database, schema, lockfile o dato modificato. Riepilogo fase,
nota gara, inventari e guardie riallineati con questa nota nello stesso aggiornamento
solo documentale. Documenti protetti intatti; non attendere CI dei soli .md.
