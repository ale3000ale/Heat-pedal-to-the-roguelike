# Interfaccia, navigazione e QR di accesso

Mappa delle fonti, non requisito approvato: il comportamento osservato è nei file citati; i documenti
di fase e di stato sono indizi da riconfrontare, non specifiche da modificare qui.

## Documenti canonici

- [Indice della KB](../INDICE.md)
- [Specifiche di gioco](../../PROJECT_SPEC.md) — menu "Admin" e barra di navigazione.
- [Note del progetto](../../PROJECT_NOTES.md) — mappa dei router e sezione «QR di accesso dal menu».
- [Stato del progetto](../../PROJECT_STATUS.md) — avanzamento fasi 14 e 0.9, note sul menu a 375 px.
- [Note fase 14](../../PHASE_14.md) — limiti noti del layout dopo il riallineamento.
- [Impostazioni account](../../ACCOUNT_SETTINGS.md) — comportamento del popup raggiunto dalla barra.
- [Guida LAN di produzione](../../PRODUCTION_LAN.md) — QR dal menu e QR del terminale.
- [Changelog](../../CHANGELOG.md) — navigazione con `resolve()`, drawer sotto gli 768 px.
- [Autenticazione, sessioni e ruoli](autenticazione-e-sessioni.md) — sessione, ruoli e popup account.
- [Eventi live e SSE](eventi-live-e-sse.md) — client condiviso usato dal guscio.
- [Preparazione della prossima gara](setup-prossima-gara.md) — host del dialogo di draft.
- [Pool, caricamento carte e amministrazione](pool-e-amministrazione-carte.md) — pagine raggiungibili
  dal menu Admin.
- [Avvio, configurazione e strumenti](avvio-configurazione-e-strumenti.md) — origine pubblica impostata
  dal launcher.

Allineamento controllato: le voci principali e admin hanno un'unica fonte in `nav-menu.svelte`, usata
sia nella barra sia nel drawer; il tasto "QR di accesso" è visibile a tutti gli utenti collegati; il
popup mostra QR e indirizzo e avvisa se l'indirizzo è locale; l'endpoint è autenticato e restituisce
solo l'origine del sito, senza credenziali. Corrisponde a `docs/PROJECT_NOTES.md:506-514`,
`docs/PROJECT_STATUS.md:42-46` e `docs/PRODUCTION_LAN.md:19-21`.

**Discrepanze segnalate senza modifica:**

1. `docs/PROJECT_STATUS.md:206` e `docs/PROJECT_NOTES.md:195` indicano ancora come da fare in fase 14
   lo sforamento del menu dell'intestazione a 375 px, mentre `docs/PROJECT_STATUS.md:123` e
   `docs/PROJECT_STATUS.md:299` danno la fase 14 come unita e la voce come residue del vecchio elenco.
   Non è stato verificato nel browser se lo sforamento sia effettivamente risolto: le note di stato
   risultano superate come pianificazione, non come constatazione di fixing.
2. `docs/PHASE_14.md:139` afferma che il menu in alto resta largo `max-w-5xl`; in
   `frontend/src/routes/+layout.svelte:127` la barra usa `max-w-6xl` e il solo footer resta
   `max-w-5xl` (`frontend/src/routes/+layout.svelte:265`). La nota di fase non descrive più il codice
   osservato.
3. `docs/PROJECT_NOTES.md:514` e `docs/PROJECT_STATUS.md:44` descrivono il QR come lavoro del ramo
   `feat/0.9-qr-accesso`; la revisione esaminata è su `feat/0.9-mappe-eventi` e contiene già il codice.
   È una datazione storica delle note, non un contrasto sulle regole.

Nessun documento o codice è stato modificato per risolvere queste discrepanze.

## Perimetro ed esclusioni

**Incluso:** guscio dell'applicazione (stato di autenticazione, redirect, loading, banner di errore,
contenuto e footer), stili globali del tema, barra di navigazione orizzontale, drawer sotto gli
768 px, regole condivise di chiusura dei modal, popup "Impostazioni account" come ospite del guscio,
tasto e popup del QR di accesso, endpoint e servizio dell'origine pubblica, test individuati.

**Escluso:** regole e API di sessione, ruoli, cambio password e revoca (scheda
[Autenticazione, sessioni e ruoli](autenticazione-e-sessioni.md)); trasporto SSE e logica del client
eventi (scheda [Eventi live e SSE](eventi-live-e-sse.md)); host e chiusura del dialogo di draft
(scheda [Preparazione della prossima gara](setup-prossima-gara.md)); pagine funzionali raggiungibili
dalle voci di menu; launcher e QR stampato nel terminale (scheda
[Avvio, configurazione e strumenti](avvio-configurazione-e-strumenti.md)); browser, CI, database
reale ed esecuzione dei test.

Questa scheda è proprietaria di `routes/+layout.svelte`, `routes/+layout.ts`, `routes/layout.css`,
`components/shared/{nav-menu,nav-drawer,modal-close,site-qr-dialog}.svelte`, `lib/site/site-qr.ts`,
`api/site.py`, `schemas/site.py` e `services/core/site_qr.py`. `account-settings.svelte` è citato
solo come ospite del guscio: il suo comportamento appartiene alla scheda sull'autenticazione.

## Revisione e stato del worktree esaminati

- Revisione: `21e17e637b43528d7320e88f0af5623db7158ee9`; branch
  `feat/0.9-mappe-eventi` in tracking con `origin/feat/0.9-mappe-eventi`.
- Worktree invariato rispetto alle fasi documentali precedenti: tre file tracciati modificati e due
  directory non tracciate. Qui si aggiungono solo scheda e link all'indice.
- Nessuna tabella, migrazione o scrittura SQLite è coinvolta: non c'è uno schema SQLite reale da
  verificare per questo sottosistema. Non sono stati eseguiti test né usato il browser.

## Punti d'ingresso e flusso

### Guscio lato frontend

- `ssr = false`: l'app gira solo nel browser perché la sessione è un cookie; il layout importa il CSS
  globale, il favicon e i componenti condivisi: `frontend/src/routes/+layout.ts:1-3`,
  `frontend/src/routes/+layout.svelte:1-19`.
- Stato locale: flag dei dialoghi impostazioni e QR, host del draft legato a sessione/utente/ruolo,
  elenco dei percorsi pubblici (`/login`, `/register`) e flag del drawer:
  `frontend/src/routes/+layout.svelte:20-38`.
- All'apertura `auth.init()` verifica la sessione; un effetto collega il client eventi con
  disconnessione dell'utente su `auth.expired`; altro effetto manda al login chi non è autenticato su
  pagina protetta; cambio di pagina o di utente chiude drawer e impostazioni; `logout` disconnette gli
  eventi e lascia all'effetto il redirect: `frontend/src/routes/+layout.svelte:40-79`.
- Render: host del draft, schermata di caricamento "Riscaldamento Motori…", banner rosso con
  `role="alert"` se `auth.error`, header solo per utenti autenticati, contenuto per autenticati o
  pagine pubbliche, footer solo per autenticati: `frontend/src/routes/+layout.svelte:82-120`,
  `frontend/src/routes/+layout.svelte:253-282`.
- Header: `nav` con `max-w-6xl`, pulsante hamburger `md:hidden` con `aria-expanded`/`aria-controls`,
  logo con link alla home, `NavMenu` orizzontale, badge utente con etichetta Admin o Giudice e tasto
  "Esci", riga decorativa `curb-bar`: `frontend/src/routes/+layout.svelte:122-229`.
- Ospiti dei dialoghi: `NavDrawer` con `NavMenu` verticale, `AccountSettings` con chiave sull'id
  utente e `SiteQrDialog`, tutti montati solo quando aperti:
  `frontend/src/routes/+layout.svelte:231-250`.
- Tema e utility: import Tailwind e shadcn-svelte, variabili chiare e scure, `@theme inline`,
  regole base per body e titoli, strisce `curb-bar` e relative varianti:
  `frontend/src/routes/layout.css:1-7`, `frontend/src/routes/layout.css:9-51`,
  `frontend/src/routes/layout.css:53-79`, `frontend/src/routes/layout.css:81-129`.

### Navigazione

- Voci principali e admin definite una sola volta; il tasto QR è una voce tra le principali e non
  richiede permessi: `frontend/src/lib/components/shared/nav-menu.svelte:1-23`,
  `frontend/src/lib/components/shared/nav-menu.svelte:94-127`.
- Props: percorso corrente, flag admin, orientamento, callback di navigazione e callback per il QR;
  il menu admin a tendina si chiude al cambio pagina o al clic fuori, ignorando i clic dentro il
  dialogo del draft: `frontend/src/lib/components/shared/nav-menu.svelte:25-57`,
  `frontend/src/lib/components/shared/nav-menu.svelte:129-177`.
- Stile attivo con `aria-current="page"` e classi diverse tra barra e drawer; le icone sono quelle
  condivise `helmet`, `trophy`, `tires`, `spark_plug`, `wrenches` e `qr`:
  `frontend/src/lib/components/shared/nav-menu.svelte:59-91`,
  `frontend/src/lib/components/shared/racing-icon.svelte:8-22`,
  `frontend/src/lib/components/shared/racing-icon.svelte:316-316`,
  `frontend/src/lib/components/shared/racing-icon.svelte:757-757`.
- Drawer: `open` bindable, chiusura con X, Escape e sfondo, overlay `md:hidden`, pannello
  `role="dialog"` con `aria-modal="true"` e larghezza `w-72 max-w-[85vw]`:
  `frontend/src/lib/components/shared/nav-drawer.svelte:1-24`,
  `frontend/src/lib/components/shared/nav-drawer.svelte:28-58`.
- Regola condivisa: X chiude sempre salvo intercettore, Escape e sfondo solo se abilitati, errori
  dell'intercettore propagati senza autorizzare la chiusura:
  `frontend/src/lib/components/shared/modal-close.ts:1-22`.

### QR di accesso

- Il client chiama `GET /api/site/qr` con le credenziali della sessione e riconosce gli indirizzi
  raggiungibili solo dal PC (`localhost`, `127.0.0.1`, `[::1]`):
  `frontend/src/lib/site/site-qr.ts:1-22`.
- Il popup gestisce caricamento, errore con "Riprova", immagine PNG in data URL, indirizzo in chiaro,
  istruzione di stare nella stessa rete e avviso locale con il suggerimento di avviare
  `python heat.py production`; ignora risposte tardive dopo lo smontaggio:
  `frontend/src/lib/components/shared/site-qr-dialog.svelte:1-37`,
  `frontend/src/lib/components/shared/site-qr-dialog.svelte:39-74`.
- Il router è registrato sotto `/api/site`; `GET /qr` richiede un utente corrente, legge
  `HEAT_PUBLIC_URL`, `X-Forwarded-Host`/`Host` e `X-Forwarded-Proto`, e restituisce `{ url, image }`
  senza token o credenziali: `backend/app/main.py:27-27`,
  `backend/app/main.py:83-83`, `backend/app/api/site.py:1-27`,
  `backend/app/schemas/site.py:1-8`.
- Origine: `normalize_origin` accetta solo http/https con host valido e senza percorso, query,
  frammento, credenziali o porta non numerica; `site_origin` privilegia `HEAT_PUBLIC_URL`, poi
  l'host inoltrato, poi `http://127.0.0.1:5173`; `qr_png_data_url` codifica il PNG in base64 senza
  file temporanei: `backend/app/services/core/site_qr.py:8-37`,
  `backend/app/services/core/site_qr.py:40-60`,
  `backend/app/services/core/site_qr.py:63-69`.

## Test individuati (non eseguiti in questa fase)

- `backend/tests/test_site_qr.py` — 401 senza login, precedenza di `HEAT_PUBLIC_URL`, host e proto
  inoltrati, firma PNG, valori rifiutati e accettati da `normalize_origin`, precedenza e primo valore
  degli header, data URL: `backend/tests/test_site_qr.py:29-72`,
  `backend/tests/test_site_qr.py:75-120`.
- `frontend/src/lib/site/site-qr.spec.ts` — richiesta con cookie, messaggio di errore del backend e
  riconoscimento degli indirizzi locali: `frontend/src/lib/site/site-qr.spec.ts:11-44`.
- `frontend/src/lib/components/shared/nav-drawer.spec.ts` — render SSR delle voci principali e
  admin, orientamento verticale senza `<details>`; non verifica clic, Escape, focus o responsive:
  `frontend/src/lib/components/shared/nav-drawer.spec.ts:1-29`,
  `frontend/src/lib/components/shared/nav-drawer.spec.ts:31-63`.
- `frontend/src/lib/components/shared/modal-close.spec.ts` e
  `frontend/src/lib/draft/draft-close-policy.spec.ts` — regola condivisa di chiusura e sua
  interazione con il draft.
- `frontend/src/lib/auth/password-ui.spec.ts` — render SSR del popup account, la cui logica è
  descritta nella scheda sull'autenticazione.

Nessun test è stato eseguito durante la generazione della scheda. I risultati riportati in
`docs/PROJECT_STATUS.md:46` e `docs/PROJECT_NOTES.md:516` sono riferiti ad altre sessioni e non qui
ri-osservati.

## Osservato, dedotto e non verificato

- **Osservato:** layout, stili, componenti di navigazione, dialoghi, client, router, schema e servizio
  citati; documenti di stato, note di fase e test elencati.
- **Dedotto dal codice:** menu e drawer condividono le stesse voci; il QR non contiene segreti e la
  scelta dell'origine è deterministica; il popup non aggiorna uno stato smontato; il guscio non
  renderizza il contenuto finché la sessione non è pronta, salvo le pagine pubbliche.
- **Non verificato:** comportamento reale a 375 px e sotto gli 768 px, clic e tasti nei dialoghi,
  esecuzione dei test, browser, CI e risoluzione effettiva del TODO sulla navigazione admin.

## Fonti da ricontrollare quando cambiano le fonti pertinenti

- `frontend/src/routes/+layout.svelte`, `frontend/src/routes/+layout.ts`,
  `frontend/src/routes/layout.css`, `frontend/src/lib/components/shared/` e
  `frontend/src/lib/site/site-qr.ts` con i test colocated.
- `backend/app/main.py`, `backend/app/api/site.py`, `backend/app/schemas/site.py`,
  `backend/app/services/core/site_qr.py`, `backend/tests/test_site_qr.py` e le variabili
  `HEAT_PUBLIC_URL` del launcher e del gateway.
- I documenti canonici linkati all'inizio. Se cambiano le voci di menu, la soglia responsive, le
  regole di chiusura o la precedenza dell'origine del QR, aggiornare qui i rimandi a
  `PROJECT_NOTES.md`, `PROJECT_STATUS.md` e `PRODUCTION_LAN.md`.
