# Fase 15a-4b - Strumenti condivisi, commit 1

Data: 2026-10-20. Ramo phase-15-sse-sistemazione, PR 14 in bozza.
Base verificata: 2960c05, CI verde run 39430586035.
Nessun merge autorizzato. Questo blocco non collega ancora le schermate.

## Scelte approvate

- Risultati: nel commit 2 aggiornare soltanto campi non modificati localmente.
  Ordine d'arrivo e non partecipanti richiedono confronto con lo snapshot di base;
  non e' autorizzata una sostituzione indiscriminata del modulo.
- Polling soltanto quando lo stream non e' open. Nessun polling lento di sicurezza
  con stream aperto. Resta il limite del proxy che mantiene open ma trattiene dati.
- L'utente ha approvato il commit 1 separato dal collegamento delle schermate.

## File preparati

- events/refresh-coalescer.ts e .spec.ts: una sola lettura in corso, invalidazioni
  accorpate in un flag, scarto del risultato superato e nessuna applicazione dopo
  dispose. Errori osservabili tramite callback, successivo tentativo consentito.
- events/live-refresh.svelte.ts e live-refresh.spec.ts: lettura iniziale, eventi
  filtrati, resync, timer solo senza stream open. Il prossimo timer viene programmato
  dopo il completamento della lettura di fallback, non con setInterval sovrapposti.
  Il modulo non usa rune: e' un coordinatore con lifecycle esplicito e testabile.
  Non crea EventSource: riusa subscribe/subscribeStatus del client gia' verificato.
  Il 401 ferma timer/coda/sottoscrizioni prima del callback onUnauthorized.
  auth.expired ferma il coordinatore; l'autenticazione resta gestita dal layout.
- gift-reconcile.ts e .spec.ts: funzione pura per regali visibili ancora validi e
  nuovi regali in attesa, sulla base di uno snapshot REST completo riuscito.
  Non invia richieste /seen e non marca automaticamente le notifiche nuove.

La lettura load deve essere priva di effetti UI; solo apply modifica la vista.
Il chiamante deve fare dispose su cambio campionato/gara/utente e smontaggio.
Un errore di lettura non deve essere convertito in uno snapshot vuoto dei regali.
Per questo il wrapper attuale che ignora gli errori per pilota va rivisto nel
commit 2 prima di usarlo per riconciliare il popup.

## Limite delle notifiche viste

L'endpoint attuale marca tutte le notifiche non viste del pilota, non singoli id.
Questo blocco non cambia il backend ne' risolve l'ack selettivo dei regali nuovi
arrivati durante il popup. Nessuna promessa di exactly-once per i popup.
Il collegamento e la chiusura automatica del popup richiedono una gestione esplicita
che non chiami /seen quando il popup si svuota per annullamento remoto.

## Verifiche e prossimo passo

Riletti contratto degli eventi e CardGift; verificata la testa della PR.
Sei file di codice/test nuovi e questa nota. Nessuna pagina o API modificata.
Nessuna dipendenza, migrazione, immagine o database reale toccato.
Nessun npm, formatter, lint, check, test o build eseguito localmente.
I test sono preparati ma il nuovo blocco non e' ancora verificato in CI.
Prima del commit 2 leggere lint/check/test/build e risolvere eventuali errori.
Dopo la CI riallineare questa nota e PHASE_15.md con gli esiti reali, conservando
PROJECT_SPEC.md e PROJECT_STATUS.md secondo la decisione della fase.
Il job formatter esistente elenca solo i sei file del precedente client SSE:
non formatta automaticamente questi nuovi file, e non viene dichiarato eseguito.
