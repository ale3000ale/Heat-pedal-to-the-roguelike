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

## Errore storico di formattazione

Commit implementativo: 33b87b8b51bc318f02d36938341d3461279dc683.
CI run 39454933814: backend pytest success, migrazioni success, frontend failure.
Il log fornito dall'autore alle 18:22 CEST del 2026-10-20 identifica Prettier:

- src/lib/events/live-refresh.spec.ts
- src/lib/events/live-refresh.svelte.ts
- src/lib/gift-reconcile.spec.ts

In quel tentativo npm run lint si ferma su prettier --check; ESLint non viene
eseguito dopo il fallimento del primo comando della catena. Non si dichiarano
superati test e build del job fallito. Il precedente job formatter elencava
soltanto i sei file del client iniziale e non copriva questi tre nuovi file.

## Correzione pubblicata e verifica della nuova testa

Il commit 96f98efa516f26c6054089305ddd876e953b0e8d aggiorna il job esistente
.github/workflows/format-sse-client.yml con i soli tre percorsi sopra, sia per
prettier --write/--check sia per git add. Configurazione, plugin, package.json
e lockfile invariati. Node 22 e npm ci come nel job precedente.

Il job esegue lint completo, check, test e build sulla copia formattata prima
di pubblicare. Se un controllo fallisce non pubblica; se il ramo cambia si ferma
senza force push. Trigger limitato al ramo fase 15 e al workflow stesso.
main e phase-14 non sono coinvolti.

Commit effettivamente pubblicato da github-actions[bot]:
fb4f128786d74bdcece526f28a8f158fb13374eb, il 2026-10-20 alle 18:27:02 CEST.
Messaggio: style: formatta coordinatore live SSE con Prettier del lockfile.
Verificati i dettagli del commit: modifica esattamente i tre file segnalati.
Nessuna modifica logica prevista nella correzione di formattazione.

Verificata la CI ordinaria sulla testa formattata della PR 14:
https://github.com/ale3000ale/Heat-pedal-to-the-roguelike/actions/runs/39457551822

| Job | Esito | Conclusione CEST del 2026-10-20 |
|---|---|---|
| Migrazioni (database di test) | success | 18:30:41 |
| Frontend (check, lint, test, build) | success | 18:31:14 |
| Backend (pytest) | success | 18:32:17 |

Tutti i job completati con successo; errore Prettier risolto sulla testa fb4f128.
La verifica usa dettagli del commit bot e risultati della CI ordinaria, non
log completi del job format o conteggi numerici dei test. Non si presumeva
che il push bot bastasse ad avviare i check: sono stati letti quelli presenti.

Nessun npm, formatter, lint, check, test o build eseguito localmente dall'assistente.
Nessuna pagina, API, dipendenza, migrazione, immagine o database reale modificato
in questi blocchi. Nessuna prova browser del coordinatore collegato alle schermate:
il collegamento non e' ancora implementato. Il riscontro manuale delle 15:23
riguarda lo stato precedente e non viene esteso a questo blocco.

## Prossimo passo

Commit 1 verificato in CI. Questo riallineamento modifica solo questa nota e
PHASE_15.md; il suo eventuale commit richiede una verifica CI separata.
Prima del commit 2 presentare il perimetro definitivo dei file e dei test per
approvazione. Applicare le due scelte gia' approvate senza perdere modifiche locali
ne' introdurre polling di sicurezza con stream aperto. Conservare PROJECT_SPEC.md
e PROJECT_STATUS.md secondo la decisione della fase. Nessun merge autorizzato.
