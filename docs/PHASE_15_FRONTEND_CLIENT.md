# Fase 15a-4a - Client SSE condiviso

Data: 2026-10-20. Ramo phase-15-sse-sistemazione, PR 14 in bozza.
Base 4430d40 con CI verde run 39421574917. Nessun merge autorizzato.

## Perimetro

Otto file iniziali: cinque moduli/test in frontend/src/lib/events, layout radice,
questa nota e PHASE_15.md. Nessuna dipendenza o migrazione aggiunta.
Pagine campionato/gara, revisione, popup e polling non modificati.
Il client e' collegato al layout, ma le schermate non sono ancora sottoscritte.

## Contratto e lifecycle

- Connessione browser same-origin a /api/events/stream dopo auth.ready/user.
  Il cookie resta gestito dal browser; niente token o user_id in URL.
- Tipi dominio allineati a schemas/events.py; messaggi normalizzati e validati.
  Cursori SQLite int64 conservati come stringhe, non Number arrotondati.
- subscribe filtra campionato/gara. Eventi senza race_id invalidano anche
  sottoscrizioni di gara del campionato. resync e auth.expired passano i filtri.
- subscribeStatus espone il trasporto: open non significa snapshot REST pronto.
- Cleanup su logout, cambio utente e smontaggio; callback obsolete invalidate.
  Nessuna coda di eventi, token o cursore salvata nel browser.
- Retry CONNECTING e Last-Event-ID affidati all'EventSource esistente.
  Sorgente CLOSED o factory in errore: nuova apertura dopo 3 secondi.
  La nuova sorgente riparte senza header manuali e riceve resync iniziale.
  Riapertura nativa: invalidazione locale resync/reconnected prudenziale.
- JSON non valido: resync locale invalid_event, senza inoltrare il payload.
- auth.expired: chiusura prima del callback, stato expired, utente locale
  svuotato dal layout e redirect preesistente al login. Non invia logout.
- Errori sincroni/asincroni dei sottoscrittori loggati e isolati.

## Verifiche effettive

Implementazione cb5d649, seguita dalla correzione di formattazione descritta in
PHASE_15_FRONTEND_FORMATTING.md. Commit formattato e verificato:
33f01f0447706cbfe78a7468b4e0c7cb13696deb, autore github-actions[bot].
La modifica del bot riguarda esattamente i sei file segnalati da Prettier.

CI ordinaria della PR 14 sulla testa formattata: run 39425660561.
https://github.com/ale3000ale/Heat-pedal-to-the-roguelike/actions/runs/39425660561

| Job | Esito | Conclusione CEST del 2026-10-20 |
|---|---|---|
| Frontend (check, lint, test, build) | success | 15:03:35 |
| Backend (pytest) | success | 15:04:41 |
| Migrazioni (database di test) | success | 15:03:02 |

Test del client con EventSource simulato: lifecycle, filtri, disiscrizione,
errori dei listener, retry/cleanup, scadenza e messaggi invalidi.
Sono stati verificati gli esiti dei job, non i conteggi numerici dei log.
Nessun npm, formatter, lint, check, test o build eseguito localmente dall'assistente.
Il verde qui registrato non certifica un successivo commit documentale.

## Riscontro manuale e limiti

Il 2026-10-20 alle 15:23 CEST l'autore ha riferito: "ok per ora va tutto".
Registrato come riscontro positivo delle prove svolte finora. Non sono stati
specificati casi eseguiti, browser, ruoli, log, commit locale o database usato.
Non viene quindi dichiarata superata l'intera checklist proposta, ne' una
prova di carico, di durata attraverso il proxy o di deployment online.
Nessuna prova browser eseguita direttamente dall'assistente.

Gli errori HTTP iniziali di EventSource sono opachi al client: non vengono
interpretati come auth.expired. Il fallback REST e la gestione del relativo
401 saranno collegati nel blocco schermate; il polling esistente resta attivo.
La correttezza dei payload specifici delle azioni resta responsabilita' dei
servizi backend: il validatore verifica busta, JSON, cursore e riferimenti.
Non e' ancora una consegna end-to-end real-time.

## Passo successivo

Presentare analisi e file previsti della 15a-4b per approvazione: riletture REST
coalescenti, fallback senza sovrapposizioni, protezione form/bozze locali,
riconciliazione dei regali annullati con popup aperto e gestione 401 REST.
Questo riallineamento non avvia l'implementazione del blocco successivo.
Nessuna modifica a database reale, immagini o documenti grandi protetti.
