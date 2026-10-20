# Fase 15a-4b - Controller e chiusura volontaria del popup

Aggiornamento: 2026-10-21. Ramo phase-15-sse-sistemazione, PR 14 in bozza.
Controller ora collegato al campionato tramite championship-live.ts: df7edf5,
formattazione dc97fcf, CI 39502927035 tutta verde. Pagina gara ancora pendente.

## Comportamento e confini

gift-popup-controller.ts e .spec.ts mantengono pilota/regalo, lista visibile,
ultimo snapshot e ID nascosti durante/dopo conferma. Riusa reconcileGifts.
Snapshot completo riuscito rimuove annulli senza ack; nuovi regali in coda finche'
la lista visibile si esaurisce o viene chiusa. close seleziona solo ID visibili
presenti nella lista resa passata dal componente. Durante l'ack non apre altri
popup, conserva gli snapshot e riconcilia l'ultimo alla fine. ID confermati
nascosti per il contesto anche se una lettura precedente li contiene.
Nessuna promessa exactly-once tra schede, riavvii o ripristini del database.

Errore di conferma rimuove soppressione locale del tentativo e passa a onError,
nessun retry automatico; batch precedenti potrebbero essere persistiti. La
successiva REST resta autorevole. Dispose blocca nuove azioni/callback ma non
cancella HTTP gia' partite.

card-gift-popup.svelte usa function binding sul Modal: soltanto la chiusura del
Modal richiama onclosed con l'ultima lista registrata dopo render. open=false del
genitore e smontaggio non confermano. Le vecchie callback senza argomenti restano
compatibili, ma il campionato ora usa onGiftsClosed(shown) e /seen-selected,
non il precedente /seen generale. Collegamento in PHASE_15_CHAMPIONSHIP_LIVE.md.

## Verifiche del blocco e successive

Base 991c218/CI 39498576979; servizio de29e70/CI 39497343267.
Implementazione 936f27b5fee628dba81974dfe864428ed61bf6a9. CI 39500026385 verde il
2026-10-20: migrazioni 23:24:20 CEST, frontend check/lint/test/build 23:24:31,
backend pytest 23:25:57. Formatter 39500018271 success 23:24:49. Testa riletta
invariata 936f27b: nessun nuovo commit bot presente a quel controllo.
Riallineamento eca9adb verificato in CI 39501199891.

Suite controller: coda nuovi arrivi, annullo senza ack, ID resi precedenti alla
nuova notifica, lettura precedente all'ack, errore senza retry, doppi click e
dispose durante ack. Passati con callback simulate, non DOM. Il successivo
collegamento campionato ha passato la propria suite sulla testa dc97fcf.
Rendering e function binding nel browser restano da verificare. Letti esiti e
commit, non log completi del formatter o conteggi numerici. Nessun comando locale.

Il workflow ora formatta i tre file del collegamento campionato: il perimetro
controller/popup era quello del commit 936f27b. Nessuna nuova dipendenza,
modifica a lockfile, API, schema, immagini o dati in questi blocchi frontend.
Questo riallineamento cambia solo documenti, da verificare con CI separata.
PROJECT_SPEC.md e PROJECT_STATUS.md restano protetti. Prossimo blocco: gara e
merge dei risultati non modificati; test manuali finali con avviso esplicito solo
dopo completamento e relativa CI verde. Nessun merge o intervento sui dati reali.
