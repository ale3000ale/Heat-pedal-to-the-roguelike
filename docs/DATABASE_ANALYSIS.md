> **STATO: DOCUMENTO STORICO (fase 1).** Fotografia di `HeatDB.sql` com'era
> prima delle migrazioni Alembic. Non descrive lo schema attuale: per quello
> fanno fede i modelli in `backend/app/db/models/`, le migrazioni in
> `backend/alembic/` e `PROJECT_SPEC.md`. Le differenze elencate nella sezione 6
> sono state in gran parte risolte dalle fasi successive.

# Analisi del database — Heat

Questo documento separa i fatti verificati su `HeatDB.sql` dalle differenze
rispetto al modello target di `PROJECT_SPEC.md`. Non contiene dati inventati.

## 1. Fonte analizzata

- File: `HeatDB.sql`
- Dimensione: 1.503 byte
- Tipo: script SQL DDL (`CREATE TABLE ...`), non un file binario SQLite
- Verifica: lettura integrale del contenuto testuale

## 2. Contenuto verificato

Il file contiene esclusivamente 6 istruzioni `CREATE TABLE IF NOT EXISTS`.
Non contiene `INSERT`, `CREATE INDEX`, `CREATE VIEW`, `PRAGMA` né commenti.
Nessun dato reale è disponibile.

## 3. Schema rilevato

### User

| Colonna | Tipo | Vincoli |
|---|---|---|
| id | INTEGER | NOT NULL, PRIMARY KEY |
| username | TEXT | NOT NULL, UNIQUE |
| password | TEXT | NOT NULL |

### Pilot

| Colonna | Tipo | Vincoli |
|---|---|---|
| id | INTEGER | NOT NULL, PRIMARY KEY |
| name | TEXT | NOT NULL, UNIQUE |
| gold | INTEGER | NOT NULL, DEFAULT 0 |
| sponsor | INTEGER | NOT NULL, DEFAULT 0 |
| point | INTEGER | NOT NULL, DEFAULT 0 |
| championship_id | INTEGER | nullable |
| team | INTEGER | NOT NULL |
| user_id | INTEGER | NOT NULL |

Foreign key: `team` → `Team(id)`; `championship_id` → `"Championship "(id)`
(nome con spazio finale); `user_id` → `User(id)`.

### Deck

| Colonna | Tipo | Vincoli |
|---|---|---|
| id | INTEGER | NOT NULL, PRIMARY KEY |
| cards | TEXT | nullable |
| id_prototype | INTEGER | NOT NULL |

Foreign key: `id_prototype` → `Deck_prototype(id)`.

### "Championship " (nome con spazio finale)

| Colonna | Tipo | Vincoli |
|---|---|---|
| id | INTEGER | NOT NULL, PRIMARY KEY |
| name | TEXT | NOT NULL, UNIQUE |
| pilots | TEXT | nullable |
| deck | INTEGER | nullable |
| date | DATETIME | NOT NULL |

Foreign key: `deck` → `Deck(id)`.

### Team

| Colonna | Tipo | Vincoli |
|---|---|---|
| id | INTEGER | NOT NULL, PRIMARY KEY |
| name | TEXT | NOT NULL, UNIQUE |

### Deck_prototype

| Colonna | Tipo | Vincoli |
|---|---|---|
| id | INTEGER | NOT NULL, PRIMARY KEY |
| base_cards | TEXT | nullable |
| name | TEXT | NOT NULL, UNIQUE |

Tutte le foreign key usano `ON UPDATE NO ACTION ON DELETE NO ACTION`.

## 4. Relazioni presenti nello schema

```text
User (1) ── < user_id (Pilot)
Team (1) ── < team (Pilot)
"Championship " (1) ── < championship_id (Pilot)
Deck_prototype (1) ── < id_prototype (Deck)
Deck (1) ── < deck ("Championship ")
```

Nessuna FK da `Pilot` o `Team` verso `Deck`. Il solo collegamento verso `Deck`
parte da `"Championship "`.

## 5. Anomalie riscontrate (non corrette in `HeatDB.sql`)

1. Nome tabella `"Championship "` con spazio finale; compare nel `CREATE TABLE`
   e nella FK di `Pilot.championship_id`.
2. `Deck.cards` e `Deck_prototype.base_cards` senza vincolo `CHECK`.
3. `Championship.pilots` è TEXT, non una tabella di relazione.
4. Nessuna FK tra `Deck` e `Pilot`.
5. Nessuna tabella per il Negozio.
6. `User` senza ruolo e senza indicazione sul formato di `password`.
7. `Team` senza riferimento a `User`.
8. `Pilot.user_id` senza UNIQUE: coerente con User 1:N Pilot.
9. `Pilot.championship_id` è singolo: lo schema consente un solo campionato
   per pilota, coerente con la regola di `PROJECT_SPEC.md`.

## 6. Differenze rispetto a PROJECT_SPEC.md (risolte con Alembic)

| Modello target | Stato in `HeatDB.sql` |
|---|---|
| Tabella `ChampionshipPilot` | Assente; esiste `Championship.pilots` (TEXT) |
| Tabelle `Race` e `RaceResult` | Assenti |
| Pilot 1:1 Inventario e Pilot 1:1 Mazzo da gioco | `Deck` non collegato a `Pilot` |
| Pool di carte per campionato da `DeckPrototype` | `Championship.deck` → `Deck` → `Deck_prototype` (corrispondenza da confermare) |
| Ruoli (`admin`, `player` e successivi) | `User` senza ruolo |
| User 1:N Team | `Team` senza `user_id` |
| Nome tabella `Championship` | Nome con spazio finale |

## 7. Controllo di Deck.cards

Formato atteso (da `PROJECT_SPEC.md`): array JSON di oggetti
`{"path": "/images/cards/N_nome.ext", "value": N}`.

Nessun dato è verificabile perché il file non contiene `INSERT`. Non sono
riportati conteggi di righe valide, nulle o errate.

## 8. Cosa non è stato verificato

- Contenuto dei dati reali
- Indici oltre a quelli impliciti da `UNIQUE`
- Eventuali vincoli `CHECK` (nessuno presente nel testo)
- Comportamento di `ON DELETE` e `ON UPDATE` diverso da `NO ACTION`
