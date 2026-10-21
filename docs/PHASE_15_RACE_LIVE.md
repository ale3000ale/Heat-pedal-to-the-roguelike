# Fase 15a-4b - Collegamento gara e callback revisione

Data: 2026-10-21. Solo phase-15-sse-sistemazione, PR 14 in bozza.
Base riletta 0709ca4, commit solo documentale senza attesa CI, come richiesto.
Merge puro verificato sulla testa 3c860d2, CI 39509635060 verde.

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

## Confini e verifiche ancora pendenti

Lo store review-counts.svelte.ts non e' modificato: nessuna nuova sincronizzazione
SSE interna degli inventari, delle bozze o del revisore a stato gara invariato
viene dichiarata qui. Restano le sue operazioni e il suo timer esistenti. Questo
blocco collega intestazione/risultati/stato gara e rimuove il reload distruttivo;
non certifica completata ogni vista di revisione della fase 15.

La suite pura di riconciliazione e i test del coordinatore sono gia' presenti.
Non sono aggiunti test DOM dei due componenti: guardia uscita, vista in sola lettura,
modifiche durante PUT e callback richiedono ancora verifica integrata/browser.
Nessun npm, formatter, lint, check, test o build locale eseguito dall'assistente.
Nessun controllo dei nuovi componenti ancora dichiarato superato: leggere formatter,
eventuale commit bot, diff e CI della testa risultante. Il formatter usa il lockfile,
esegue lint completo/check/test/build prima di pubblicare solo i due file;
se cambia il ramo si ferma senza force push. Prima CI non formattata distinta.

Nessuna nuova dipendenza, lockfile, API, migrazione, immagine o dato modificato.
PROJECT_SPEC.md e PROJECT_STATUS.md protetti. Dopo CI riuscita riallineare tutte
le note interessate e PHASE_15.md, senza attendere test dei soli commit .md.
Prima di dichiarare completato SSE, affrontare la sincronizzazione interna del
pannello. Nessuna prova browser eseguita o richiesta ora: avviso e checklist finali
solo dopo completamento dei collegamenti restanti e relativi controlli verdi.
Nessun merge o intervento sul database reale autorizzato.
