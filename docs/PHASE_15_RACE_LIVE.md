# Fase 15a-4b - Collegamento gara e callback revisione

Data: 2026-10-21. Solo phase-15-sse-sistemazione, PR 14 in bozza.
Base riletta 0709ca4, commit solo documentale senza attesa CI, come richiesto.
Merge puro verificato sulla testa 3c860d2, CI 39509635060 verde.
Implementazione del collegamento: 4833a8dce73dec8d6634376fdaaab67fa1d24168.
Controlli del collegamento non ancora superati: primo tentativo fallito, fix sotto.

## File e comportamento implementato

- Pagina championships/[id]/races/[raceId]/+page.svelte.
- components/race-review-panel.svelte: callback onchanged al posto del reload.
- Workflow format-sse-client.yml limitato ai due componenti e questa nota.

La pagina usa startLiveRefresh condiviso: load completo di gara, campionato e
piloti propri, senza effetti UI; eventi del campionato e resync invalidano la
lettura. Filtro per campionato, non sola gara, per aggiornare anche is_last quando
parte una gara successiva. Polling solo senza stream open, intervallo admin.
Nessun altro EventSource e nessun polling di sicurezza con stream aperto.

Base server separata da ordine/assenti/sponsor. Le REST riuscite applicano il
merge a tre vie gia' testato. Ordine/assenti restano accoppiati; sponsor locali
non sovrascritti. Conflitti segnalati senza scrivere. I risultati ufficiali e i
permessi si aggiornano comunque; se la modifica non e' piu' permessa la bozza
locale resta visibile in sola lettura. Bozza solo in memoria fino all'uscita,
non salvata automaticamente sul server o nel browser. Un cambio utente svuota
il contesto per non trasferire bozze tra utenti.

Il salvataggio esplicito verifica stato UI, tutti i piloti assegnati, duplicati,
ID ancora presenti e massimo 12 partecipanti; mantiene la normalizzazione sponsor
preesistente. Il backend resta autorevole su regole e permessi. La copia locale
prima della PUT e' la base per fondere la risposta con modifiche fatte durante
la richiesta. Nessun lock ottimistico/versione backend introdotto: non garantisce
assenza di sovrascritture concorrenti sul server. Letture durante PUT non applicate,
poi nuova lettura accorpata anche dopo errore. Risposte di vecchio contesto ignorate.

Uscita interna o unload protetti con bozza modificata o PUT in corso, anche per
correzioni di gare gia' concluse. Il dialogo chiarisce che uscire non annulla HTTP
gia' inviate. Sessione scaduta non blocca il flusso di autenticazione. Errori di
refresh conservano i dati, 401 svuota auth; cleanup invalida code e avvii tardivi.

Il pannello notifica una transizione riuscita alla pagina tramite onchanged,
senza window.location.reload e senza richiamare genitore dopo smontaggio.
Il componente e' ricreato per campionato/gara/utente/stato, non a ogni snapshot:
non si azzerano conteggi locali per un semplice aggiornamento dei risultati.

## Primo tentativo e fix del type-check

CI ordinaria 39593722874: frontend failure alle 13:41:05 CEST del 2026-10-21,
migrazioni success alle 13:41:13, backend pytest success alle 13:43:00.
Formatter 39593716889: failure alle 13:41:16. Esiti dei job letti su GitHub;
non si dichiara pubblicato un commit bot di formattazione riuscita.

Il log dell'autore alle 13:54 segnala un errore svelte-check: race potenzialmente
null nel callback di unknownPilot, oltre a un warning separato sul role img del
canvas in card-crop-editor.svelte. Non si presumono riusciti test/build dei job
falliti o risultati di step non riportati dal log.

Fix mirato: knownPilotIds e' un Set derivato da race?.results oppure da [].
unknownPilot mantiene la guardia race !== null, ma il callback legge solo il Set
sempre definito. Nessun race!, cast, soppressione TypeScript o cambio alle regole
di salvataggio. La modifica preserva il significato del controllo: nessun pilota
sconosciuto prima della lettura, blocco se una bozza contiene ID non piu' presenti.

Il workflow viene riattivato cambiando soltanto il nome dello step check; comandi,
file formattabili, trigger e protezioni restano invariati. Formatter dal lockfile,
lint completo/check/test/build prima di pubblicare i due componenti. Se il ramo
cambia si ferma senza force push. Verificare nuovo job, eventuale bot e CI della
testa risultante; non dichiarare risolto il type-check prima degli esiti reali.
Il warning canvas e' registrato come sistemazione separata e non viene corretto
qui; non si dichiara quindi ottenuto un check senza warning.

## Confini e verifiche ancora pendenti

Lo store review-counts.svelte.ts non e' modificato: nessuna nuova sincronizzazione
SSE interna degli inventari, delle bozze o del revisore a stato gara invariato
viene dichiarata qui. Restano le sue operazioni e il suo timer esistenti. Questo
blocco collega intestazione/risultati/stato gara e rimuove il reload distruttivo;
non certifica completata ogni vista di revisione della fase 15.

La suite pura di riconciliazione e i test del coordinatore sono gia' presenti.
Non sono aggiunti test DOM dei componenti: guardia uscita, vista in sola lettura,
modifiche durante PUT, callback e reattivita' del controllo piloti richiedono
ancora verifica integrata/browser. Nessun npm, formatter, lint, check, test o build
locale eseguito dall'assistente. Nessun successo dei nuovi controlli dichiarato.

Questo fix modifica pagina gara, nome dello step nel workflow e questa nota;
nessuna modifica diretta al pannello o al componente canvas. Nessuna dipendenza,
lockfile, API, migrazione, immagine o dato modificato. PROJECT_SPEC.md e
PROJECT_STATUS.md protetti. Dopo CI riuscita riallineare tutte le note interessate
e PHASE_15.md, senza attendere test dei soli commit .md. Prima di dichiarare
completato SSE, affrontare la sincronizzazione interna del pannello.
Nessuna prova browser eseguita o richiesta ora: avviso e checklist finali solo
dopo completamento dei collegamenti restanti e relativi controlli verdi.
Nessun merge o intervento sul database reale autorizzato.
