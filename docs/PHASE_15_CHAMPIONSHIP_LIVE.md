# Fase 15a-4b - Collegamento effettivo della pagina campionato

Aggiornamento: 2026-10-21. Solo ramo phase-15-sse-sistemazione, PR 14 in bozza.
Base eca9adb verificata in CI 39501199891. Implementazione df7edf5,
testa formattata dc97fcf verificata in CI 39502927035. Nessun merge autorizzato.

## File e comportamento corrente

- frontend/src/lib/championship-live.ts: lettura e coordinamento testabili.
- frontend/src/lib/championship-live.spec.ts: REST e client SSE simulati.
- frontend/src/routes/championships/[id]/+page.svelte: collegamento reale.
- .github/workflows/format-sse-client.yml: formatter sui tre file frontend sopra.
- Questa nota. Pagina gara, API e migrazioni non modificate dal blocco.

La pagina non usa piu' startGiftPolling, il wrapper che nasconde errori o
markGiftsSeen generale. Riusa servizio selettivo, controller popup e coordinatore
SSE condiviso, senza un secondo EventSource o modifiche al layout autenticato.
Load rilegge campionato, classifica, gare e piloti propri, poi le notifiche dei
soli piloti propri iscritti, mantenendo associazione pilota/regalo. Sono piu'
REST autorizzate, non una transazione SQL unica. Un errore rifiuta lo snapshot:
non diventa [] e non chiude il popup. Campionato chiuso: nessun popup regali,
come prima; l'API backend puo' comunque confermare notifiche storiche.

Apply aggiorna pagina e controller anche con popup aperto; refreshKey aggiorna
le sezioni sponsor aperte. Eventi del campionato e resync richiedono riletture,
non costruiscono carte dai payload. Polling con intervallo admin soltanto senza
stream open, nessun polling di sicurezza con stream aperto. Resta il limite
non verificato del proxy che mantiene open ma trattiene gli eventi.

La X passa la lista resa al controller. Conferma soltanto /seen-selected, in
batch per pilota; chiusure remote e snapshot vuoti riusciti non scrivono.
Dopo l'ack richiede una rilettura accorpata che invalida risposte precedenti.
Restano i limiti sui batch parziali, sugli ID sicuri JavaScript e sulle HTTP
gia' partite, che non vengono cancellate. Nessun retry automatico delle scritture.

Lifecycle legato a parametro campionato e utente, non agli snapshot. Cleanup
ferma controller/coordinatore e impedisce avvii tardivi dopo la lettura
intervallo. Un 401 ferma il modulo prima di svuotare auth; auth.expired resta
anche gestito dal layout. Reload dopo impostazioni, iscrizione o creazione gara
usa la stessa coda. Errori di refresh conservano i dati e mostrano un avviso;
al primo caricamento mostrano l'errore senza inventare dati. I CRUD privi di
eventi non diventano immediati tra client con stream aperto.

## Verifiche effettive

Implementazione: df7edf52e46092a0102d5edcb3ac4a2373bf22ed.
Commit bot: dc97fcf91a9c39ae4efcd956c64955a3006edcfe, pubblicato il
2026-10-20 alle 23:45:21 CEST. Letto il diff: sola formattazione dei tre file
frontend previsti, nessun cambiamento logico; nessuna modifica ai lockfile.
Non si attribuisce il verde della nuova testa alla prima CI del commit iniziale.

CI della PR 14 sulla testa dc97fcf: run 39502927035, tutta verde.
https://github.com/ale3000ale/Heat-pedal-to-the-roguelike/actions/runs/39502927035

| Job | Esito | Conclusione CEST del 2026-10-20 |
|---|---|---|
| Migrazioni (database di test) | success | 23:56:31 |
| Frontend (check, lint, test, build) | success | 23:57:05 |
| Backend (pytest) | success | 23:58:10 |

La suite include filtro piloti propri/iscritti, campionato chiuso, popup/ack
selettivo, nuovi arrivi in coda, errore che conserva il popup, snapshot vuoto
senza scrittura, fallback/open, 401 e risposta tardiva dopo dispose. Sono prove
con dipendenze simulate, non DOM o browser. Verificati commit, diff ed esiti dei
job, non log completi o conteggi numerici. Nessun comando locale eseguito.

## Riallineamento e seguito

Riallineati PHASE_15.md, note API/servizio/controller, questa nota e DATABASE.md
per la disponibilita' effettiva del campionato. Il nuovo commit documentale
richiede una CI separata. PROJECT_SPEC.md e PROJECT_STATUS.md restano protetti.
Nessuna nuova modifica a codice, workflow, dipendenze, immagini, schema o dati.

Prossimo passo: pagina gara e merge dei soli campi risultati non modificati
localmente, preservando ordine, assenti e sponsor modificati ma non salvati.
Campionato collegato non significa app interamente real-time o rendering,
proxy, deployment e carico verificati. Nessuna prova browser eseguita o richiesta
ora. Avviso e checklist dei test manuali finali dopo il collegamento restante
e la relativa CI verde. Migrazioni sui dati reali ancora non autorizzate.
