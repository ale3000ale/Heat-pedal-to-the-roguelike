# Stato del progetto — Heat

Ultimo aggiornamento: 2026-10-01

## Fasi

| Fase | Contenuto | Stato |
|---|---|---|
| 1-2 | Analisi, specifiche, schema database | Completate |
| 3 | Bootstrap frontend (SvelteKit minimal, TypeScript, npm, ESLint, Prettier, Vitest) | Completata |
| 4 | Backend FastAPI, modelli SQLAlchemy, migrazioni Alembic | Completata (2026-10-01) |
| 5 | Autenticazione e API | Da iniziare |

## Fase 4 in sintesi

- Backend in `backend/` con FastAPI, SQLAlchemy 2.0, Alembic e SQLite.
- 9 tabelle create dalla migrazione iniziale, verificate con upgrade e downgrade.
- Primo admin e prototipo `default` creati con script dedicati.
- Dettagli in `BACKEND_BOOTSTRAP.md`.

## Documenti

- `PROJECT_SPEC.md`: specifiche definitive
- `DATABASE_ANALYSIS.md`: analisi dello schema
- `OPEN_QUESTIONS.md`: domande rinviate
- `BACKEND_BOOTSTRAP.md`: dettagli della Fase 4

## Prossimi passi

1. Fase 5: registrazione, login con cookie di sessione httpOnly, logout, utente
   corrente, controllo dei ruoli.
2. Raccogliere l'elenco reale delle carte per la pool di `DeckPrototype`.