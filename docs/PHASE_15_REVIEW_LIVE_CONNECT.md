# Collegamento effettivo inventari revisione

Stato: applicazione e controlli ancora da verificare.
Base: store 1a5e941 e pannello aa14960, dopo guardie 01c567a e documenti a36e536.
Solo phase-15-sse-sistemazione. Il workflow vincola i blob originali, applica
sostituzioni univoche, crea sette test e pubblica store/pannello/test/nota solo
dopo formatter, lint, check, test e build. Se il ramo cambia si ferma senza force.
Questo commit prepara workflow e nota, non altera ancora i componenti pubblicati.

## Comportamento previsto dalla patch

Mount senza POST: ripresa GET della revisione propria. Coda condivisa SSE,
fallback solo senza open, intervallo admin, nessun nuovo EventSource. Load legge
stato, inventario/bozza propri e stato finale; 403/409 ricontrollano il contesto,
non diventano bozze vuote. Apply scarta letture durante scritture o di generazioni
precedenti e richiede un nuovo snapshot. Dopo azioni esplicite nuova lettura.

Base server separata: merge conserva remaining locali, metadati remoti e revoca
spunte interessate. Incompatibilita' conserva copia e blocca editing/conferma.
Cambio titolare/inizio non trasferisce lavoro. Guarda utente e verifica preinvio
restano attivi; nessuna atomicita' aggiunta al backend. Countdown locale e singola
rilettura alla scadenza, senza riarmare timer su scadenza gia' trascorsa.

Rilettura/apertura che sostituisce una copia richiede dialogo e backup browser
riuscito prima della sostituzione. Backup distinti, mai eliminati; copia precedente
visibile nella vista. Se storage fallisce l'operazione si interrompe. Progresso
legacy conserva conteggi ma revoca spunte; progresso non applicabile resta testo.
Bozza server incompatibile resta leggibile: solo recupero confermato riparte dai
dati inventario ignorando quell'esatto contenuto nella stessa revisione; un nuovo
contenuto incompatibile blocca di nuovo. Nessuna PUT/POST di conteggi agli eventi.
401/auth.expired fermano contesto e sottoscrizioni; non svuotano un diverso utente
entrato nel frattempo. HTTP gia' partite non sono annullate.

## Verifiche e confini

Sette test simulati: evento/merge, blocco e recupero, proprietario/nuovo inizio,
bozza incompatibile, errore/401, risposta dopo dispose, fallback/open. Mantiene
anche la suite preesistente delle guardie. Nessun test DOM/browser nuovo e nessun
comando npm eseguito localmente dall'assistente. Non presumere successo prima
di esito workflow, commit bot, diff e CI ordinaria della nuova testa.

Il genitore continua a ricreare/nascondere il pannello per stato/permessi: copia
visibile fino allo smontaggio, progresso sotto la propria chiave browser. Non e'
ancora un collaudo end-to-end del cambio fase. Restano warning canvas e prove
browser, compresi dialoghi, permessi e chiusure durante operazioni. Nessun avviso
di test manuale finale prima di verifiche e valutazione di questi confini.

Nessun backend, API, database, schema, dipendenza o lockfile modificato. Nessun
merge o intervento sui dati reali. Dopo controlli riusciti riallineare riepilogo,
nota gara, inventari e guardie senza attendere CI dei soli documenti. Documenti
protetti intatti. SSE complessivo non dichiarato concluso da questo solo blocco.
