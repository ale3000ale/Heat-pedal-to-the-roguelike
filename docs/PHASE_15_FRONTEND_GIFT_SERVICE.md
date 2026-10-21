# Fase 15a-4b - Servizio frontend delle notifiche

Aggiornamento: 2026-10-21. Ramo phase-15-sse-sistemazione, PR 14 in bozza.
Servizio ora usato dalla pagina campionato tramite championship-live.ts:
implementazione df7edf5, testa formattata dc97fcf, CI 39502927035 tutta verde.
Vedi PHASE_15_CHAMPIONSHIP_LIVE.md per il collegamento, non ancora prova browser.

## Contratto del servizio

File gift-notifications-api.ts e .spec.ts. CardGift non contiene pilot_id:
PilotGiftNotification {pilotId, gift} conserva il pilota della REST senza
modificare DTO/backend. fetchGiftNotifications deduplica piloti e legge uno
snapshot completo: errore anche su un solo pilota, incluso 401, rifiuta tutto.
Mai [] fittizi per cancellare notifiche valide.

acknowledgeGiftNotifications riceve lo snapshot gia' mostrato, raggruppa per
pilota, deduplica e invia batch sequenziali di massimo 100 a /seen-selected.
Non usa /seen legacy, non rilegge la coda e non modifica UI/input. Lista vuota:
nessuna richiesta. Tutti gli ID validati prima dell'invio, solo interi positivi
sicuri JavaScript: backend int64 non implica che number li rappresenti tutti.
Nessun bigint o nuovo formato JSON introdotto.

Primo batch fallito interrompe i successivi, ma quelli gia' riusciti possono
restare persistiti. Nessuna atomicita' tra richieste o retry automatico. Ripetere
lo stesso snapshot e' compatibile con l'idempotenza backend. HTTP gia' partite
non cancellate. Il chiamante resta responsabile di selezionare gli ID resi.

## Cronologia verificata

Base 9ea0cb0/CI 39479071828; backend cda06a9. Implementazione
493a3fbde86573ae7373a081e2195972dc7d486d: CI 39491830284 del 2026-10-20,
migrazioni success 22:25:51 CEST, frontend failure 22:25:56, backend success
22:27:25. Log autore 22:43: Prettier sul solo gift-notifications-api.spec.ts;
ESLint non parte dopo prettier --check fallito, test/build del tentativo non
certificati. Correzione workflow ae161cc, bot de29e7000aa5ad9bc6c313817178622b9844f903
alle 23:04:11: diff letto, sola formattazione del test. CI 39497343267 tutta verde:
migrazioni 23:05:19, frontend check/lint/test/build 23:05:42, backend 23:06:47 CEST.

Suite: associazione pilota/DTO, deduplica, completezza, errori e 401, vuoti,
validazione preventiva, endpoint/cookie/corpo, batch 100/100/1 e errore parziale.
Nessun conteggio numerico dei test o log completi dichiarato. Nessun comando locale.

## Uso corrente e limiti

Il blocco iniziale non modificava le pagine; ora championship-live.ts le collega
al servizio e al controller. La pagina campionato non usa piu' il vecchio wrapper
che nasconde errori, anche se le funzioni legacy restano nei loro file.
Il formatter e' ora mirato ai tre file del collegamento campionato, non a quelli
della correzione storica del servizio. Nessuna modifica a dipendenze, lockfile,
immagini, migrazioni o dati. Pagina gara e merge non distruttivo ancora pendenti.

Test del servizio e dell'integrazione non certificano DOM/browser. Avviso manuale
finale dopo collegamento restante e relativa CI verde, come richiesto dall'autore.
PROJECT_SPEC.md e PROJECT_STATUS.md protetti. Questo push riallinea solo documenti,
richiede una CI separata e non autorizza merge o modifiche al database del gioco.
