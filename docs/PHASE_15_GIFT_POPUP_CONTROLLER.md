# Fase 15a-4b - Controller e chiusura volontaria del popup

Data: 2026-10-20. Ramo esclusivo phase-15-sse-sistemazione, PR 14 in bozza.
Base documentale 991c218 verificata: CI 39498576979 tutta verde.
Servizio notifiche de29e70 verificato nella CI 39497343267.

## Perimetro del blocco

- Nuovo gift-popup-controller.ts e relativa suite Vitest.
- card-gift-popup.svelte: distingue chiusura dal Modal e chiusura dal genitore.
- Workflow format-sse-client.yml mirato ai soli tre file frontend sopra.
- Questa nota. Nessuna pagina modificata in questo sottoinsieme.

Il controller mantiene associazione pilota/regalo, notifiche visibili, ultimo
snapshot completo e ID nascosti durante/dopo la conferma. Riusa reconcileGifts.
Una lettura completa rimuove i regali annullati senza inviare conferme. Nuovi
regali restano in coda finche' la lista visibile non si esaurisce o viene chiusa.
La chiusura volontaria riceve gli ID resi dal componente e seleziona solo quelli
ancora visibili: una notifica nuova non ancora resa non viene confermata.

Durante una conferma non apre un altro popup; gli snapshot vengono conservati.
Alla fine riconcilia l'ultima lettura. Gli ID confermati restano nascosti per
questo contesto, anche se una lettura partita prima della conferma li contiene.
Non si dichiara exactly-once tra schede, riavvii o ripristini del database.
Un errore rimuove la soppressione locale del tentativo e viene passato a onError;
non viene ritentata automaticamente la scrittura. Batch gia' riusciti restano
possibili: la successiva lettura REST resta autorevole, come nel servizio API.
Dispose impedisce nuove azioni e callback locali, non cancella HTTP gia' partite.

Il popup usa un function binding sul Modal: soltanto una chiusura originata dal
Modal richiama onclosed, passando l'ultima lista registrata dopo il render.
Impostare open=false nel genitore o smontare il componente non conferma regali.
Le callback esistenti senza argomenti restano compatibili, ma non usano ancora
la lista selettiva. Il vecchio handler nella pagina del campionato e' invariato:
continua a chiamare /seen generale. Questo blocco non dichiara risolta quella
conferma e non collega ancora il controller o il coordinatore SSE alle pagine.
La pagina gara e il merge delle modifiche locali ai risultati restano pendenti.

## Verifiche previste e stato reale

Test preparati: nuovi arrivi in coda, annullo remoto senza conferma, click prima
del rendering della nuova notifica, lettura precedente all'ack, errore senza
retry automatico, doppi click e dispose durante una conferma in corso.
Sono test del controller con callback simulate, non test DOM del componente:
la distinzione del function binding e il rendering richiedono ancora verifica.
Nessun npm, formatter, lint, check, test o build locale eseguito dall'assistente.
Nessun successo di questi nuovi file dichiarato prima dei risultati della CI.

Il workflow esistente formatta soltanto i tre file frontend del blocco usando
Prettier dal lockfile. Lint completo, check, test e build devono riuscire prima
del commit automatico; se il ramo cambia si ferma senza force push. Leggere il
commit effettivo del bot e i check della nuova testa, senza presumere trigger.
La prima CI ordinaria potrebbe precedere il commit di formattazione: distinguere
sempre gli SHA e non estendere il verde della base a questo blocco.

Nessuna nuova dipendenza, modifica ai lockfile, API, migrazioni, immagini o dati.
PROJECT_SPEC.md e PROJECT_STATUS.md restano protetti. Dopo la CI riuscita
riallineare le note interessate e PHASE_15.md, poi completare il collegamento
della pagina del campionato e, separatamente, della gara. Test manuali finali
solo dopo il collegamento e la relativa CI verde, con avviso esplicito all'autore.
Nessun merge o intervento sul database reale autorizzato da questo blocco.
