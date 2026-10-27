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
app/api/accounts/auth.py, app/api/deps.py, app/schemas/accounts/auth.py,
app/services/accounts/sessions.py, app/services/accounts/users.py,
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

<!-- account-password-ui-current:start -->
## Aggiornamento grafico impostazioni e login - 24 ottobre 2026

Nel modal Impostazioni account la sezione Cambio password e a scomparsa e inizialmente chiusa a ogni nuova apertura. La chiusura della sezione svuota i campi. In login e nei tre campi del cambio password e disponibile Mostra/Nascondi, indipendente per ogni campo e nascosto inizialmente. La visibilita non viene salvata; il componente dedicato password-input.svelte e riusato nei due contesti. Durante le richieste i controlli relativi sono disabilitati. Backend, API, database e comportamento di revoca delle altre sessioni restano invariati.

Il fallimento Prettier su account-settings.svelte e stato affrontato applicando il formatter del lockfile solo a quel componente. Prima di questo riallineamento sono riusciti sul runner: npm run check, npm run lint, npm test e npm run build. Run 40124870171, checkout fc8d1f301a9350c555e4c4f2ab0d8ff6a7bb89ae, con componente formattato prima delle verifiche. Il successivo commit pubblica quello stile e questi documenti; non e una nuova esecuzione della CI sul commit risultante. Nessun test locale o conteggio inventato.

I test password-ui.spec.ts presenti nel candidato sono controlli di rendering server, non prove interattive di clic, tastiera o browser. Restano da verificare manualmente espansione/richiusura, reset alla riapertura e Mostra/Nascondi nei quattro campi. Nessuna migrazione, nuova dipendenza, modifica al lockfile o operazione sul DB reale.
<!-- account-password-ui-current:end -->
