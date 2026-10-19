# Fase 15 - SSE in tempo reale e sistemazione

Data: 2026-10-20. Ramo: `phase-15-sse-sistemazione` (da `main`, commit `2cded6d`).
Stato: **piano concordato con l'autore, nessun codice scritto**. Questo documento raccoglie
le decisioni e ciò che non è stato riallineato in `PROJECT_SPEC.md` e `PROJECT_STATUS.md`
(troppo grandi per essere riscritti in blocco).

## 1. Sottofasi

| Sotto-fase | Contenuto | Stato |
|---|---|---|
| 15a | Backend e frontend in tempo reale con SSE | Da avviare (serve approvazione dei file e dello schema) |
| 15b | Sistemazione generale (elenco in sezione 4) | Da definire con l'autore dopo la 15a |

## 2. Decisioni dell'autore (2026-10-20)

1. **Uso online**: l'applicazione deve poter funzionare online in ogni momento. L'affluenza sarà bassa e
   sarà usata solo dall'autore e dai suoi amici. Un bus di eventi solo in memoria non basta.
2. **Eventi**: tutti quelli proposti: carta ottenuta (tasto S), stato della gara (in corso, in revisione,
   confermata), carte giocate e annullate, risultati e classifica.
3. **Polling**: resta come ripiego se l'SSE non è disponibile; `card_poll_seconds` e il suo campo nelle
   impostazioni generali restano. La rimozione è rinviata a qualche versione successiva.
4. **Scadenza della revisione**: aggiungere un timer in background nel backend, oltre alla conferma
   alla prima richiesta (`settle_expired_reviews`), che resta come rete di sicurezza.
5. **Rete**: chiamate dirette del frontend al backend; la scelta va verificata sul codice
   (client API del frontend) prima di scrivere.
6. **Rami**: si lavora solo su `phase-15-sse-sistemazione`. Dopo il primo push si apre una pull request
   provvisoria per far partire la CI; non si unisce senza richiesta esplicita.

## 3. Piano tecnico proposto per la 15a (da approvare)

Proposta dell'assistente, non ancora approvata nel dettaglio:

- Tabella `event_log` nel database (id crescente, tipo, campionato, pilota o utente destinatario, dati JSON,
  data), scritta nella stessa transazione dell'azione che genera l'evento. Ogni connessione SSE legge
  gli eventi con id maggiore dell'ultimo inviato; `Last-Event-ID` gestisce la riconnessione.
  Così funziona anche con più worker. Richiede una **migrazione Alembic** e un **backup del database prima**.
- `services/event_log.py` (scrittura, lettura, pulizia degli eventi vecchi), `api/events.py`
  (`GET /api/events/stream`, autenticato con il cookie di sessione, con keep-alive), `schemas/events.py`.
- Timer in background avviato dal `lifespan` di `main.py`, che conferma le revisioni scadute; con più
  worker deve essere sicuro se eseguito due volte (operazione idempotente).
- Punti che pubblicano eventi: `card_gift`, `card_play`, `card_play_close`, `card_judge`, `race_review`, `races`.
- Frontend: `lib/event-stream.svelte.ts` (EventSource con riconnessione e ripiego sul polling),
  `lib/event-types.ts`, test; `card-poll.svelte.ts` resta come ripiego.
- Test: backend (eventi, riconnessione, autorizzazioni, timer) e frontend; CI sulla pull request provvisoria.
- Limite SQLite: una sola scrittura alla volta; le letture periodiche delle connessioni SSE vanno misurate.

Domande ancora aperte prima di scrivere codice:
- Schema esatto di `event_log` e durata di conservazione degli eventi.
- Chi riceve quali eventi (per pilota, per campionato, solo admin e giudici per la revisione).
- Intervallo di lettura della tabella per ogni connessione.

## 4. Da riallineare (non fatto in questa sessione)

Voci raccolte dalla lettura dei documenti; non verificate sul codice se non indicato.

- `PROJECT_STATUS.md`: la riga 14 dice ancora "Da definire a fine fase 13" mentre la fase 14 è unita
  in `main` (PR #13, 2026-10-19); manca la riga 15; l'intestazione riporta "Ultimo aggiornamento: 2026-10-18";
  la descrizione della 13e non riporta nomi di file, rotte e limiti (il testo stesso dice di prenderli dal codice).
- `PROJECT_SPEC.md`: resta da rileggere dopo il commit `bc0fbfb` (refuso nella sezione 14, indicato in PR #6).
- `PHASE_14_POST_MERGE.md`: indica `main` a `aae6c33`; oggi `main` è a `2cded6d`, quindi il dato è storico.
  L'esito del workflow `format-championships.yml` su `main` non è stato letto.
- `SHOP_DESIGN.md`, `PROJECT_NOTES.md`, `SETUP.md`, `SCRIPTS.md`, `DATABASE.md`, `README.md`: non riletti in questa sessione.
  `SETUP.md` e `SCRIPTS.md` (PR #12) dichiarano nessun backup prima delle migrazioni e nessun reset sicuro:
  rilevante per la migrazione di `event_log`.
- Uso online (rinviato in `OPEN_QUESTIONS.md` a dopo la 14): ora anticipato dalla fase 15; vedi sezione 2.

## 5. Regole di lavoro

Ogni modifica, a fine lavoro e a test verdi, richiede il riallineamento di tutti i documenti, come da istruzioni del progetto.
Il riallineamento completo di `PROJECT_SPEC.md` e `PROJECT_STATUS.md` è un lavoro a parte, da fare a pezzi.
