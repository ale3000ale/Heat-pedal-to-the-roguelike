# Database, migrazioni e concorrenza

Mappa delle fonti, non requisito approvato: non ripete i documenti tecnici e non certifica lo
stato del database reale.

## Documenti canonici

- [Indice della KB](../INDICE.md)
- [Database](../../DATABASE.md) — schema descritto dai modelli, con blocchi storici; le note
  “testa Alembic `d6f0a4b8c2e7`” risalgono a fasi precedenti.
- [Analisi del database](../../DATABASE_ANALYSIS.md) — dichiara esplicitamente di descrivere lo
  schema **pre-migrazione**, non quello attuale.
- [Mappa del codice](../../PROJECT_NOTES.md) — regole di lavoro e comandi.
- [Stato del progetto](../../PROJECT_STATUS.md)
- [Concorrenza fase 15](../../PHASE_15_CONCURRENCY.md) — cronologia, non specifica corrente.

Allineamento controllato: `DATABASE_ANALYSIS.md` è marcato come storico e `DATABASE.md` separa i
blocchi per fase; la testa attuale va letta nei file di migrazione, non in quelle note.

## Perimetro ed esclusioni

**Incluso:** configurazione SQLite, engine e sessioni Alembic/SQLAlchemy, catena delle migrazioni,
modelli come **schema descritto**, lock condiviso di scrittura, blocchi ottimistici e traduzione
dei conflitti nei servizi che li usano.

**Escluso:** ispezione del file `backend/heat.db`, backup o operazioni sui dati, regole di gioco,
singoli servizi applicativi (citati solo come utenti del lock), esecuzione di test o migrazioni.

Questa scheda è proprietaria di: configurazione del database, catena Alembic, convenzioni di
schema e lock/versioni. Le altre schede citano le colonne che usano e linkano qui il meccanismo.

## Revisione e stato del worktree esaminati

- Revisione: `21e17e637b43528d7320e88f0af5623db7158ee9`; branch
  `feat/0.9-mappe-eventi` in tracking con `origin/feat/0.9-mappe-eventi`.
- Worktree: tre file tracciati già modificati nelle fasi documentali precedenti e due directory
  non tracciate; in questa fase si aggiungono solo la scheda e un link all'indice.
- Non sono state eseguite migrazioni, né letta qualsiasi istanza SQLite reale, né avviato
  `setup`/`start`.

## Punti d'ingresso e flusso

### Configurazione e migrazioni

- URL hardcoded `sqlite:///./heat.db` e nome+cookie della sessione in
  `backend/app/config.py:4-10`; i comandi backend girano con cwd `backend/`, ma il percorso
  effettivo del file non è stato verificato.
- Engine, `SessionLocal`, PRAGMA `foreign_keys=ON` e dipendenza `get_db`:
  `backend/app/db/session.py:6-23`.
- Alembic usa `DATABASE_URL`, metadata dei modelli e `render_as_batch=True`:
  `backend/alembic/env.py:6-16`, `backend/alembic/env.py:31-44`.
- Catena letta da `backend/alembic/versions/`: radice `3201b138ce2e` (`down_revision=None`) in
  `backend/alembic/versions/3201b138ce2e_schema_iniziale.py:15-16`; testa `b8f4e2a1c7d9` in
  `backend/alembic/versions/b8f4e2a1c7d9_next_race_setup.py:5-6` (nessuna migrazione successiva
  lo dichiara come `down_revision`). Il file conta 24 revisioni, inclusa un'unione con due padri
  in `backend/alembic/versions/b2d6f0a4c8e1_unione_teste_negozio.py:11-12`.
- Il confronto migrazioni/modelli usa un database temporaneo e verifica tabelle e colonne:
  `backend/tests/test_migrations.py:14-33`. Non è stato eseguito.

### Schema descritto (non schema effettivo)

- Modelli: `backend/app/db/models/` con 12 file di tabella; `Deck.cards` è testo JSON e
  `version` è `version_id_col`: `backend/app/db/models/deck.py:14-24`.
- Anche `Draft` ha un `version_id_col`: `backend/app/db/models/draft.py:17-26`.
- Esempio di DDL descritto da migrazione: tabella `session`, FK con `CASCADE` e indici:
  `backend/alembic/versions/3daf355a6ffd_tabella_session.py:21-36`.
- **Schema SQLite effettivo: non verificato.** Nessuna ispezione in lettura del database reale è
  stata fatta: quanto sopra è evidenza da codice e migrazioni, non dal file SQLite.

### Lock e conflitti

- `acquire_sqlite_write_lock` richiede sessione senza modifiche pendenti, solo dialetto SQLite,
  `BEGIN IMMEDIATE` o promozione con `UPDATE ... WHERE 0`, poi `expire_all()`; nessun retry
  interno: `backend/app/services/core/sqlite_write_lock.py:9-28`.
- Il blocco ottimistico di `Deck` solleva `StaleDataError` su scrittura concorrente:
  `backend/app/db/models/deck.py:20-24`; test dedicato:
  `backend/tests/test_deck_versioning.py:12`.
- `move_card` acquisisce il lock prima delle letture, ritenta solo `StaleDataError` e traduce
  busy/lock in `ConcurrentUpdateError`: `backend/app/services/pilots/pilot_deck.py:107-152`.
- Altri utenti del lock: salvataggio carte admin, draft, acquisti shop, avvio gara, chiusura
  campionato, cambio password e setup gara. Esempi:
  `backend/app/services/cards/admin_pilot_card_save.py:25`,
  `backend/app/services/draft/draft_transaction.py:78`,
  `backend/app/services/shop/shop_purchase.py:98`,
  `backend/app/services/championship/championships.py:158`,
  `backend/app/services/accounts/password_changes.py:41`,
  `backend/app/services/championship/race_setup.py:65`.
- Traduzione HTTP dei conflitti di draft:
  `backend/app/api/draft/draft_errors.py:55-57`.

## Test individuati (non eseguiti in questa fase)

- `backend/tests/test_migrations.py:14-33` — upgrade su database temporaneo e confronto con i
  modelli.
- `backend/tests/test_deck_versioning.py:12` — conflitto di versione su mazzo.
- `backend/tests/test_admin_pilot_card_save.py:197` — due salvataggi concorrenti.
- `backend/tests/test_race_start_write_lock.py:1` — lock occupato all'avvio gara.
- `backend/tests/test_review_concurrency.py:56` — chiusure concorrenti della revisione.
- `backend/tests/test_race_start_readiness.py:115` — lock occupato tradotto in conflitto HTTP.

Nessuno di essi è stato eseguito; i conteggi riportati in altre fasi non vengono qui dichiarati.

## Osservato, dedotto e non verificato

- **Osservato:** URL, engine, PRAGMA, configurazione Alembic, revisioni lette, testo del lock,
  versioni ORM, chiamate al lock e test individuati.
- **Dedotto dal codice:** la testa Alembic è `b8f4e2a1c7d9`; le operazioni che rileggono stato
  prima di scrivere usano il lock condiviso; i retry sono deliberatamente limitati.
- **Non verificato:** database SQLite reale, indici effettivi, esito di upgrade/downgrade,
  backup, esecuzione test, CI e comportamento sotto carico.

## Fonti da ricontrollare quando cambiano le fonti pertinenti

- `backend/app/config.py`, `backend/app/db/session.py`, `backend/alembic/env.py`,
  `backend/app/db/models/`, `backend/alembic/versions/`.
- `backend/app/services/core/sqlite_write_lock.py` e i servizi che lo chiamano elencati sopra.
- `backend/tests/test_migrations.py`, `backend/tests/test_deck_versioning.py`,
  `backend/tests/test_admin_pilot_card_save.py`, `backend/tests/test_race_start_write_lock.py`,
  `backend/tests/test_review_concurrency.py`, `backend/tests/test_race_start_readiness.py`.
- I documenti canonici linkati all'inizio. In caso di nuova migrazione, aggiornare la testa qui
  citata; in caso di ispezione autorizzata del database reale, aggiornare solo dopo averla letta.
