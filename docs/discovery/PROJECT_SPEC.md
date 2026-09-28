> **STATO: APPROVATO E BLOCCATO — SPECIFICA VERSIONE 1 (AGGIORNATA CON ARCHITETTURA SCRIPT RUN-ONCE).**
>
> Questo documento è la specifica tecnica ufficiale della versione 1 di Heat, aggiornato con la nuova architettura degli script di automazione. Non modificare i requisiti senza autorizzazione esplicita dell'utente.

# PROJECT_SPEC.md — Heat (v1.0)

## 1. Panoramica

Applicazione web locale per la gestione del gioco da tavolo **Heat**, con:

- autenticazione sicura con sessioni server-side e hash Argon2id;
- gestione di più campionati attivi contemporaneamente;
- vincolo "un pilota, un solo campionato attivo";
- classifiche indipendenti per campionato calcolate da `RaceResult`;
- gestione di team, piloti e mazzi con ownership per utente;
- ruoli `user` e `admin` (primo utente registrato = admin);
- pagine: Home, Login, Team, Campionati, Mazzo; Negozio rinviato (placeholder).

## 2. Stack tecnologico

| Livello | Tecnologia |
|---|---|
| Frontend | SvelteKit + TypeScript, npm, ESLint, Prettier, Vitest |
| Backend | Python + FastAPI + SQLAlchemy + Pydantic |
| Database | SQLite (schema iniziale da `HeatDB.sql`) |
| Migrazioni | Alembic |
| Dipendenze backend | `uv` con `pyproject.toml` e `uv.lock` |
| Autenticazione | sessioni server-side, cookie HttpOnly/SameSite/Lax, Secure su HTTPS, Argon2id |

## 3. Struttura del repository

Radice unica (nessun `frontend/frontend`):

```
Heat-pedal-to-the-roguelike/
  frontend/
  backend/
  database/
  resources/
  scripts/
    windows/
    unix/
  tests/
  docs/
  run-once.py
  run-once.bat
  run-once.sh
  setup.py
  setup.bat
  setup.sh
  .gitignore
  .env.example
  README.md
  SETUP.md
  DATABASE.md
  SCRIPTS.md
  PROJECT_SPEC.md
  PROJECT_STATUS.md
  REQUIREMENTS_DRAFT.md
  OPEN_QUESTIONS.md
  DATABASE_ANALYSIS.md
```

## 4. Bootstrap frontend

- Comando: `npx sv create frontend`
- Template: minimal
- TypeScript: sì
- Package manager: npm
- Add-on: ESLint, Prettier, Vitest
- Verifica obbligatoria prima di personalizzazioni: `npm install`, `npm run check`, `npm run build` senza errori.
- Conservare `package-lock.json` generato.

## 5. Modello dati

### 5.1 Entità e relazioni

- **User** 1:N **Team**
- **User** 1:N **Pilot**
- **Team** 1:N **Pilot**
- **Pilot** 1:1 **Deck**
- **Championship** 1:N **ChampionshipPilot**
- **ChampionshipPilot** N:1 **Pilot**
- **Championship** 1:N **Race**
- **Race** 1:N **RaceResult**
- **Pilot** 1:N **RaceResult**
- **DeckPrototype** (indipendente; usato solo come sorgente per reset/creazione mazzi)

Regola di integrità applicativa: un `Pilot` deve appartenere a un `Team` dello stesso `User` proprietario, salvo future operazioni amministrative.

### 5.2–5.12

*(Sezioni modello dati, migrazioni, autenticazione, ruoli, pagine, risorse, sicurezza — invariate rispetto alla versione precedente; vedi sotto per aggiornamenti solo su automazione.)*

## 6. Migrazioni

- Usare Alembic per tutte le evoluzioni dello schema.
- Migrazione iniziale: allineamento di `HeatDB.sql` alla specifica corrente (rinomina Championship, ownership, Pilot 1:1 Deck, rimozione `Deck.id_prototype`, `ChampionshipPilot`, `Race`, `RaceResult`, rimozione `Pilot.point`/`Pilot.sponsor`, campi audit e ruoli).
- Prima di ogni migrazione: backup del database.
- Abilitare `PRAGMA foreign_keys = ON` su ogni connessione SQLite.
- Eseguire controlli di integrità dopo ogni migrazione.
- Il DB iniziale non contiene dati; importazioni future richiederanno procedura esplicita.

## 7. Autenticazione

*(Invariata — vedi versione precedente.)*

## 8. Ruoli

*(Invariata — vedi versione precedente.)*

## 9. Pagine

*(Invariata — vedi versione precedente.)*

## 10. Risorse carte

*(Invariata — vedi versione precedente.)*

## 11. Automazione e script

### 11.1 Entrypoint principale raccomandato

Il progetto deve avere **un unico file principale "usa e getta"** nella radice:

- **`run-once.py`** — controller principale multipiattaforma.
- **`run-once.bat`** — launcher sottile per Windows CMD (non PowerShell).
- **`run-once.sh`** — launcher sottile per macOS/Linux Unix shell.

Scopo:
- Utente Windows: esegue `run-once.bat` dalla radice.
- Utente macOS/Linux: esegue `./run-once.sh` dalla radice.
- Alternativa: `python run-once.py` direttamente.
- Entrambi i launcher richiamano `run-once.py`.
- `run-once.py` rileva automaticamente il sistema operativo e usa gli script corretti nelle cartelle `scripts/windows/` e `scripts/unix/`.

### 11.2 Script secondari (mantenuti)

- `setup.py` — logica applicativa principale (può essere richiamato da `run-once.py`).
- `setup.bat` — wrapper Windows per `setup.py`.
- `setup.sh` — wrapper Unix per `setup.py`.

Questi restano nel progetto ma **non sono l'entrypoint raccomandato per l'utente finale**.

### 11.3 Script interni organizzati per piattaforma

Gli script reali sono organizzati in:

- `scripts/windows/` — file `.bat` o `.cmd` (solo CMD, no PowerShell).
- `scripts/unix/` — file `.sh`.

`run-once.py` funge da controller unico e semplice per l'utente, mostrando un menu interattivo persistente e richiamando gli script giusti in base al sistema operativo.

### 11.4 Comportamento di `run-once.py`

`run-once.py` deve:

1. Rilevare il sistema operativo (Windows, macOS, Linux, altro Unix).
2. Verificare la disponibilità di Python.
3. Verificare di essere eseguito dalla radice del progetto.
4. Mostrare un menu interattivo persistente.
5. Offrire le operazioni principali (vedi 11.5).
6. Richiamare gli script giusti per Windows o Unix.
7. Mostrare chiaramente ogni comando eseguito (echo dei comandi).
8. Fermarsi in caso di errore con messaggio leggibile.
9. Restituire codice 0 in caso di successo e diverso da 0 in caso di errore.

### 11.5 Operazioni del menu principale

Il menu di `run-once.py` deve includere almeno:

1. Setup completo
2. Verifica prerequisiti
3. Crea o verifica base SvelteKit
4. Installa frontend
5. Installa backend
6. Installa tutto
7. Aggiorna frontend
8. Aggiorna backend
9. Aggiorna tutto
10. Crea o ripara cartelle
11. Posiziona o sincronizza file
12. Inizializza o migra database
13. Backup database
14. Ripristino database
15. Reset frontend
16. Reset backend
17. Reset completo sicuro
18. Avvia frontend
19. Avvia backend
20. Avvia tutto
21. Test, lint e type-check
22. Build produzione frontend
23. Diagnostica completa
0. Esci

### 11.6 Requisiti di robustezza

- Script idempotenti.
- Validazione dei percorsi.
- Funzionamento garantito solo se eseguiti dalla radice del progetto.
- Devono mostrare errori reali (nessun errore mascherato o finto successo).
- Non devono mai eliminare database, immagini, `.env` o backup.
- Ogni operazione distruttiva richiede backup preventivo e conferma esplicita dell'utente.

## 12. Sicurezza repository

- `.gitignore` e `.env.example` obbligatori.
- Non includere: `node_modules`, `.svelte-kit`, `build`, `.venv`, `cache`, `.env` reali, password o token.

## 13. Metodo di lavoro

Fasi con approvazione esplicita prima di procedere:

1. Analisi e requisiti (completata).
2. Approvazione `PROJECT_SPEC.md` (completata, versione 1.0 bloccata).
3. Bootstrap frontend (in attesa di esecuzione locale da parte dell'utente).
4. Backend e migrazioni.
5. Funzionalità una alla volta.
6. Test, documentazione e ZIP finale.

## 14. Domande aperte residue

Vedi `OPEN_QUESTIONS.md`. Le uniche questioni non definite (Negozio, amministrazione carte, spareggio sportivo) sono esplicitamente rinviate e non bloccano la prima versione.

## 15. Criteri di approvazione

Questo documento è stato approvato esplicitamente dall'utente in data 2026-09-24 ed è ora bloccato come specifica di versione 1.0 (aggiornata con architettura script run-once). Qualsiasi modifica futura richiederà una nuova versione e una nuova approvazione.