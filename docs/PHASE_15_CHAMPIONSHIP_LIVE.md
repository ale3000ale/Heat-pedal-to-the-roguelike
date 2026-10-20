# Fase 15a-4b - Collegamento effettivo della pagina campionato

Data: 2026-10-20. Solo ramo phase-15-sse-sistemazione, PR 14 in bozza.
Base eca9adb: CI 39501199891 tutta verde. Nessun merge autorizzato.

## File del blocco

- frontend/src/lib/championship-live.ts: lettura e coordinamento testabili.
- frontend/src/lib/championship-live.spec.ts: test con REST e client SSE simulati.
- frontend/src/routes/championships/[id]/+page.svelte: collegamento reale.
- .github/workflows/format-sse-client.yml: formatter sui tre file frontend sopra.
- Questa nota. Pagina gara, API e migrazioni non modificate.

La pagina non usa piu' startGiftPolling, il wrapper che nasconde errori o
markGiftsSeen generale. Riusa servizio selettivo, controller popup e coordinatore
SSE condiviso. Non crea un altro EventSource e non cambia il layout autenticato.

Il load rilegge campionato, classifica, gare e piloti propri, poi le notifiche
dei soli piloti propri iscritti, con associazione pilota/regalo conservata.
Non e' una transazione unica tra REST. Un errore rifiuta lo snapshot completo:
non viene trasformato in [] e non chiude il popup. Campionato chiuso: niente
popup dei regali, coerente con il comportamento precedente.

Apply aggiorna i dati della pagina e il controller anche con popup aperto;
refreshKey aggiorna le sezioni sponsor aperte. Gli eventi del campionato e resync
richiedono una rilettura, non costruiscono carte dai payload. Il fallback usa
l'intervallo admin e gira solo senza stream open. Nessun polling di sicurezza
con stream aperto; buffering reale del proxy ancora non verificato.

La X passa gli ID resi al controller: la conferma usa soltanto /seen-selected,
con batch per pilota gia' gestiti dal servizio. La chiusura remota non invoca
onclosed. Dopo la conferma si richiede una nuova lettura accorpata per invalidare
risposte precedenti all'ack. Annullamenti e snapshot vuoti riusciti non scrivono.
Le garanzie sui batch parziali e sugli ID sicuri JavaScript restano invariate.

Il contesto dipende dal parametro campionato e dall'utente, non dagli snapshot.
Cleanup ferma coordinator/controller e impedisce avvii tardivi dopo la lettura
dell'intervallo. Le risposte di un vecchio contesto non vengono applicate.
Un 401 del modulo ferma lavoro e popup prima di svuotare auth; auth.expired
resta gestito dal layout e dal coordinatore condiviso. Le HTTP gia' partite non
vengono cancellate. Nessun retry automatico delle scritture.

Reload dopo impostazioni/iscrizione/creazione gara usa la stessa coda live.
Gli errori dei refresh conservano i dati correnti e mostrano un avviso; al primo
caricamento mostrano l'errore senza inventare dati. Non si estende SSE ai CRUD
privi di eventi: eventuali modifiche di impostazioni o iscrizioni da altri client
non sono garantite immediate con stream aperto.

## Verifiche e limiti

Test preparati: filtro piloti propri/iscritti, campionato chiuso, collegamento
popup/ack selettivo, nuovi arrivi in coda, errore REST che non chiude il popup,
annullo su snapshot vuoto senza scrittura, fallback/open, 401 e risposta tardiva
dopo dispose. Usano dipendenze simulate, non il DOM della pagina o del popup.
Nessun npm, formatter, lint, type-check, test o build locale eseguito dall'assistente.
Nessun successo dei nuovi file dichiarato prima della relativa CI.

Il formatter dal lockfile e' limitato ai tre file frontend del blocco. Prima di
un eventuale commit automatico esegue lint completo, check, test e build. Se il
ramo cambia si ferma senza force push. Leggere esito del formatter, eventuale
commit bot e check sulla testa effettiva, distinguendo la prima CI non formattata.
Nessuna dipendenza, lockfile, immagine, API, migrazione o dato del gioco modificato.

Dopo CI riuscita riallineare PHASE_15.md e tutte le note interessate, mantenendo
PROJECT_SPEC.md e PROJECT_STATUS.md protetti. Le note precedenti che descrivono
pagine non collegate restano storiche fino a quel riallineamento.
La pagina gara e il merge non distruttivo dei risultati restano da implementare.
Il collegamento del campionato non certifica il rendering, il deployment, il
proxy o il carico. Nessuna prova browser eseguita o richiesta ora all'autore.
Avviso e checklist dei test manuali finali dopo il collegamento restante e la
relativa CI verde. Nessuna applicazione di migrazioni al database reale autorizzata.
