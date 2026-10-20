# Fase 15a-4a - Client SSE condiviso

Data: 2026-10-20. Ramo phase-15-sse-sistemazione, PR 14 in bozza.
Base 4430d40 con CI verde run 39421574917. Nessun merge autorizzato.

## Perimetro

Otto file: cinque moduli/test in frontend/src/lib/events, layout radice,
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

## Verifiche e limiti

Riletti layout, autenticazione, protocollo backend, configurazione e test.
Test scritti con EventSource simulato: lifecycle, filtri, disiscrizione,
errori dei listener, retry/cleanup, scadenza e messaggi invalidi.
Test, formatter, lint, check e build non eseguiti localmente.
CI del nuovo blocco da verificare dopo push; il verde della base non basta.
Nessuna prova browser, proxy di lunga durata o backend online eseguita.
Gli errori HTTP iniziali di EventSource sono opachi al client: non vengono
interpretati come auth.expired. Il fallback REST e la gestione del relativo
401 saranno collegati nel blocco schermate; il polling esistente resta attivo.
La correttezza dei payload specifici delle azioni resta responsabilita' dei
servizi backend: il validatore verifica busta, JSON, cursore e riferimenti.
Non e' ancora una consegna end-to-end real-time.

## Passo successivo

Verificare CI e riallineare queste note. Poi approvare 15a-4b: riletture REST
coalescenti, fallback senza sovrapposizioni, protezione form/bozze locali,
riconciliazione dei regali annullati con popup aperto e gestione 401 REST.
Nessuna modifica a database reale, immagini o documenti grandi protetti.
