# Fase 15a-4b - Controller e chiusura volontaria del popup

Data: 2026-10-20. Ramo esclusivo phase-15-sse-sistemazione, PR 14 in bozza.
Base documentale 991c218 verificata: CI 39498576979 tutta verde.
Servizio notifiche de29e70 verificato nella CI 39497343267.
Controller e popup pubblicati in 936f27b e verificati in CI 39500026385.

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

## Verifiche effettive e limiti

Commit implementativo: 936f27b5fee628dba81974dfe864428ed61bf6a9.
CI ordinaria della PR 14: run 39500026385, tutti i job completati con successo.
https://github.com/ale3000ale/Heat-pedal-to-the-roguelike/actions/runs/39500026385
Formatter: run 39500018271, job format success.
https://github.com/ale3000ale/Heat-pedal-to-the-roguelike/actions/runs/39500018271

| Controllo | Esito | Conclusione CEST del 2026-10-20 |
|---|---|---|
| Migrazioni (database di test) | success | 23:24:20 |
| Frontend (check, lint, test, build) | success | 23:24:31 |
| Formatter e verifiche frontend | success | 23:24:49 |
| Backend (pytest) | success | 23:25:57 |

Letti anche i dettagli della testa del ramo: ancora 936f27b dopo il successo del
formatter, nessun nuovo commit del bot presente al controllo. Non si attribuisce
quindi la CI a una testa formattata diversa o a un commit automatico presunto.
Non sono stati letti log completi del formatter o conteggi numerici dei test.

La suite del controller include nuovi arrivi in coda, annullo remoto senza
conferma, click con ID resi precedenti alla nuova notifica, lettura precedente
all'ack, errore senza retry automatico, doppi click e dispose durante una conferma.
Questi test sono passati con la suite frontend, ma usano callback simulate:
non sono test DOM del componente. Il rendering e il comportamento del function
binding nel browser restano da verificare; type-check e build non li certificano.
Nessun npm, formatter, lint, check, test o build locale eseguito dall'assistente.
Nessuna nuova prova browser richiesta all'autore in questo passaggio.

Il workflow resta limitato ai tre file frontend del blocco, con Prettier dal
lockfile e lint completo, check, test e build prima di un eventuale commit.
Se il ramo cambia si ferma senza force push. Nessuna modifica a dipendenze,
lockfile, API, migrazioni, immagini o dati nel blocco del controller.

## Riallineamento e seguito

Questo riallineamento aggiorna soltanto questa nota e PHASE_15.md; il nuovo
commit documentale richiede una verifica CI separata. PROJECT_SPEC.md e
PROJECT_STATUS.md restano protetti. Nessun codice, workflow o dato modificato
in questo push e nessun merge autorizzato.

Passo successivo: collegare realmente la pagina del campionato a servizio,
controller e coordinatore SSE; sostituire l'handler /seen generale con la
conferma dei soli ID resi, mantenendo polling solo senza stream open e snapshot
completi senza errori trasformati in []. Poi completare la pagina gara e il
merge dei campi risultati non modificati. Non occorrono altri prerequisiti
backend per questi collegamenti gia' pianificati.
Test manuali finali solo dopo il collegamento e la relativa CI verde, con avviso
esplicito all'autore. Nessun intervento sul database reale autorizzato dal verde.
