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
