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

## File pubblicati nel commit 33b87b8

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

## Verifiche effettive e errore di formattazione

Commit implementativo: 33b87b8b51bc318f02d36938341d3461279dc683.
CI run 39454933814: backend pytest success, migrazioni success, frontend failure.
Il log fornito dall'autore alle 18:22 CEST del 2026-10-20 identifica Prettier:

- src/lib/events/live-refresh.spec.ts
- src/lib/events/live-refresh.svelte.ts
- src/lib/gift-reconcile.spec.ts

npm run lint si ferma su prettier --check; ESLint non e' ancora eseguito in quel
passaggio. Non si dichiarano superati test e build del job fallito.
Il precedente job formatter elencava soltanto i sei file del client iniziale;
non copriva questi tre nuovi file.

## Correzione preparata

Riuso di .github/workflows/format-sse-client.yml, con elenco esclusivo dei tre
file sopra sia per prettier --write/--check sia per git add. Nessuna modifica
alla configurazione, ai plugin, a package.json o al lockfile. Node 22 e npm ci
restano quelli gia' usati dal job. Nessuna modifica logica ai moduli SSE.

Il job esegue lint completo, check, test e build sulla copia formattata prima
di pubblicare il commit bot. Se un controllo fallisce non pubblica; se il ramo
cambia nel frattempo si ferma senza force push. Trigger limitato al ramo fase 15
e alle modifiche del workflow stesso; main e phase-14 non sono coinvolti.
La CI ordinaria del commit che attiva il job puo' ancora fallire sui file non
formattati. Verificare il risultato del job format e l'eventuale nuova testa,
senza presumere che il push bot attivi una nuova CI ordinaria.

Nessun npm, formatter, lint, check, test o build eseguito localmente.
Il nuovo tentativo di formattazione non e' ancora eseguito ne' dichiarato riuscito.
Nessuna pagina, API, dipendenza, migrazione, immagine o database reale modificato.

## Prossimo passo

Dopo approvazione e push, leggere l'esito del job e risolvere eventuali errori
prima del commit 2. Solo dopo controlli riusciti riallineare questa nota e
PHASE_15.md con i risultati reali, conservando PROJECT_SPEC.md e PROJECT_STATUS.md
secondo la decisione della fase. Nessun merge autorizzato.
