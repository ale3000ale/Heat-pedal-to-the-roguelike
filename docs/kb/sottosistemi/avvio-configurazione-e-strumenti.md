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

### Strumento immagini di mappe ed eventi

- Avvio: `python heat.py images` passa da `heat.py:167-178`; il modulo accetta `--port` predefinita
  8765 e `--no-browser`, verifica che la porta sia libera e apre uvicorn solo su loopback:
  `tools/image_tool/__main__.py:12-50`.
- App locale: cartella predefinita `backend/media/board`, area di staging temporanea con ID
  esadecimali e lock, pagina statica e API `/api/destinations`, `/api/upload`,
  `/api/staged/{id}` (GET e DELETE) e `/api/save`; la pulizia dello staging avviene a lifespan
  terminato: `tools/image_tool/app.py:29-35`, `tools/image_tool/app.py:38-121`,
  `tools/image_tool/app.py:123-175`.
- Convertitore: file fino a 25 MB, scatola massima 560x870 senza ingrandire, orientamento EXIF,
  WebP qualità 90 scritto su temporaneo e sostituito solo dopo verifica, nomi minuscoli a trattini
  con suffisso `-2`, `-3` se esiste già un file, destinazioni relative e confinate a
  `backend/media/board`: `tools/image_tool/conversion.py:9-16`,
  `tools/image_tool/conversion.py:19-33`, `tools/image_tool/conversion.py:36-69`,
  `tools/image_tool/conversion.py:72-110`.
- Salvataggio: sposta i WebP dallo staging alla destinazione scelta, usa il nome suggerito se il
  campo è vuoto e restituisce esiti ed errori per singola immagine:
  `tools/image_tool/app.py:177-219`.

## Test individuati (non eseguiti in questa fase)

- `tools/test_lan.py`, `tools/test_production.py`, `tools/test_production_lan.py` — validazione IP e
  origini, ambiente di produzione, gateway, proxy, readiness e intestazioni.
- `frontend/production-server.test.mjs`, `frontend/production-lan.test.mjs` — gateway Node, scelta
  del bind,Host, Origine, cookie, media, SSE e inoltro:
  `frontend/production-lan.test.mjs:31-51`,
  `frontend/production-lan.test.mjs:53-55`.
- `tools/image_tool/tests/test_conversion.py` — ridimensionamento, nomi e destinazioni:
  `tools/image_tool/tests/test_conversion.py:24-72`.
- `tools/image_tool/tests/test_app.py` — pagina, elenco destinazioni, upload, anteprima, salvataggio,
  nomi e conflitti: `tools/image_tool/tests/test_app.py:18-100`.
- `tools/test_startup.py` — test di avvio reali di `setup`, `migrate`, `test`, `check`, sviluppo e
  produzione, disabilitati salvo `HEAT_STARTUP_TESTS=1` e con server non accesi:
  `tools/test_startup.py:1-7`, `tools/test_startup.py:95-120`.

Nessun test è stato eseguito durante la generazione della scheda. I conteggi e gli esiti riportati in
`docs/PROJECT_STATUS.md:52` sono riferiti ad altre sessioni e non qui ri-osservati.

## Osservato, dedotto e non verificato

- **Osservato:** launcher, configurazione, proxy, gateway, strumento immagini, script richiamati dal
  setup, test elencati e documenti di avvio.
- **Dedotto dal codice:** produzione non crea il database e non applica migrazioni; il gateway non
  accetta header inoltrati dal client e costruisce quelli verso il backend; lo strumento immagini non
  sovrascrive i file esistenti; `start` passa `--public-url` solo al processo frontend.
- **Non verificato:** esecuzione di comandi, porte, build, test, CI, database reale, browser,
  codice di uscita dei comandi `test` e `check`, scattering degli header in una rete LAN effettiva.

## Fonti da ricontrollare quando cambiano le fonti pertinenti

- `heat.py`, `backend/app/config.py`, `backend/app/scripts/{create_admin,seed_prototype}.py`,
  `frontend/vite.config.ts`, `tools/check-frontend.mjs`, `tools/{production,lan}.py`,
  `frontend/production-server.mjs` e i test elencati sopra.
- `tools/image_tool/` (app, conversione, pagina statica e test) e `backend/media/board` come
  destinazione predefinita.
- I documenti canonici linkati all'inizio. Se cambiano i comandi del launcher, le variabili
  d'ambiente, le porte, la selezione dell'IP o la procedura di avvio, aggiornare qui i rimandi a
  `SETUP.md`, `SCRIPTS.md` e `PRODUCTION_LAN.md`.
