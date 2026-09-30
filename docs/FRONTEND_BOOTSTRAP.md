# Fase 3: Bootstrap frontend

> STATO: COMPLETATA CON LIMITI (Vitest assente, lint da sistemare: vedi "Limiti noti").

## Stack

- Node.js 24.19.0, npm 11.17.0
- SvelteKit 2.70.3, Svelte 5.57.1
- Vite 8.3.1
- TypeScript 6.0.3
- Prettier (configurato dallo scaffold)
- Adapter: `@sveltejs/adapter-auto`
- Template: SvelteKit minimal, TypeScript, npm

## Posizione

`frontend/` nella radice del progetto `Heat-pedal-to-the-roguelike`.
Nome del pacchetto: `heat-pedal-to-the-roguelike` versione 0.0.1.

## Comandi (dalla cartella frontend/)

```bat
npm install
npm run dev
npm run check
npm run build
npm run lint
```

Il server di sviluppo gira su `http://localhost:5173/`.
Il backend gira separatamente su `http://127.0.0.1:8000` (vedi `BACKEND_BOOTSTRAP.md`).

## Esiti (2026-10-01)

| Controllo | Esito |
|---|---|
| `npm run check` | OK: 0 errori, 0 warning |
| `npm run build` | OK (l'adapter auto segnala che non rileva un ambiente di produzione: normale in locale) |
| `npm run test` | Non eseguibile: lo script `test` non esiste |
| `npm run lint` | Fallito: 53 warning Prettier, tutti su file generati in `.svelte-kit/` |

## Limiti noti

- **Vitest non installato**: manca lo script `test` e il pacchetto `vitest`,
  anche se `PROJECT_SPEC.md` lo prevede. Da aggiungere con `npx sv add vitest`.
- **Lint**: `prettier --check .` controlla anche `.svelte-kit/` (file generati).
  Da risolvere escludendo `.svelte-kit/` in `.prettierignore`.
- **ESLint**: presenza da verificare con `npm ls eslint`. Lo script `lint`
  esegue oggi solo Prettier.
- Nessuna pagina applicativa: solo lo scaffold minimal.
- Nessun collegamento con il backend: previsto nella Fase 5.
- Adapter da definire quando si deciderà come distribuire l'app.

## Da fare in seguito

1. Aggiungere Vitest e rendere `npm run test` eseguibile.
2. Sistemare `.prettierignore` e rendere `npm run lint` pulito.
3. Verificare o aggiungere ESLint.