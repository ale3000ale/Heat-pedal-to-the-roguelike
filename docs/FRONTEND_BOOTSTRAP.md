# Fase 3: Bootstrap frontend

> STATO: COMPLETATA. **DOCUMENTO STORICO**: fotografia del frontend alla fase 3.
> I limiti emersi alla chiusura sono stati risolti durante la Fase 6 (vedi
> FRONTEND_AUTH.md). Le versioni indicate sotto sono quelle di allora: per lo
> stato attuale vedi `PROJECT_STATUS.md` e `frontend/package.json`.

## Stack

- Node.js 24.19.0, npm 11.17.0
- SvelteKit 2.70.3, Svelte 5.57.1
- Vite 8.3.1, TypeScript 6.0.3
- Prettier, ESLint, Vitest (solo test unitari), Tailwind CSS 4
- Adapter: `@sveltejs/adapter-auto`
- Template: SvelteKit minimal, TypeScript, npm

## Posizione

`frontend/` nella radice del progetto `Heat-pedal-to-the-roguelike`.
Nome del pacchetto: `heat-pedal-to-the-roguelike` versione 0.0.1.

## Comandi (dalla cartella frontend/)

    npm install
    npm run dev       (di norma si avvia tutto con `py heat.py` dalla radice)
    npm run check
    npm run lint
    npm run test
    npm run build

Il server di sviluppo gira su `http://127.0.0.1:5173/`.
Il backend gira su `http://127.0.0.1:8000` (vedi `BACKEND_BOOTSTRAP.md`).

## Esiti iniziali (2026-10-01)

| Controllo | Esito |
|---|---|
| `npm run check` | OK: 0 errori, 0 warning |
| `npm run build` | OK (adapter-auto non rileva un ambiente di produzione: normale in locale) |
| `npm run test` | Non eseguibile: script assente |
| `npm run lint` | Fallito: 53 warning Prettier su file generati in `.svelte-kit/` |

## Limiti emersi e risoluzione

| Limite | Risoluzione |
|---|---|
| Vitest non installato | Aggiunto con `npx sv add vitest`, solo test unitari |
| Lint su `.svelte-kit/` | Aggiunto `frontend/.prettierignore` |
| ESLint da verificare | Presente; errore sul `.gitignore` risolto aggiungendo `import { fileURLToPath }` in `eslint.config.js` e usando il `.gitignore` della radice |
| Nessun collegamento col backend | Fatto nella Fase 6 (proxy di Vite) |

## Ancora aperto

- Adapter da definire quando si deciderà come distribuire l'app.
