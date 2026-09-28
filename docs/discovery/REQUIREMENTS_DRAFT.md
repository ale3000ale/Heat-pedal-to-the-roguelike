> **STATO: BOZZA NON APPROVATA — AGGIORNATA CON ARCHITETTURA SCRIPT RUN-ONCE.**
>
> Questo documento riepiloga i requisiti già stabiliti nelle istruzioni permanenti del progetto e nelle richieste dell'utente. Non è definitivo finché non approvato esplicitamente.

# Requisiti noti — Heat

## Stack

- Frontend: SvelteKit + TypeScript, responsive e mobile-first.
- Backend: Python + FastAPI + SQLAlchemy + Pydantic.
- Database: SQLite; schema iniziale autorevole in `HeatDB.sql`.
- Dipendenze: npm con `package-lock.json` per frontend; `uv` con `pyproject.toml` e `uv.lock` per backend.
- Usare solo versioni stabili, recenti e compatibili; mai beta o RC.

## Struttura e bootstrap

- Radice unica del progetto, senza `frontend/frontend` o secondo frontend.
- Struttura finale separata in frontend, backend, database, resources, scripts, test e documenti.
- `frontend/` è intenzionalmente vuota e va creata in fase successiva solo tramite `npx sv create frontend` con template minimal, TypeScript, npm, ESLint, Prettier e Vitest.
- Prima di qualsiasi codice applicativo: installazione dipendenze, type-check e build della base autentica SvelteKit.

## Architettura script di automazione

### Entrypoint principale raccomandato

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

### Script secondari (mantenuti)

- `setup.py` — logica applicativa principale (può essere richiamato da `run-once.py`).
- `setup.bat` — wrapper Windows per `setup.py`.
- `setup.sh` — wrapper Unix per `setup.py`.

Questi restano nel progetto ma **non sono l'entrypoint raccomandato per l'utente finale**.

### Script interni organizzati per piattaforma

Gli script reali sono organizzati in:

- `scripts/windows/` — file `.bat` o `.cmd` (solo CMD, no PowerShell).
- `scripts/unix/` — file `.sh`.

`run-once.py` funge da controller unico e semplice per l'utente, mostrando un menu interattivo persistente e richiamando gli script giusti in base al sistema operativo.

### Comportamento di `run-once.py`

`run-once.py` deve:

1. Rilevare il sistema operativo (Windows, macOS, Linux, altro Unix).
2. Verificare la disponibilità di Python.
3. Verificare di essere eseguito dalla radice del progetto.
4. Mostrare un menu interattivo persistente.
5. Offrire le operazioni principali (vedi sotto).
6. Richiamare gli script giusti per Windows o Unix.
7. Mostrare chiaramente ogni comando eseguito (echo dei comandi).
8. Fermarsi in caso di errore con messaggio leggibile.
9. Restituire codice 0 in caso di successo e diverso da 0 in caso di errore.

### Operazioni del menu principale

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

### Requisiti di robustezza

- Script idempotenti.
- Validazione dei percorsi.
- Funzionamento garantito solo se eseguiti dalla radice del progetto.
- Devono mostrare errori reali (nessun errore mascherato o finto successo).
- Non devono mai eliminare database, immagini, `.env` o backup.
- Ogni operazione distruttiva richiede backup preventivo e conferma esplicita dell'utente.

## Modello dati

### Relazioni principali

- User 1:N Team.
- User 1:N Pilot.
- Team 1:N Pilot.
- Pilot 1:1 Deck.

Un utente può possedere più team e più piloti. Un pilota deve appartenere a un team dello stesso proprietario, salvo future operazioni amministrative.

### User, Team e Pilot

- `Team` deve contenere `user_id` come proprietario.
- `Pilot` deve contenere `user_id` e `team_id`.
- A `User` vanno aggiunti `is_admin BOOLEAN NOT NULL DEFAULT 0`, `created_at` e `updated_at`.
- `Pilot.point` e `Pilot.sponsor` vanno rimossi nella migrazione iniziale: non sono fonti autorevoli. `Pilot.sponsor` rappresentava punti sponsor, non denaro né una entità Sponsor.

### Deck e DeckPrototype

- `Deck` appartiene esclusivamente a `Pilot`, non a Team o Championship.
- Aggiungere `Deck.pilot_id UNIQUE NOT NULL` per la relazione 1:1.
- Rimuovere `Deck.id_prototype` e il relativo legame persistente con `DeckPrototype`.
- `DeckPrototype` è indipendente e serve solo a creare o resettare un Deck.
- Durante il reset, il backend valida `DeckPrototype.base_cards` e copia il JSON in `Deck.cards`; non conserva il prototipo scelto e modifiche future al prototipo non modificano il mazzo già creato.
- `Deck.cards` e `DeckPrototype.base_cards` restano `TEXT` con JSON validato dal backend, avente formato:

```json
[
  {
    "path": "/images/cards/1_nome.webp",
    "value": 1
  }
]
```

- `path` deve essere relativo; `value` deve essere un intero.

### Championship e iscrizioni

- Rinominare tramite migrazione `"Championship "` in `Championship`, eliminando lo spazio finale.
- Rimuovere `Championship.pilots` testuale e sostituirlo con `ChampionshipPilot`.
- `Championship.date` è la data prevista di inizio.
- Aggiungere a Championship: `status`, `created_at`, `updated_at`, `closed_at` opzionale.
- Stati ammessi: `draft`, `open`, `in_progress`, `closed`.
- Possono esistere più campionati `open` o `in_progress` contemporaneamente.
- Un Pilot può appartenere a un solo campionato attivo alla volta, ma può essere nello storico di più campionati chiusi.

`ChampionshipPilot` deve contenere almeno `id`, `championship_id`, `pilot_id`, `team_id` come fotografia del team, `status`, `joined_at`, `left_at` opzionale e UNIQUE su `(championship_id, pilot_id)`.

Il backend deve verificare nella stessa transazione di iscrizione/riattivazione che il pilota non abbia già una iscrizione a un altro Championship `open` o `in_progress`; in conflitto deve rifiutare l'operazione con errore chiaro. Lo storico non va eliminato.

### Gare, risultati e classifica

Aggiungere:

- `Race`: `id`, `championship_id`, `name`, `sequence_number`, `date`, `status`, `created_at`, `updated_at`.
- `RaceResult`: `id`, `race_id`, `pilot_id`, `position` opzionale, `points`, `sponsor_points`, `notes` opzionale, `created_at`, `updated_at`.

Relazioni:

- Championship 1:N Race.
- Race 1:N RaceResult.
- Pilot 1:N RaceResult.
- UNIQUE su `(race_id, pilot_id)`.

Un RaceResult è ammesso solo per un pilota iscritto al Championship cui appartiene la Race. L'amministratore inserisce manualmente `points` e `sponsor_points` per gara e pilota.

La classifica è indipendente per Championship:

- punti = somma di `RaceResult.points` delle Race del Championship selezionato;
- punti sponsor = somma di `RaceResult.sponsor_points` delle Race del Championship selezionato.

I risultati di campionati diversi non devono mescolarsi. Fino a futura decisione, i pari punti sono visualizzati a pari merito; l'ordine alfabetico serve solo a stabilizzare la visualizzazione e non è uno spareggio sportivo.

## Migrazioni

- Usare Alembic per ogni evoluzione dello schema.
- La migrazione iniziale deve allineare `HeatDB.sql` alla nuova specifica: rinomina Championship, ownership di Team/Pilot, Pilot 1:1 Deck, rimozione `Deck.id_prototype`, rimozione campi testuali/aggregati sostituiti, `ChampionshipPilot`, `Race`, `RaceResult`, dati User per ruoli e audit.
- Prima di ogni migrazione creare un backup.
- Abilitare `PRAGMA foreign_keys = ON` su ogni connessione SQLite ed eseguire controlli di integrità dopo le migrazioni.
- Il DB iniziale non contiene dati; l'importazione futura di dati reali richiederà una procedura esplicita e non blocca la prima versione.

## Risorse carte

- Le carte sorgente sono in `resources/images/cards/`.
- Vanno sincronizzate in `frontend/static/images/cards/`.
- Nomi: `N_nome.ext`, con N da 1 a 10.
- Nel database sono ammessi esclusivamente path relativi come `/images/cards/1_nome.webp`.

## Autenticazione

- Applicazione inizialmente locale; HTTP è ammesso su localhost.
- Il frontend invia la password al backend senza hashing lato client.
- Non salvare password o token in localStorage, sessionStorage, cookie, log o file.
- Il backend genera e verifica solo hash Argon2id; il DB conserva solo l'hash.
- Password e hash non compaiono in risposte API o log.
- Usare sessioni server-side, non JWT.
- Il cookie contiene solo un identificatore di sessione casuale e opaco; i dati sessione vivono lato server/database.
- Cookie: HttpOnly, SameSite=Lax, Secure con HTTPS, scadenza configurabile e revocabile al logout.
- Nessuna cifratura reversibile e nessuna chiave segreta nel frontend.
- Configurazione e documentazione devono consentire il passaggio futuro a HTTPS senza cambiare l'architettura di autenticazione.

## Ruoli

- Ruoli della prima versione: `user` e `admin`.
- Il primo utente registrato diventa admin in modo atomico e testato.
- Gli admin successivi sono abilitati manualmente intervenendo su `User.is_admin` nel database; non è previsto pannello di promozione.
- Utenti normali: gestione dei soli team, piloti e mazzi posseduti.
- Admin: gestione di tutti i dati e parametri globali.

## Pagine

### Team

- Elenco pubblico di tutti i team e relativi piloti.
- Utente autenticato: creazione e gestione di propri team e piloti.
- Vietata modifica di dati altrui; admin può gestire ogni team e pilota.
- Cancellazioni con conferma e rispetto relazioni; non cancellare automaticamente RaceResult o storico dei campionati.

### Campionati

- Elenco completo, filtro per stato, dettaglio, iscritti, gare, risultati, classifica e storico campionati chiusi.
- Solo admin: crea/modifica/apre/avvia/chiude Championship, iscrive/rimuove piloti, crea gare, inserisce/corregge RaceResult.
- Utenti normali: sola visualizzazione di campionati, gare, risultati e classifiche.

### Home

Senza autenticazione:
- riepilogo campionati attivi;
- classifica dell'ultimo campionato chiuso;
- stato vuoto chiaro se non esistono dati.

Con autenticazione:
- team e piloti dell'utente;
- campionati attivi;
- eventuale campionato attivo di ogni pilota;
- punti e punti sponsor del pilota nel relativo campionato;
- mazzo del pilota selezionato;
- collegamenti rapidi alle pagine principali.

### Mazzo

- Utente: selezione di uno dei propri piloti, visualizzazione mazzo e immagini carte, reset da DeckPrototype con conferma, sole operazioni autorizzate.
- Admin: gestione di tutti i mazzi e DeckPrototype.
- Aggiunta di nuove carte da parte dell'amministratore rinviata a decisione futura.

### Negozio

- Rinviato.
- Prima versione: solo pagina/modulo separato "Funzionalità in definizione".
- Non creare `ShopItem`, `Purchase`, prodotti, prezzi o regole.
- Le relazioni future Pilot-Purchase e ShopItem-Purchase non appartengono allo schema corrente.

### Login

- Usa sessioni server-side come definito nella sezione Autenticazione.

## Automazione

- Includere `run-once.py`, `run-once.bat`, `run-once.sh` come entrypoint raccomandati.
- Mantenere anche `setup.py`, `setup.bat`, `setup.sh` come logica applicativa secondaria.
- Organizzare script interni in `scripts/windows/` (.bat/.cmd) e `scripts/unix/` (.sh).
- Il menu principale deve gestire tutte le operazioni elencate nella sezione "Operazioni del menu principale".
- Script idempotenti, validazione percorsi, esecuzione dalla radice, errori reali visibili.
- Nessuna eliminazione automatica di DB, immagini, `.env` o backup; ogni azione distruttiva richiede backup e conferma.

## Sicurezza repository

- Non includere node_modules, `.svelte-kit`, build, `.venv`, cache, `.env` reali, password o token.
- Fornire `.gitignore` e `.env.example`.

## Metodo

Fasi obbligatorie con approvazione prima del passaggio successivo:

1. Analisi e requisiti.
2. Approvazione `PROJECT_SPEC.md`.
3. Bootstrap frontend.
4. Backend e migrazioni.
5. Funzionalità una alla volta.
6. Test, documentazione e ZIP finale.