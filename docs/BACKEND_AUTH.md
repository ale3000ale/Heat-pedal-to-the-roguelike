STATO: COMPLETATA. DOCUMENTO STORICO della fase 5: gli endpoint e le scelte
restano validi, ma i ruoli sono poi diventati `admin`, `judge` e `player`
(la registrazione crea sempre un `player`) e i test sono molti di più dei 16
citati sotto. Stato attuale in `PROJECT_STATUS.md`.

# Fase 5 - Autenticazione

## Endpoint
- POST /api/auth/register: crea un player, apre la sessione. 201, 409 se username in uso
- POST /api/auth/login: 200, 401 per credenziali errate
- POST /api/auth/logout: elimina la sessione e il cookie. 204, anche senza sessione
- GET /api/auth/me: utente corrente. 200 o 401

## Scelte
- Sessioni lato server nella tabella session. Nel database c'è solo l'hash SHA-256 del token
- Cookie heat_session: HttpOnly, SameSite=lax, Max-Age 7 giorni, Secure da config (False in locale)
- Scadenza fissa a 7 giorni, senza rinnovo
- Password Argon2 (pwdlib). Verifica con hash finto per utenti inesistenti
- Username normalizzato in minuscolo (strip + lower) in schemi e servizi
- La registrazione crea solo player. L'admin nasce con app.scripts.create_admin
- Sessioni scadute eliminate all'avvio (lifespan)
- Host di sviluppo sempre http://127.0.0.1:5173, mai localhost

## File
app/api/auth.py, app/api/deps.py, app/schemas/auth.py,
app/services/sessions.py, app/services/users.py,
app/db/models/session.py, migrazione 3daf355a6ffd,
tests/conftest.py, tests/test_auth.py

## Esiti (alla fase 5)
- 16 test pytest passati, database di prova in memoria
- Verifica manuale con curl.exe: login, me, logout OK

## Limiti noti
- Nessun rate limiting sui tentativi di login
- Nessun cambio password né invalidazione di tutte le sessioni di un utente
- Nessuna protezione CSRF oltre a SameSite=lax
- SESSION_COOKIE_SECURE va messo a True con HTTPS
- Il modello User usa ancora lo stile Column
- Il nome host heat.race e il DNS locale non sono stati affrontati

<!-- account-password-current:start -->
## Impostazioni account e cambio password - 24 ottobre 2026

Su main: clic sul proprio nome apre Impostazioni account. Password attuale e doppio inserimento della nuova; nuova password di 8-128 caratteri, validata anche sul server. La sessione corrente resta attiva con token e scadenza invariati; le altre sessioni dello stesso account vengono revocate. Hash e revoche sono nella stessa transazione con rollback su errore. Gli altri account non cambiano.

Endpoint POST /api/auth/change-password, autenticato, successo 204. Nessuna migrazione o dipendenza nuova. Nessuna modifica al DB reale eseguita dall assistente. Durante l invio niente doppio invio o chiusura ordinaria; campi svuotati dopo la richiesta e alla chiusura. Errori di rete: esito incerto e nessun retry automatico. SSE riusa il controllo periodico delle sessioni.

Riallineamento dopo pytest backend, tipi, lint, test frontend e build riusciti nel runner: run 40114589745, checkout 97653418434af55ff904d36ab75d80fb0e8fe365, formattazione circoscritta applicata prima delle verifiche. Nessun conteggio inventato, test locale o collaudo browser attestato.

Dettagli, limiti e prove: [Impostazioni account](ACCOUNT_SETTINGS.md).
<!-- account-password-current:end -->
