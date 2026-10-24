# Fase 6: Frontend e autenticazione

> STATO: COMPLETATA. **DOCUMENTO STORICO**: descrive il frontend alla fine
> della fase 6 (14 test Vitest di allora). Pagine, popup e test attuali sono in
> `PROJECT_STATUS.md`; i ruoli sono oggi `admin`, `judge` e `player`.

## Stack aggiunto

- Proxy di Vite, client API, stato utente con runes di Svelte 5, pagine di accesso

## Struttura (frontend/src)

- lib/api.ts: funzione api() per tutte le chiamate al backend, classe ApiError
- lib/types.ts: tipi User e Role
- lib/auth.svelte.ts: AuthStore (user, ready, error, login, register, logout, init)
- routes/+layout.svelte: chiama auth.init() all'avvio e mostra "Caricamento" finché non è pronto
- routes/+layout.ts: ssr = false (app solo browser)
- routes/+page.svelte: home protetta con logout
- routes/login e routes/register: form con messaggi di errore

## Scelte

- Proxy di Vite: /api verso http://127.0.0.1:8000, nessun CORS
- Host di sviluppo sempre http://127.0.0.1:5173, strictPort attivo
- Il cookie di sessione è gestito dal browser, il frontend non lo legge mai
- Percorsi interni con resolve() di $app/paths
- Stato condiviso in una classe con campi $state, in un file .svelte.ts
- 401 su /auth/me non è un errore: significa "nessuna sessione"
- Avvio e setup unificati in heat.py (menu interattivo, Windows e Unix)

## Esiti (alla fase 6)

- 14 test Vitest passati (api: 6, auth: 7, esempio: 1)
- check e lint senza errori
- Verifica manuale: login, registrazione, logout, redirect, sessione dopo F5

## Limiti noti

- I form non validano username e password prima dell'invio
- adapter-auto: per la produzione serve un adapter per SPA con pagina di fallback
- Il proxy di Vite esiste solo in sviluppo
- Nessun test sui componenti Svelte

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
