> **STATO: BOZZA NON APPROVATA.** Questo documento riporta esclusivamente informazioni verificate realmente sul file `HeatDB.sql` fornito. Non contiene correzioni, deduzioni non verificabili né dati inventati. In attesa di risposte alle domande aperte (vedi `OPEN_QUESTIONS.md`) prima di poter essere considerato definitivo.

# Analisi del database — Heat

## 1. Fonte analizzata

- File: `HeatDB.sql`
- Dimensione: 1.503 byte
- Tipo reale: script SQL DDL (`CREATE TABLE ...`), **non** un file binario SQLite (`.db`/`.sqlite`)
- Metodo di verifica: lettura integrale del contenuto testuale del file, eseguita più volte con richieste diverse per confermare la completezza del contenuto restituito

## 2. Contenuto verificato

Il file contiene **esclusivamente 6 istruzioni `CREATE TABLE IF NOT EXISTS`**. Non contiene:

- istruzioni `INSERT` (quindi nessun dato reale è disponibile)
- istruzioni `CREATE INDEX`
- istruzioni `CREATE VIEW`
- istruzioni `PRAGMA`
- commenti SQL

## 3. Schema rilevato

### Tabella `User`

| Colonna | Tipo | Vincoli |
|---|---|---|
| id | INTEGER | NOT NULL, PRIMARY KEY |
| username | TEXT | NOT NULL, UNIQUE |
| password | TEXT | NOT NULL |

Nessun campo di ruolo, permesso o timestamp. Nessuna indicazione nello schema se `password` contenga un valore già hashato.

### Tabella `Pilot`

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

Foreign key:
- `team` → `Team(id)` (ON UPDATE/DELETE NO ACTION)
- `championship_id` → `"Championship "(id)` (ON UPDATE/DELETE NO ACTION) — nota lo spazio finale nel nome della tabella referenziata
- `user_id` → `User(id)` (ON UPDATE/DELETE NO ACTION)

Nessun vincolo `UNIQUE` su `user_id`: lo schema non impedisce che un utente abbia più piloti.

### Tabella `Deck`

| Colonna | Tipo | Vincoli |
|---|---|---|
| id | INTEGER | NOT NULL, PRIMARY KEY |
| cards | TEXT | nullable |
| id_prototype | INTEGER | NOT NULL |

Foreign key:
- `id_prototype` → `Deck_prototype(id)` (ON UPDATE/DELETE NO ACTION)

Nessun `CHECK` a livello database sul contenuto di `cards`. Nessun FK da `Pilot` o `Team` verso `Deck`: l'unico collegamento verificato verso `Deck` proviene dalla tabella `"Championship "` (colonna `deck`).

### Tabella `"Championship "` (nome con spazio finale, verificato letteralmente nel file)

| Colonna | Tipo | Vincoli |
|---|---|---|
| id | INTEGER | NOT NULL, PRIMARY KEY |
| name | TEXT | NOT NULL, UNIQUE |
| pilots | TEXT | nullable |
| deck | INTEGER | nullable |
| date | DATETIME | NOT NULL |

Foreign key:
- `deck` → `Deck(id)` (ON UPDATE/DELETE NO ACTION)

La colonna `pilots` è di tipo `TEXT`, non una tabella ponte: la relazione campionato↔piloti non è espressa con vincoli referenziali nello schema.

### Tabella `Team`

| Colonna | Tipo | Vincoli |
|---|---|---|
| id | INTEGER | NOT NULL, PRIMARY KEY |
| name | TEXT | NOT NULL, UNIQUE |

Nessun'altra colonna presente nello schema fornito.

### Tabella `Deck_prototype`

| Colonna | Tipo | Vincoli |
|---|---|---|
| id | INTEGER | NOT NULL, PRIMARY KEY |
| base_cards | TEXT | nullable |
| name | TEXT | NOT NULL, UNIQUE |

Nessuna indicazione nello schema sul formato interno di `base_cards`.

## 4. Diagramma delle relazioni verificate

```
User (1) ── < user_id (Pilot)
Team (1) ── < team (Pilot)
"Championship " (1) ── < championship_id (Pilot)
Deck_prototype (1) ── < id_prototype (Deck)
Deck (1) ── < deck ("Championship ")
```

Nessuna relazione diretta verificata tra `Pilot`/`Team` e `Deck`.

## 5. Controllo di `Deck.cards`

Formato atteso (da istruzioni permanenti del progetto, non dal DB): array JSON di oggetti `{"path": "/images/cards/N_nome.ext", "value": N}`.

**Nessun dato è verificabile**, perché il file `HeatDB.sql` non contiene alcuna istruzione `INSERT`. Di conseguenza non è possibile fornire conteggi di record:

- validi: non verificabile (0 righe di dati presenti nel file)
- nulli: non verificabile
- vuoti: non verificabile
- JSON non validi: non verificabile
- validi ma con struttura errata: non verificabile

Qualsiasi cifra su questi conteggi sarebbe inventata: non viene riportata.

## 6. Anomalie riscontrate (non corrette)

1. **Nome tabella con spazio finale**: `"Championship "` è definita così sia nel `CREATE TABLE` sia nella `FOREIGN KEY` di `Pilot` e nella `FOREIGN KEY` di `Deck`... verificato: solo `Pilot.championship_id` e la relazione inversa `"Championship ".deck → Deck.id` referenziano questa tabella; lo spazio è presente in modo consistente ovunque compaia nel file.
2. **`Deck.cards` e `Deck_prototype.base_cards` senza vincolo `CHECK`**: nessuna garanzia a livello database che il contenuto sia JSON valido nella struttura richiesta.
3. **`Championship.pilots` come colonna testuale** invece di una tabella di relazione N:N con vincoli referenziali.
4. **Assenza di FK diretta tra `Deck` e `Pilot`/`Team`**: il mazzo risulta collegato solo al campionato nello schema attuale.
5. **Assenza di qualunque tabella relativa a un "negozio"** (nessuna tabella `Shop`, `Item`, `Purchase` o simile presente nel file).
6. **Nessun campo di ruolo/permesso in `User`** e nessuna indicazione sul formato di `password`.
7. **Nessun vincolo `UNIQUE` su `Pilot.user_id`**: cardinalità Utente↔Pilota non definita a livello database.

## 7. Cosa non è stato verificato

- Contenuto dati reale (perché assente nel file fornito)
- Indici oltre a quelli impliciti da `UNIQUE`
- Eventuali vincoli `CHECK` (nessuno presente nel testo letto)
- Comportamento di `ON DELETE`/`ON UPDATE` diverso da `NO ACTION` (tutte le FK usano `NO ACTION`, verificato)
</content>
