# Autenticazione, sessioni e ruoli

Questa scheda è una **mappa delle fonti**, non un requisito approvato. Indica dove leggere il
codice e i documenti esistenti; non ne ripete il contenuto e non sostituisce specifiche,
database o verifiche.

## Documenti canonici

- [Indice della KB](../INDICE.md)
- [Backend: autenticazione](../../BACKEND_AUTH.md) — documento storico della fase 5: il blocco
  “Limiti noti” iniziale è superato dal blocco corrente `account-password-current`.
- [Frontend: autenticazione](../../FRONTEND_AUTH.md) — stesso layering storico/corrente.
- [Impostazioni account](../../ACCOUNT_SETTINGS.md) — dettaglio del cambio password.
- [Mappa del codice](../../PROJECT_NOTES.md) — convenzioni e punti di ingresso.
- [Stato del progetto](../../PROJECT_STATUS.md) — avanzamento, non specifica.

Allineamento controllato: i documenti storici dichiarano il proprio carattere e includono blocchi
correnti; non è emersa una contraddizione irrisolta tra essi e il codice letto.

## Perimetro ed esclusioni

**Incluso:** endpoint `/api/auth/*`, cookie `heat_session`, sessioni lato server, ruoli
`admin`/`judge`/`player` e dipendenze FastAPI, gestione utenti admin, cambio password con revoca
delle altre sessioni, store frontend e pagine login/registro/utenti.

**Escluso:** regole di gioco e permessi di giudice in azione (le schede funzionali citano solo il
ruolo richiesto), emissione/consumo di `auth.expired` nel flusso SSE, QR di accesso, dati reali,
schema SQLite effettivo, esecuzione di test.

Questa scheda è proprietaria di: contratto degli endpoint auth, ciclo di vita del cookie e della
sessione, definizione dei ruoli e delle dipendenze `CurrentUser`/`AdminUser`/`JudgeUser`,
cambio password. Le altre schede possono citare questi elementi senza ridescriverli.

## Revisione e stato del worktree esaminati

- Revisione: `21e17e637b43528d7320e88f0af5623db7158ee9`; branch
  `feat/0.9-mappe-eventi` in tracking con `origin/feat/0.9-mappe-eventi`.
- Worktree all'inizio di questa scheda: modificati `AGENTS.md`, `docs/PROJECT_NOTES.md`,
  `docs/PROJECT_STATUS.md`; non tracciate `.agents/skills/codebase-knowledge-builder/` e
  `docs/kb/`. Le modifiche ai tre file tracciati appartengono alle fasi documentali precedenti.
- In questa fase vengono aggiunti solo la scheda e un link in `docs/kb/INDICE.md`.
- Non sono stati eseguiti test, né ispezionato il database reale, né avviati `setup`/`start`.

## Punti d'ingresso e flusso

### API e contratto

- Router auth con prefisso: `backend/app/main.py:65`.
- Registro 201/409 e login 401 aprono la sessione; logout 204; `me` 200/401:
  `backend/app/api/accounts/auth.py:32-39`, `backend/app/api/accounts/auth.py:42-49`,
  `backend/app/api/accounts/auth.py:52-60`, `backend/app/api/accounts/auth.py:63-65`.
- Cambio password 204, con 401/403/409/422 e validazione manuale per non eco delle password:
  `backend/app/api/accounts/auth.py:68-105`.
- DTO di registrazione/login e `UserRead` con i tre ruoli:
  `backend/app/schemas/accounts/auth.py:10-21`, `backend/app/schemas/accounts/auth.py:24-29`.
- DTO segreto del cambio password, `extra="forbid"` e conferma:
  `backend/app/schemas/accounts/password_change.py:7-24`.
- Nome cookie, secure da env e URL del database: `backend/app/config.py:4-10`.

### Dipendenze e ruoli

- Cookie HttpOnly, SameSite=lax, durata da `SESSION_DURATION`, secure configurabile:
  `backend/app/api/deps.py:14-23`; rimozione: `backend/app/api/deps.py:26-33`.
- `get_current_user` → 401 senza sessione valida: `backend/app/api/deps.py:36-46`.
- `require_admin` e `require_judge` (admin più giudice): `backend/app/api/deps.py:49-65`.
- Ruoli assegnabili `player`/`judge`, admin non modificabile:
  `backend/app/services/accounts/roles.py:6`, `backend/app/services/accounts/roles.py:22-34`.
- Endpoint admin utenti e cambio ruolo: `backend/app/api/admin/admin.py:35-50`.

### Servizi e persistenza descritta

- Registrazione crea sempre `player`, username normalizzato, password hashata; login usa un hash
  finto per tempi uniformi: `backend/app/services/accounts/users.py:8`,
  `backend/app/services/accounts/users.py:25-40`, `backend/app/services/accounts/users.py:43-49`.
- Hash password con `pwdlib`: `backend/app/security.py:1-11`.
- Sessione di 7 giorni, token casuale salvato solo come SHA-256, lettura con scadenza, delete e
  purge: `backend/app/services/accounts/sessions.py:10`,
  `backend/app/services/accounts/sessions.py:17-18`,
  `backend/app/services/accounts/sessions.py:21-31`,
  `backend/app/services/accounts/sessions.py:34-41`,
  `backend/app/services/accounts/sessions.py:49-52`.
- Cambio password sotto lock SQLite: rilettura della sessione, verifica della password attuale,
  nuovo hash, revoca delle altre sessioni, commit; rollback e 409 su lock:
  `backend/app/services/accounts/password_changes.py:28-65`.
- Purge delle sessioni scadute all'avvio: `backend/app/main.py:46-49`.
- **Schema descritto** da modelli e migrazione: colonne `user`, `role` con check e `Session` con
  `token_hash` unico e FK a `user.id`:
  `backend/app/db/models/user.py:4-14`, `backend/app/db/models/session.py:9-20`,
  `backend/alembic/versions/3daf355a6ffd_tabella_session.py:21-36`.
- **Schema SQLite effettivo non verificato**: il database reale è fuori perimetro e non è stato
  ispezionato in lettura; quanto sopra è solo ciò che dicono modelli e migrazioni.

### Frontend

- Store `auth`: `init` via `/auth/me`, login, registrazione, logout con pulizia dell'utente anche
  su errore: `frontend/src/lib/auth/auth.svelte.ts:43-58`,
  `frontend/src/lib/auth/auth.svelte.ts:60-81`, `frontend/src/lib/auth/auth.svelte.ts:83-92`.
- `sessionKey` è un metadata locale di lifecycle, non un token né un'autorizzazione; i permessi
  derivano dal ruolo: `frontend/src/lib/auth/auth.svelte.ts:8-23`,
  `frontend/src/lib/auth/auth.svelte.ts:25-33`.
- Form login e registrazione: `frontend/src/routes/login/+page.svelte:17-35`,
  `frontend/src/routes/register/+page.svelte:17-38`.
- Pagina admin utenti con toggle giudice/player e blocco per non admin:
  `frontend/src/routes/admin/users/+page.svelte:22-51`,
  `frontend/src/routes/admin/users/+page.svelte:63-64`.
- Modal impostazioni account: un solo invio, campi puliti dopo la richiesta e alla chiusura,
  risposte tardive ignorate se il modal è smontato o l'account è cambiato:
  `frontend/src/lib/components/shared/account-settings.svelte:11-19`,
  `frontend/src/lib/components/shared/account-settings.svelte:26-53`,
  `frontend/src/lib/components/shared/account-settings.svelte:55-80`.
- Validazione e messaggi d'errore lato client senza retry automatico:
  `frontend/src/lib/auth/password-change.ts:3-34`,
  `frontend/src/lib/auth/password-change-api.ts:4-16`.

## Test individuati (non eseguiti in questa fase)

- `backend/tests/test_auth.py:33-151`: registrazione, ruolo non scegliibile, hash, login, cookie,
  token non in chiaro, logout, scadenza, cascade e guard admin.
- `backend/tests/test_password_change.py:41-119`: sessione conservata e altre revocate, rifiuti
  senza mutazioni, sessioni scadute/revocate, rollback e rilettura sotto lock.
- `frontend/src/lib/auth/auth.spec.ts:27`, `frontend/src/lib/auth/auth-roles.spec.ts:11`,
  `frontend/src/lib/auth/auth-generation.spec.ts:20`,
  `frontend/src/lib/auth/password-change.spec.ts:18`,
  `frontend/src/lib/auth/password-ui.spec.ts:8`: store, permessi, chiave locale, payload/validazione
  e rendering iniziale. `password-ui.spec.ts` non prova interazioni browser.

Nessun test è stato eseguito durante la generazione della scheda.

## Osservato, dedotto e non verificato

- **Osservato:** endpoint, dipendenze, servizi, modelli, migrazione e componenti citati; codici di
  risposta e messaggi presenti nel codice; layering storico/corrente dei documenti canonicali.
- **Dedotto dal codice:** `JudgeUser` include admin e giudice; il cambio password mantiene la
  sessione corrente; `sessionKey` serve a isolare dati locali di draft, non a autorizzare.
- **Non verificato:** esecuzione test, browser, database SQLite reale, effettiva revoca SSE
  `auth.expired`, risultati CI, collaudo manuale.

## Fonti da ricontrollare quando cambiano le fonti pertinenti

Rivalutare solo se cambia una fonte pertinente, non a ogni commit:

- `backend/app/api/accounts/auth.py`, `backend/app/api/deps.py`, `backend/app/api/admin/admin.py`,
  `backend/app/config.py`, `backend/app/main.py`.
- `backend/app/services/accounts/sessions.py`, `backend/app/services/accounts/users.py`,
  `backend/app/services/accounts/password_changes.py`, `backend/app/services/accounts/roles.py`,
  `backend/app/security.py`.
- `backend/app/schemas/accounts/auth.py`, `backend/app/schemas/accounts/password_change.py`.
- `backend/app/db/models/user.py`, `backend/app/db/models/session.py`,
  `backend/alembic/versions/3daf355a6ffd_tabella_session.py`.
- `frontend/src/lib/auth/`, `frontend/src/lib/components/shared/account-settings.svelte`,
  `frontend/src/routes/login/+page.svelte`, `frontend/src/routes/register/+page.svelte`,
  `frontend/src/routes/admin/users/+page.svelte`.
- I test elencati sopra e i documenti canonici linkati all'inizio.
