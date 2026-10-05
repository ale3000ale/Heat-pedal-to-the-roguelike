# Stato del progetto — Heat

Ultimo aggiornamento: 2026-10-05

## Fasi

| Fase | Contenuto | Stato |
|---|---|---|
| 1-2 | Analisi, specifiche, schema database | Completate |
| 3 | Bootstrap frontend: SvelteKit minimal, TypeScript, npm, ESLint, Prettier, Vitest | Completata |
| 4 | Backend FastAPI, modelli SQLAlchemy, migrazioni Alembic, SQLite | Completata |
| 5 | Autenticazione: registrazione, login, logout, sessioni httpOnly, ruoli | Completata |
| 6 | Team, piloti, mazzi, inventario e immagini carte | Completata |
| 7.6 | Pool derivate e campionati | Completata |
| 7.6b | Cancellazione dei campionati chiusi | Completata |
| 7.7 | Gare, risultati e classifica live | Completata |
| 7.8 | Pulizia amministrativa e automatica di team e piloti nascosti | Completata |
| 7.9 | Classifica finale congelata dei campionati chiusi | Completata |
| 7.10 | Ruolo giudice e punti sponsor nei risultati | Completata |
| 8a | Frontend: login, registrazione, team, piloti, campionati, gare, classifica, utenti e ruoli | Completata |
| 8b | Backend: due pool di base (modifiche e sponsor), ricarica delle pool, seconda pool sul campionato | In corso (modelli e migrazione fatti; servizi e router da fare) |
| 8c | Frontend admin: pool con ricarica, creazione, chiusura e cancellazione dei campionati | Da fare |
| 8d | Frontend: costruzione del mazzo da gioco dall'inventario | Da fare |
| 8e | Frontend admin: pulizia di team e piloti nascosti | Da fare |
| 9 | Negozio e pacchetti di carte | Rinviata (regole da definire) |

## Backend

- FastAPI, SQLAlchemy 2.0, Alembic e SQLite in `backend/`.
- Autenticazione con password hashate e cookie di sessione httpOnly.
- Ruoli `admin`, `judge` e `player`; registrazione libera e primo admin creato con setup.
- Team e piloti con nomi unici senza distinguere maiuscole, rinomina ed eliminazione logica.
- Un pilota può non avere un team, ma deve averne uno per iscriversi a un campionato.
- Ogni pilota possiede inventario e mazzo da gioco indipendenti.
- Gestione e validazione delle carte JSON, inclusa la preparazione e il ridimensionamento delle immagini.
- Pool `default` (modifiche), pool `sponsor` (nuova, vuota) e pool derivate create dall'admin.
- Creazione dei campionati con copia indipendente della pool scelta; chiusura forzabile dall'admin.
- Iscrizione ai campionati con reset di inventario, mazzo, gold, sponsor e punti.
- Gare numerate automaticamente, risultati correggibili (solo admin) e punti 9-6-4-3-2-1, poi 0, con punti sponsor inseriti a mano.
- In ogni gara, gli iscritti assenti compaiono a 0 punti senza una riga `RaceResult`.
- Classifica live per i campionati attivi e classifica congelata per quelli chiusi.
- Cancellazione di un campionato chiuso con gare, risultati, iscrizioni, classifica finale e copia della pool.
- Admin: gestione degli elementi nascosti, eliminazione definitiva manuale e pulizia automatica dopo 365 giorni.

## Qualità verificata

- Ultima suite backend registrata: `138 passed` (prima delle modifiche alle due pool: da rieseguire).
- Migrazioni Alembic fino a `e5b9c3d7a2f8` (tipo della pool e pool sponsor).
- Test dedicati ad autenticazione, carte, immagini, nomi, team, piloti, campionati, pool, gare, classifiche e pulizia.

## API principali

| Area | Prefisso |
|---|---|
| Autenticazione | `/api/auth` |
| Team | `/api/teams` |
| Piloti | `/api/pilots` |
| Pool | `/api/pools` |
| Campionati, iscrizioni, gare e classifica | `/api/championships` |
| Amministrazione e pulizia | `/api/admin` |
| Salute del servizio | `/health` |

## Documenti

- `PROJECT_SPEC.md`: specifiche funzionali (fonte delle regole).
- `PROJECT_NOTES.md`: mappa del codice, comandi, convenzioni e questioni aperte.
- `DATABASE_ANALYSIS.md`: analisi dello schema iniziale.
- `BACKEND_BOOTSTRAP.md`, `BACKEND_AUTH.md`, `FRONTEND_BOOTSTRAP.md`, `FRONTEND_AUTH.md`: dettagli dei bootstrap e dell'autenticazione.
- `OPEN_QUESTIONS.md`: decisioni ancora rinviate.

## Prossimi passi

1. Fase 8b: servizi e router per due pool di base, ricarica che aggiunge soltanto, campionato con due pool, test.
2. Fase 8c: pannello admin per pool (con ricarica) e campionati (creazione, chiusura, cancellazione).
3. Fasi 8d e 8e: mazzo da gioco e pulizia dei nascosti.
4. Fase 9: negozio e pacchetti, solo dopo aver definito regole, prezzi e uso degli sponsor.
