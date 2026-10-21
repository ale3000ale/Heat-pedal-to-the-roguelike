# Collegamento effettivo inventari revisione

Stato: collegamento e correzione lint applicati; formatter, lint, check, test e build frontend riusciti prima del commit bot.
Base: store 1a5e941 e pannello aa14960, dopo guardie 01c567a e documenti a36e536.
Solo phase-15-sse-sistemazione. Nessun merge o intervento sui dati reali autorizzato.

## Tentativo fallito e correzione mirata

Preparazione 23b6bda; job connect 39646853375 fallito. Log fornito dall'autore
alle 20:03 CEST del 2026-10-21: npm ci e formatter eseguiti, lint fallito con
sette errori e zero warning. autoOpen dichiarato ma inutilizzato, tre each senza
chiave e tre Set nello store per cui la regola richiede SvelteSet. Nessun successo
di type-check, test o build attribuito a quel tentativo fermato dal lint.
La CI ordinaria 39646861530 verde verificava il codice precedente al collegamento,
non i componenti generati nel workspace del job connect; nessun commit bot pubblicato.

review-live-lint-fix.yml verifica i blob di workflow/store/pannello, esegue solo
il blocco Python gia' approvato di review-live-connect.yml e corregge quei sette
errori: import SvelteSet, tre sostituzioni nello store, chiavi pilot_id nelle due
liste piloti e chiave composta pilota/carta/motivo nei problemi. autoOpen resta
compatibile ed esprime una richiesta iniziale GET accorpata, mai un POST al mount.
Nessuna regola ESLint disattivata, cast aggiunto o modifica al lockfile.

Il workflow applica le modifiche e crea i sette test nel workspace. Solo dopo
formatter, lint, check, test e build riusciti pubblica store/pannello/test/nota.
Se base o ramo cambiano si ferma, senza force push. Il vecchio workflow non viene
riattivato da questo aggiornamento; il suo contenuto resta vincolato al blob letto.
I due workflow condividono il gruppo concurrency per non applicare patch in parallelo.

## Comportamento del collegamento

Mount senza POST, ripresa GET propria, client condiviso e fallback solo senza open
con intervallo admin. Nessun nuovo EventSource. Snapshot legge stato, inventario e
bozza propri e stato finale; 403/409 ricontrollano il contesto senza bozze vuote.
Apply scarta letture durante scritture o di generazioni precedenti; dopo azioni
esplicite nuova lettura. Base server distinta, merge conserva remaining locali e
metadati remoti, revoca spunte interessate. Incompatibilita' conserva la copia e
blocca editing/conferma. Nessun trasferimento automatico fra titolari o nuovi inizi.
Guardie preinvio conservate, ma nessuna atomicita' nuova fra verifica e scrittura.
Countdown e rilettura alla scadenza senza riarmare timer su scadenza gia' trascorsa.

Recupero/apertura che sostituisce lavoro richiede dialogo e backup browser riuscito;
backup distinti mai eliminati, copia precedente visibile. Se storage fallisce si
interrompe. Progresso legacy revoca spunte; progresso non applicabile resta testo.
Bozza server incompatibile leggibile: recupero confermato ignora solo quel contenuto
nella stessa revisione, un nuovo contenuto incompatibile blocca di nuovo. Nessuna
scrittura REST di conteggi agli eventi. 401/auth.expired fermano contesto e
sottoscrizioni senza svuotare un diverso utente entrato nel frattempo.

## Verifiche e confini

Sette test preparati: evento/merge, blocco e recupero, proprietario/nuovo inizio,
bozza incompatibile, errore/401, risposta dopo dispose, fallback/open. Suite guardie
preesistente conservata. Nessun test DOM/browser nuovo, nessun npm locale eseguito
dall'assistente. Verificare esito workflow, bot, diff e CI ordinaria della nuova testa.

Il genitore ricrea/nasconde il pannello per stato/permessi: copia visibile fino allo
smontaggio, progresso sotto la chiave browser propria. Restano collaudo cambio fase,
dialoghi, permessi, chiusure durante operazioni e warning canvas. Nessun avviso di
collaudo finale prima di controlli riusciti e valutazione di questi confini.

npm ci segnala 10 vulnerabilita' (6 low, 2 moderate, 2 high): segnalazione distinta
dall'arresto ESLint, non risolta qui. Nessun npm audit fix o audit fix --force,
aggiornamento dipendenze o analisi di impatto effettuato in questo blocco.
Nessun backend, API, database, schema o dato modificato. Documenti protetti intatti.
Dopo riuscita riallineare riepilogo, gara, inventari e guardie senza attendere CI
dei soli .md; SSE complessivo non dichiarato concluso da questo solo blocco.
