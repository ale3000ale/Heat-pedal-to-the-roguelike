# Stato del progetto — Heat

Ultimo aggiornamento: 2026-10-04

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
| 8 | Frontend funzionale dell'applicazione | Da iniziare |
| 9 | Negozio e pacchetti di carte | Rinviata |

## Backend completato

- FastAPI, SQLAlchemy 2.0, Alembic e SQLite in `backend/`.
- Autenticazione con password hashate e cookie di sessione httpOnly.
- Ruoli `admin` e `player`; registrazione libera e primo admin creato con setup.
- Team e piloti con nomi unici senza distinguere maiuscole, rinomina ed eliminazione logica.
- Un pilota può non avere un team, ma deve averne uno per iscriversi a un campionato.
- Ogni pilota possiede inventario e mazzo da gioco indipendenti.
- Gestione e validazione delle carte JSON, inclusa la preparazione e il ridimensionamento delle immagini.
- Pool `default` e pool derivate dalla base, create dall'admin scegliendo carte e numero di copie.
- Creazione dei campionati con copia indipendente della pool scelta; chiusura forzabile dall'admin.
- Iscrizione ai campionati con reset di inventario, mazzo, gold, sponsor e punti.
- Gare numerate automaticamente, risultati correggibili e punti 9-6-4-3-2-1, poi 0.
- In ogni gara, gli iscritti assenti compaiono a 0 punti senza una riga `RaceResult`.
- Classifica live per i campionati attivi e classifica congelata per quelli chiusi.
- Cancellazione di un campionato chiuso con gare, risultati, iscrizioni, classifica finale e copia della pool.
- Admin: gestione degli elementi nascosti, eliminazione definitiva manuale e pulizia automatica dopo 365 giorni.

## Qualità verificata

- Suite backend: `138 passed`.
- Migrazioni Alembic applicate e schema aggiornato fino alla tabella `championship_standing`.
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

- `PROJECT_SPEC.md`: specifiche funzionali aggiornate.
- `DATABASE_ANALYSIS.md`: analisi dello schema iniziale.
- `BACKEND_BOOTSTRAP.md`: dettagli del bootstrap backend.
- `OPEN_QUESTIONS.md`: decisioni ancora rinviate.

## Prossimi passi

1. Aggiornare il frontend SvelteKit per collegarlo alle API già disponibili.
2. Creare login, dashboard, gestione team e piloti, pagine campionati, gare e classifica.
3. Creare il pannello admin per pool, chiusura campionati, risultati e pulizia.
4. Lasciare il negozio come placeholder finché non saranno definite le regole di pacchetti, prezzi e sponsor.