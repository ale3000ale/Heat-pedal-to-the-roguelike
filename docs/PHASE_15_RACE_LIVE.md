# Fase 15a-4b - Gara e revisione live

Aggiornamento: 2026-10-21. Solo phase-15-sse-sistemazione, PR 14 in bozza.
Cronologia gara estesa nelle versioni fcead0f/a36e536 e nella storia Git.

## Gara verificata

Implementazione 4833a8d, fix nullable 44bb4dd, bot 4978f73, CI 39596834057 verde.
Il primo tentativo falli' il frontend/type-check: nessun test/build riuscito
attribuito a quello. knownPilotIds da race?.results o [], niente race! o cast.
Pagina con startLiveRefresh per gara/campionato/piloti, eventi anche per is_last,
fallback solo senza open. Base distinta da ordine/assenti/sponsor, merge risultati
3c860d2. Ufficiali/permessi aggiornati, bozza locale preservata in sola lettura se
non modificabile, in memoria fino all'uscita. PUT esplicita con copia preinvio,
controlli ID/duplicati/piloti e massimo 12, normalizzazione sponsor preesistente.
Nessun lock ottimistico. Letture durante PUT non applicate, nuova lettura dopo esito.
Uscita/unload protetti, HTTP gia' partite non annullate. Cleanup per contesto,
401 libera auth. Pannello usa onchanged, non reload browser.

## Store e pannello ora collegati

Guardie 01c567a, CI 39636047244; collegamento effettivo 1145a9a, CI 39650297363
verde su frontend, backend e migrazioni di test. Non e' piu' corretto descrivere
merge inventari o coda interna come ancora da collegare. Mount GET-only, bozza
propria, merge conservativo, spunte revocate sui dati cambiati, blocchi espliciti,
backup e recupero confermato. autoOpen non invia POST. Nessun EventSource aggiunto.
Dettagli, errori iniziali e sette test in PHASE_15_REVIEW_LIVE_CONNECT.md.

Rimane la ricreazione del pannello per campionato/gara/utente/stato: non viene
ricreato a ogni snapshot risultati, ma puo' essere smontato al cambio fase.
La copia visibile vive nella vista, il progresso usa la chiave browser propria.
Il comportamento fra smontaggio, nuova fase e recupero va valutato/collaudato;
non e' certificato dai test simulati dello store. Verifica preinvio e scrittura
restano richieste separate, non una transazione backend.

## Limiti e seguito

Sette errori lint del tentativo 23b6bda corretti senza disabilitare regole:
autoOpen usato come GET, chiavi each e SvelteSet. Bot pubblicato dopo controlli.
Verificati esiti e file modificati, non log completi. Nessun comando locale o
nuovo test DOM/browser dell'assistente. Warning canvas role img ancora pendente.
CI verde non prova dialoghi, guardie uscita, callback o modifiche durante PUT.

Solo documenti in questo riallineamento, nessuna modifica a codice, workflow,
API, schema, immagini, lockfile o dati. Documenti protetti intatti. Non attendere
CI dei soli .md. Seguito: valutazione lifecycle genitore e warning, poi collaudo
browser con avviso esplicito quando pronto. Nessun merge o intervento sui dati reali.
