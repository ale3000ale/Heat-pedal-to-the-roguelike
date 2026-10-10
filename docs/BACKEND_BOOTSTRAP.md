# Fase 4: Bootstrap backend e migrazioni

> STATO: COMPLETATA. **DOCUMENTO STORICO**: descrive il backend alla fine della
> fase 4 (9 tabelle, ruoli `admin` e `player`). Lo stato attuale è in
> `PROJECT_STATUS.md`, `PROJECT_SPEC.md` e nelle migrazioni in
> `backend/alembic/versions/`; da allora sono stati aggiunti ruolo `judge`,
> pool, gare, impostazioni e altre tabelle.

## Stack

- Python 3.13.14
- FastAPI 0.142.2, Uvicorn 0.54.0
- SQLAlchemy 2.1.1 (stile 2.0: Mapped, mapped_column)
- Alembic 1.20.0, modalità batch per SQLite
- pwdlib con Argon2 0.3.1
- Database: SQLite, file `backend/heat.db` (ignorato da git)

## Struttura

```text
backend/
├── app/
│   ├── main.py            # app FastAPI, endpoint GET /health
│   ├── config.py          # DATABASE_URL
│   ├── security.py        # hash e verifica password (Argon2)
│   ├── db/
│   │   ├── base.py        # Base dichiarativa
│   │   ├── session.py     # engine, SessionLocal, get_db, PRAGMA foreign_keys=ON
│   │   └── models/        # user, team, deck, pilot, championship, race
│   └── scripts/
│       ├── create_admin.py
│       └── seed_prototype.py
├── alembic/               # env.py usa DATABASE_URL e render_as_batch=True
├── alembic.ini
└── requirements.txt
```

## Tabelle (9)

user, team, deck_prototype, deck, pilot, championship, championship_pilot,
race, race_result.

## Scelte di modellazione

- Nomi tabelle in minuscolo e singolari; `"Championship "` diventa `championship`.
- `pilot.championship_id` rimosso: l'iscrizione vive in `championship_pilot`.
- Il pilota ha due mazzi: `inventory_deck_id` e `game_deck_id` (unique, non nulli).
- `deck.id_prototype` è nullable: il mazzo base del pilota non dipende dal prototipo.
- `championship.is_closed` distingue campionati attivi e chiusi.
- `race_result.position` limitata a 1-12 (`ck_race_result_position`).
- `user.role` limitato a admin e player (`ck_user_role`).
- Nessuna `relationship()` nei modelli per ora.

## Comandi (dalla cartella backend/, con .venv attivo)

```bat
alembic upgrade head
python -m app.scripts.seed_prototype
python -m app.scripts.create_admin
uvicorn app.main:app --reload --port 8000
```

Da quando esiste `heat.py` (fase 6) avvio, setup, test e controlli passano
dal suo menu: `python heat.py`.

Variabili opzionali per `create_admin`: `HEAT_ADMIN_USERNAME`, `HEAT_ADMIN_PASSWORD`.

## Workaround applicati

- `base.py`: `Base` deve essere una classe (`class Base(DeclarativeBase): pass`),
  non un'istanza.
- Modelli scritti da Aider corretti a mano: `Base` importato da `app.db.base`,
  `CheckConstraint` con nome, `server_default` booleano.
- Migrazione iniziale rigenerata dopo la correzione dei modelli.

## Esiti

- `alembic upgrade head`, `downgrade base`, `upgrade head`: OK
- `GET /health`: OK, `/docs`: OK
- Seed prototipo e creazione admin: OK, password salvata con hash Argon2

## Limiti noti (alla fase 4)

- Pool del prototipo `default` vuota (`[]`): mancano i dati reali delle carte.
- Nessun login né endpoint applicativi: sono nella fase successiva.
- Vincoli UNIQUE senza nome: da nominare quando serviranno modifiche in batch.
