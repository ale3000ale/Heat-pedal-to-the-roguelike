# Avvio, configurazione e strumenti locali

Mappa delle fonti, non requisito approvato: le regole del gioco e le procedure autorevoli restano nei
documenti canonici; qui si indicano i punti di ingresso e il comportamento osservato nel codice.

## Documenti canonici

- [Indice della KB](../INDICE.md)
- [Installazione e avvio](../../SETUP.md) — prerequisiti e passi del setup.
- [Comandi](../../SCRIPTS.md) — elenco dei comandi `heat.py` e note sul codice di uscita.
- [Guida LAN di produzione](../../PRODUCTION_LAN.md) — indirizzi, QR e avvio operativo.
- [Specifiche di gioco](../../PROJECT_SPEC.md) — avvio e manutenzione.
- [Note del progetto](../../PROJECT_NOTES.md) — mappe dei file, QR e strumento immagini.
- [Stato del progetto](../../PROJECT_STATUS.md) — avanzamento delle funzioni 0.9.
- [Database, migrazioni e concorrenza](database-migrazioni-e-concorrenza.md) — regole delle migrazioni.
- [Interfaccia, navigazione e QR](interfaccia-navigazione-e-qr.md) — popup QR e origine dell'indirizzo.
- [Pool, caricamento carte e amministrazione](pool-e-amministrazione-carte.md) — script di
  ridimensionamento delle immagini delle carte.

Allineamento controllato: `heat.py` espone menu e CLI, il setup crea l'ambiente e installa le
dipendenze, `start` avvia sviluppo su `127.0.0.1:8000` e `:5173`, `production` fa build e avvio LAN
senza migrazioni, `images` apre lo strumento locale per mappe ed eventi. Corrisponde a
`docs/PROJECT_SPEC.md:52`, `docs/SETUP.md:40-60` e `docs/PROJECT_NOTES.md:518-520`.

**Discrepanze segnalate senza modifica:**

1. `docs/SCRIPTS.md:44` descrive un menu di sei voci e `docs/SCRIPTS.md:47-49` elenca solo `migrate`,
   `start`, `test` e `check`; in `heat.py:195-204` le voci sono otto e includono produzione LAN e
   strumento immagini, assenti anche dalla tabella. `docs/SCRIPTS.md:60` dichiara inoltre di non aver
   letto `tools/`, e `docs/SETUP.md:36-38` reca l'ultimo aggiornamento al 2026-10-13. Le note di
   `docs/PROJECT_STATUS.md:48-52` e `docs/PROJECT_NOTES.md:518-520` descrivono invece gli strumenti
   presenti: la documentazione di comandi e setup è superata.
2. `docs/PROJECT_NOTES.md:510` afferma che `HEAT_PUBLIC_URL` è impostata anche da
   `start --public-url`; in `heat.py:120-141` la variabile entra nell'ambiente passato al solo
   processo Vite, mentre il processo uvicorn viene avviato senza `env=env`. Il backend di sviluppo
   quindi non la riceve e il QR dell'endpoint può ricadere sull'host della richiesta o sul loopback.
   In produzione invece `tools/production.py:82-93` passa lo stesso ambiente a backend e gateway.

Nessun documento o codice è stato modificato per risolvere queste discrepanze.

## Perimetro ed esclusioni

**Incluso:** launcher `heat.py` (menu, CLI, setup, avvio sviluppo, arresto dei processi, test e
controlli), variabili d'ambiente lette da configurazione e launcher, proxy di sviluppo, avvio di
produzione e gateway Node, selezione dell'IPv4 LAN, script invocati dal setup, strumento web locale
per immagini di mappe ed eventi, test individuati.

**Escluso:** regole e migrazioni del database (scheda
[Database, migrazioni e concorrenza](database-migrazioni-e-concorrenza.md)); endpoint, popup e
precedenza dell'origine del QR (scheda [Interfaccia, navigazione e QR](interfaccia-navigazione-e-qr.md));
ritaglio e caricamento delle immagini delle carte (scheda
[Pool, caricamento carte e amministrazione](pool-e-amministrazione-carte.md)); logiche di gioco e API
di dominio; workflow CI, dati reali, esecuzione di setup, migrazioni, test o browser.

Questa scheda è proprietaria di `heat.py`, `backend/app/config.py`, `tools/check-frontend.mjs`,
`tools/production.py`, `tools/lan.py`, `tools/test_*.py`, `frontend/vite.config.ts`,
`frontend/production-server.mjs`, `tools/image_tool/` e degli script `create_admin`/`seed_prototype`
come passi del setup.

## Revisione e stato del worktree esaminati

- Revisione: `21e17e637b43528d7320e88f0af5623db7158ee9`; branch
  `feat/0.9-mappe-eventi` in tracking con `origin/feat/0.9-mappe-eventi`.
- Worktree invariato rispetto alle fasi documentali precedenti: tre file tracciati modificati e due
  directory non tracciate. Qui si aggiungono solo scheda e link all'indice.
- Non sono stati eseguiti setup, migrazioni, test, build, avvio di server o ispezione del database;
  lo schema SQLite reale non è stato verificato e non è oggetto di questa scheda.

## Punti d'ingresso e flusso

### Launcher e configurazione

- Percorsi e impostazioni fisse: radice del repository, `backend/`, `frontend/`, `tools/`,
  `backend/.venv`, interprete `Scripts/python.exe` su Windows e `bin/python` altrove, host
  `127.0.0.1`, porte 8000 e 5173, Python minimo 3.11: `heat.py:14-25`.
- `info`, `fail`, `run`, `find_npm`: `run` lancia i comandi con `check=True`, quindi un ritorno
  diverso da zero solleva `SystemExit` con prefisso "ERRORE":
  `heat.py:28-51`.
- `migrate` richiama `alembic upgrade head` con cwd `backend/`; `setup` verifica la versione di
  Python, crea il venv, aggiorna pip, installa i requirements, migra, esegue il seed e la creazione
  dell'admin, poi `npm ci` o `npm install`: `heat.py:54-82`.
- Seed e admin sono idempotenti: il primo crea le due pool di base vuote se mancano, il secondo
  legge credenziali da ambiente o da input, non crea un secondo admin e non sovrascrive uno username
  esistente: `backend/app/scripts/seed_prototype.py:8-17`,
  `backend/app/scripts/create_admin.py:11-27`.
- `spawn` crea un nuovo gruppo di processi; `stop` segnala il gruppo e attende otto secondi prima
  del fallback forzato (`taskkill` su Windows, `SIGKILL` altrove):
  `heat.py:85-118`.
- `start` copia l'ambiente, applica le migrazioni, avvia uvicorn con `--reload` e Vite con
  `--strictPort`, controlla che i processi restino vivi e li arresta in ordine inverso:
  `heat.py:120-150`.
- `production`, `production_menu` e `image_tool` delegano rispettivamente a `start_production` e al
  modulo `tools.image_tool`; `run_tests` lancia pytest in `backend/`, `run_checks` richiede `node` e
  `tools/check-frontend.mjs`: `heat.py:153-192`.
- Menu con otto voci e gestione degli errori che rientrano nel ciclo; CLI con sottocomandi `setup`,
  `start`, `production`, `migrate`, `test`, `check`, `images` e opzioni `--skip-admin`,
  `--skip-seed`, `--backend-only`, `--public-url`, `--port`, `--no-browser`:
  `heat.py:195-223`, `heat.py:226-269`.
- Configurazione backend: database SQLite locale, nome del cookie `heat_session`,
  `HEAT_SESSION_COOKIE_SECURE` ammesso solo `0` o `1`, cartella `media` e limiti delle immagini:
  `backend/app/config.py:1-13`.

### Sviluppo e controlli

- Vite: plugin Tailwind e SvelteKit con adapter Node e runes forzati, host e porta fissi,
  `allowedHosts` derivato da `HEAT_PUBLIC_URL`, proxy di `/api` e `/media` verso
  `127.0.0.1:8000` senza `changeOrigin`, progetto Vitest unico in ambiente node:
  `frontend/vite.config.ts:6-30`, `frontend/vite.config.ts:31-44`.
- `tools/check-frontend.mjs` esegue in sequenza `npm run format`, `check`, `lint` e `test` dentro
  `frontend/`, con `CI=true`, stdin chiuso e arresto al primo errore salvo `--keep-going`; il passo
  `format` riscrive i file: `tools/check-frontend.mjs:1-15`,
  `tools/check-frontend.mjs:17-48`.

### Produzione LAN

- `normalize_origin` accetta solo origini HTTP su loopback o IPv4 privato alla porta 5173, oppure
  HTTPS, senza percorso, credenziali, query o frammenti; `production_origin` sceglie automaticamente
  la LAN solo senza argomento: `tools/production.py:18-63`.
- `print_qr` salva il QR del terminale in una cartella temporanea e lo apre, senza richiedere
  `qrcode` per avviare: `tools/production.py:66-79`.
- `runtime_environment` rimuove gli header inoltrati forniti dall'ambiente, imposta `NODE_ENV`,
  `ORIGIN`, `HEAT_PUBLIC_URL`, `HEAT_SESSION_COOKIE_SECURE` in base all'HTTPS e un token casuale di
  readiness: `tools/production.py:82-93`.
- `require_free_ports` verifica le porte senza terminare altri processi; `wait_ready` interroga il
  figlio senza proxy e fallisce su uscita o scadenza; `DB_CHECK` verifica in sola lettura che il
  database sia `sqlite:///./heat.db` e che la revisione Alembic coincida con gli head:
  `tools/production.py:96-123`.
- `start_production` richiede venv, Node, npm, dipendenze Node e `backend/heat.db`, non installa e
  non migra, costruisce il frontend, avvia uvicorn su loopback con un worker e `--no-proxy-headers`,
  poi il gateway Node; stampa il QR solo per origini non locali e arresta i figli su errore, uscita
  inattesa o Ctrl+C: `tools/production.py:126-177`.
- `lan.py` accetta solo IPv4 RFC1918, verifica con bind che l'indirizzo appartenga al PC e, senza
  override, chiede all'utente quando il rilevamento non è univoco; non apre server e non tocca il
  firewall: `tools/lan.py:5-22`, `tools/lan.py:25-43`, `tools/lan.py:46-58`,
  `tools/lan.py:61-83`.
- Il gateway Node valida l'origine, sceglie come indirizzo di ascolto la LAN per HTTP o il loopback
  per HTTPS, controlla Host esatto e Origine sulle scritture, limita la readiness al loopback o
  all'IP scelto, rimuove gli header inoltrati dal client, manda `/api` e `/media` a `127.0.0.1:8000`
  con header inoltrati generati dal gateway e lascia lo streaming SSE senza timeout:
  `frontend/production-server.mjs:6-23`, `frontend/production-server.mjs:25-55`,
  `frontend/production-server.mjs:57-61`, `frontend/production-server.mjs:63-143`,
  `frontend/production-server.mjs:145-164`.

### Strumento di sviluppo per media e JSON di mappe ed eventi

- Avvio: `python heat.py images` passa da `heat.py:167-178`; il modulo accetta `--port` predefinita
  8765 e `--no-browser`, verifica che la porta sia libera e apre uvicorn solo su loopback:
  `tools/image_tool/__main__.py:1-53`.
- App locale: radice predefinita `backend/media`, JSON in `backend/json`, area di staging temporanea
  con ID esadecimali e lock, pagina statica, mount `/media` e API `/api/destinations`,
  `/api/media/browse`, `/api/media/last-folder` (GET e POST), `/api/data/{kind}` (GET e POST),
  `/api/data/{kind}/{index}` (PUT), `/api/upload`, `/api/staged/{id}` (GET e DELETE) e `/api/save`;
  se il JSON manca, la GET lo crea vuoto e restituisce `created: true`; se serve una riparazione la
  GET restituisce anche `repaired: true`; la pulizia dello staging avviene a lifespan terminato:
  `tools/image_tool/app.py:44-51`, `tools/image_tool/app.py:178-216`,
  `tools/image_tool/app.py:221-292`, `tools/image_tool/app.py:384-426`.
- Media: `/api/media/browse` restituisce solo le sottocartelle e le immagini della cartella richiesta,
  con `path`, `parent` nullo alla radice e URL codificati; path assoluti, `..`, parti nascoste e file
  vengono rifiutati e il resolved path deve restare dentro `backend/media`; le destinazioni di
  salvataggio restano relative e confinate: `tools/image_tool/app.py:178-216`,
  `tools/image_tool/conversion.py:72-110`.
- Stato della cartella: `GET /api/media/last-folder?kind=...` restituisce l'ultima cartella del tipo,
  `POST` la salva con scrittura atomica UTF-8 in `tools/image_tool/state.json` senza toccare gli altri
  tipi; valori non validi o cartelle sparite ricadono sulla radice:
  `tools/image_tool/app.py:58-101`, `tools/image_tool/app.py:273-292`.
- JSON: `events.json` e `maps.json` usano modelli Pydantic con `id` intero nascosto, autogenerato
  incrementale e conservato in modifica; campi obbligatori, `StrictInt >= 0`, path immagine esistente
  dentro `backend/media`, unicità case-insensitive di nome e path con errore
  `errore elemento già esistente`, e scrittura atomica UTF-8. `repair_items` all'apertura elimina le
  chiavi sconosciute e imposta a `null` i campi mancanti o non validi, riscrivendo il file; l'ID resta
  un intero positivo univoco e i duplicati vengono solo segnalati. `maps.json` include `sezioni`, lista
  di interi non negativi (anche vuota): `tools/image_tool/json_store.py:17-56`,
  `tools/image_tool/json_store.py:59-101`, `tools/image_tool/json_store.py:117-224`,
  `tools/image_tool/json_store.py:227-290`.
- Convertitore: file fino a 25 MB, scatola massima 560x870 senza ingrandire, orientamento EXIF e
  WebP qualità 90 scritto su temporaneo e sostituito solo dopo verifica:
  `tools/image_tool/conversion.py:9-69`.
- UI: barra `Media` / `JSON` con sottomenù `Mappe` ed `Eventi`, schede con immagine e valori, modale
  di modifica con anteprima dell'immagine in cima, path prima del nome, autofill del nome dal file,
  conferma, aggiunta vuota, esploratore a cartelle con breadcrumb e pulsante `Su`, ricerca limitata
  alla cartella aperta, cartella iniziale ripristinata per tipo di JSON, campo `Numero sezioni` che
  genera N input numerici senza stepper (rimossi anche da tutti gli altri campi), schede con errori in
  cima con triangolo rosso semi-trasparente sull'immagine che evidenzia i campi problematici, e avviso
  `File JSON creato` con solo `OK`:
  `tools/image_tool/static/index.html`, `tools/image_tool/static/app.js`,
  `tools/image_tool/static/style.css`.
- Salvataggio immagini: sposta i WebP dallo staging alla destinazione scelta, usa il nome suggerito
  se il campo è vuoto e restituisce esiti ed errori per singola immagine:
  `tools/image_tool/app.py:384-426`.

## Test individuati

- `tools/test_lan.py`, `tools/test_production.py`, `tools/test_production_lan.py` — validazione IP e
  origini, ambiente di produzione, gateway, proxy, readiness e intestazioni.
- `frontend/production-server.test.mjs`, `frontend/production-lan.test.mjs` — gateway Node, scelta
  del bind,Host, Origine, cookie, media, SSE e inoltro:
  `frontend/production-lan.test.mjs:31-51`,
  `frontend/production-lan.test.mjs:53-55`.
- `tools/image_tool/tests/test_conversion.py` — ridimensionamento, nomi e destinazioni:
  `tools/image_tool/tests/test_conversion.py:24-72`.
- `tools/image_tool/tests/test_app.py` — pagina, destinazioni, mount `/media`, navigazione a cartelle
  con rifiuto dei path esterni e voci nascoste, ultima cartella per JSON con persistenza al riavvio,
  upload, anteprima, salvataggio, API JSON, creazione del file mancante, riparazione all'apertura,
  duplicati preservati, ID incrementali, percorsi non validi, JSON corrotto e marker UI (triangolo,
  sezioni, assenza di stepper).
- `tools/image_tool/tests/test_json_store.py` — modelli, validazione, ID generati e normalizzati,
  riparazione dei campi e delle sezioni, duplicati preservati, path dentro `backend/media`, scrittura
  atomica e JSON corrotto.
- `tools/test_startup.py` — test di avvio reali di `setup`, `migrate`, `test`, `check`, sviluppo e
  produzione, disabilitati salvo `HEAT_STARTUP_TESTS=1` e con server non accesi:
  `tools/test_startup.py:1-7`, `tools/test_startup.py:95-120`.

Nella sessione corrente sono stati eseguiti solo i tre test dello strumento: 60 test passati con
`backend/.venv/Scripts/python.exe -m unittest tools.image_tool.tests.test_app
tools.image_tool.tests.test_conversion tools.image_tool.tests.test_json_store -v`. Test di startup,
suite applicativa, CI, avvio reale e browser non sono stati ri-eseguiti; gli altri conteggi in
`docs/PROJECT_STATUS.md` restano riferiti ad altre sessioni.

## Osservato, dedotto e non verificato

- **Osservato:** launcher, configurazione, proxy, gateway, strumento di sviluppo, script richiamati
  dal setup, test elencati, documenti di avvio e 60 test dello strumento passati nella sessione
  corrente.
- **Dedotto dal codice:** produzione non crea il database e non applica migrazioni; il gateway non
  accetta header inoltrati dal client e costruisce quelli verso il backend; lo strumento non
  sovrascrive i file esistenti, valida i JSON e confina i path immagine dentro `backend/media`;
  `start` passa `--public-url` solo al processo frontend.
- **Non verificato:** esecuzione della suite applicativa e degli script di startup, porte, build, CI,
  database reale, browser, interazioni click/tastiera della nuova UI, codice di uscita dei comandi
  `test` e `check`, scattering degli header in una rete LAN effettiva.

## Fonti da ricontrollare quando cambiano le fonti pertinenti

- `heat.py`, `backend/app/config.py`, `backend/app/scripts/{create_admin,seed_prototype}.py`,
  `frontend/vite.config.ts`, `tools/check-frontend.mjs`, `tools/{production,lan}.py`,
  `frontend/production-server.mjs` e i test elencati sopra.
- `tools/image_tool/` (app, archivio JSON, conversione, pagina statica e test), `backend/media` come
  radice predefinita e `backend/json` per `events.json` e `maps.json`.
- I documenti canonici linkati all'inizio. Se cambiano i comandi del launcher, le variabili
  d'ambiente, le porte, la selezione dell'IP o la procedura di avvio, aggiornare qui i rimandi a
  `SETUP.md`, `SCRIPTS.md` e `PRODUCTION_LAN.md`.
