# Heat — Web App locale per il gioco da tavolo

Applicazione full-stack (FastAPI + SQLite + SQLAlchemy lato backend, SvelteKit + TypeScript + Tailwind lato frontend) pensata per girare sul server locale, senza Docker.

## Struttura del progetto

```
heat/
├── backend/
│   ├── requirements.txt
│   ├── HeatDB_extended.sql        # schema DB esteso (base: HeatDB.sql fornito)
│   ├── init_db.py                 # script per creare heat.db dallo schema SQL
│   └── app/
│       ├── main.py                # entrypoint FastAPI
│       ├── db.py                  # engine + sessione SQLAlchemy
│       ├── core/
│       │   ├── config.py          # settings (JWT, CORS, ecc.)
│       │   ├── security.py        # hashing password + JWT
│       │   └── deps.py            # dependency injection (utente corrente, admin)
│       ├── models/                # user.py, pilot.py, team.py, championship.py, deck.py, shop.py
│       ├── schemas/                # auth.py, pilot.py, team.py, championship.py, deck.py, shop.py
│       ├── routers/                # auth.py, pilots.py, teams.py, championships.py, decks.py, shop.py
│       └── services/               # auth_service.py, pilot_service.py, team_service.py,
│                                    # championship_service.py, deck_service.py, deck_utils.py, shop_service.py
│
├── frontend/
│   ├── package.json, svelte.config.js, vite.config.ts, tailwind.config.cjs, postcss.config.cjs, tsconfig.json
│   └── src/
│       ├── app.html
│       ├── styles/app.css
│       ├── routes/
│       │   ├── +layout.svelte
│       │   ├── +page.svelte              # Home
│       │   ├── login/+page.svelte
│       │   ├── team/+page.svelte
│       │   ├── piloti/+page.svelte
│       │   ├── piloti/[id]/+page.svelte
│       │   ├── mazzo/+page.svelte
│       │   ├── mazzo/[id]/+page.svelte
│       │   ├── campionati/+page.svelte
│       │   ├── negozio/+page.svelte
│       │   └── negozio/[id]/+page.svelte
│       └── lib/
│           ├── api.ts
│           ├── store/ (auth.ts, theme.ts)
│           └── components/ (Navbar, ThemeToggle, PilotCard, PilotList, TeamList, DeckGrid,
│                             SearchBar, LoginForm, RegisterForm, NewTeamModal, NewPilotModal, ShopItemCard)
│
└── src/                            # risorse statiche condivise
    ├── images/cards/                # N_nome.ext (es. 3_SpeedBoost.png)
    ├── images/texture/
    └── images/icons/
```

> Nota: `backend/app/` e ogni sua sottocartella (`models`, `schemas`, `routers`, `services`, `core`) devono contenere un file vuoto `__init__.py` per essere riconosciute come package Python. Aggiungili se il tuo editor non li crea automaticamente.

## 1. Inizializzazione del database

Dalla cartella `backend/`:

```bash
python -m venv venv
source venv/bin/activate        # su Windows: venv\Scripts\activate
pip install -r requirements.txt

python init_db.py               # crea backend/heat.db eseguendo HeatDB_extended.sql
```

Lo script legge `HeatDB_extended.sql` (schema esteso a partire dal tuo `HeatDB.sql`) e crea tutte le tabelle in `heat.db`. Se preferisci gestire le migrazioni con Alembic in futuro, puoi inizializzare Alembic con `alembic init migrations` e generare la prima revisione da questo schema come baseline.

## 2. Avvio backend (FastAPI)

Sempre dalla cartella `backend/`, con il virtualenv attivo:

```bash
uvicorn app.main:app --reload --port 8000
```

- API disponibili su `http://127.0.0.1:8000`
- Documentazione automatica Swagger su `http://127.0.0.1:8000/docs`

## 3. Avvio frontend (SvelteKit)

Dalla cartella `frontend/`:

```bash
npm install        # oppure: pnpm install
npm run dev         # oppure: pnpm dev
```

- App disponibile su `http://localhost:5173`
- Le chiamate a `/api/*` vengono automaticamente proxate verso il backend su `127.0.0.1:8000` (vedi `vite.config.ts`)

## 4. Convenzioni per le risorse carte

I file immagine delle carte vanno inseriti in `src/images/cards/` con il formato `N_nome.ext`, dove `N` è un intero da 1 a 10 (es. `3_SpeedBoost.png`). Il backend valida questo formato sia in `schemas/deck.py` (CardItem) sia in `services/deck_utils.py` (validate_card_list) prima di salvare un mazzo.

Il campo `Deck.cards` nel DB contiene un JSON testuale di questo tipo:

```json
[
  { "path": "src/images/cards/3_SpeedBoost.png", "value": 5 },
  { "path": "src/images/cards/7_Overtake.png", "value": 3 }
]
```

## 5. Ruoli utente

- **user**: ruolo di default alla registrazione; gestisce i propri piloti, team, mazzi e acquisti.
- **admin**: da impostare manualmente aggiornando il campo `role` di un utente in `heat.db` (es. con un client SQLite), oppure estendendo un endpoint dedicato in `routers/auth.py` protetto da `require_admin`. Gli admin possono essere abilitati a operazioni di gestione avanzata (es. creazione campionati/oggetti negozio) aggiungendo `Depends(require_admin)` ai relativi endpoint.

## 6. Dati di esempio (opzionale)

Lo schema esteso non popola automaticamente Team, Championship, Pilot, ShopItem. Per testare l'app end-to-end, inserisci manualmente qualche riga tramite un client SQLite (es. DB Browser for SQLite) oppure tramite gli endpoint Swagger su `/docs` dopo aver registrato un utente admin.

## 7. Estensioni future consigliate

- Alembic per migrazioni versionate dello schema
- Endpoint admin dedicati per gestione campionati/negozio (`routers/admin.py`)
- Upload immagini carte via API invece che manuale in `src/images/cards/`
- Test automatici (pytest per backend, vitest per frontend)
