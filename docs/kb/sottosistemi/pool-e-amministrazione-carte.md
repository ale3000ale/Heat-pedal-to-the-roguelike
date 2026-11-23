# Pool, caricamento carte e amministrazione delle carte dei piloti

Mappa delle fonti, non requisito approvato: le regole autorevoli sono nelle sezioni 5 e 7 di
`PROJECT_SPEC.md`, con le decisioni della fase 13 in `PHASE_13_SPEC.md`.

## Documenti canonici

- [Indice della KB](../INDICE.md)
- [Specifiche di gioco, sezione 5](../../PROJECT_SPEC.md) — formato delle carte, cartelle e
  ricarica delle pool di base.
- [Specifiche fase 13, parte B](../../PHASE_13_SPEC.md) — caricamento, eliminazione e pool
  personalizzate.
- [Schema del database](../../DATABASE.md) — formato descritto di `cards` e `base_cards`.
- [Note del progetto](../../PROJECT_NOTES.md) — mappa del codice e convenzioni.
- [Stato del progetto](../../PROJECT_STATUS.md) — avanzamento e scelte riferite dall'autore.
- [Database, migrazioni e concorrenza](database-migrazioni-e-concorrenza.md) — lock di scrittura e
  versioni dei mazzi.
- [Team, piloti e mazzi](team-piloti-e-mazzi.md) — inventari e mazzo da gioco lato giocatore.
- [Preparazione della prossima gara](setup-prossima-gara.md) — blocco della preparazione.
- [Gare, risultati e classifica](gare-risultati-e-classifica.md) — registri di giocate e regali.
- [Interfaccia, navigazione e QR](interfaccia-navigazione-e-qr.md) — guscio comune.

Allineamento controllato: poiché i file immagine delle base stanno in
`backend/media/cards/base/{modifiche,sponsor}` e quelli caricati in
`backend/media/cards/uploads/`, la ricarica aggiunge le carte nuove in fondo, lascia intatte quelle
già presenti per nome o percorso e toglie solo quelle il cui file è sparito; l'anteprima non scrive;
le pool derivate e le copie dei campionati restano invariate; solo le carte caricate si eliminano e
il file viene cancellato quando nessun uso rimane; il ritaglio produce un WebP 560x870. Queste
regole corrispondono a `docs/PROJECT_SPEC.md:149-160`, `docs/PHASE_13_SPEC.md:99-109` e al codice
citato sotto.

**Discrepanze segnalate senza modifica:**

1. `docs/PHASE_13_SPEC.md:103` dice che il file resta finché un campionato usa la carta, mentre
   `backend/app/services/cards/card_delete.py:25-41` considera usato un percorso presente in
   qualunque pool o mazzo (compresi inventari e mazzi da gioco) o nei registri `card_play` e
   `card_gift`, e non cancella nulla se un mazzo ha un JSON illeggibile. L'implementazione è più
   prudente della specifica, non la contraddice apertamente.
2. `docs/PROJECT_STATUS.md:183` e `docs/PROJECT_STATUS.md:275` affermano che l'immagine si sposta
   solo con il puntatore e che non esiste un comando da tastiera; in
   `frontend/src/lib/components/cards/card-crop-editor.svelte:111-126` la funzione `keyPan` sposta
   il ritaglio con le frecce (Maiusc per il passo fine). La nota di stato è superata per questa
   istantanea.
3. `docs/PROJECT_SPEC.md:159` prevede che all'avvio non cambi nessun dato e compaia solo un avviso
   per le cartelle non ancora caricate; `backend/app/main.py:37-58` esegue invece
   `purge_expired`, `purge_old_deleted` e avvia il timer di revisione, senza scansione delle
   cartelle immagini. La specifica descrive un comportamento non presente nel codice osservato.
4. `docs/PROJECT_SPEC.md:186` mostra come esempio il percorso
   `images/cards/ruota da bagnato_3.webp`, mentre `docs/DATABASE.md:78` riporta
   `cards/starter/velocita-1.webp` e il codice usa i prefissi `cards/base/`, `cards/uploads/` e
   `cards/starter/` (si veda `frontend/src/lib/cards/card-origin.ts:3-30`). L'esempio nella
   specifica non corrisponde ai percorsi correnti.

Nessun documento o codice è stato modificato per risolvere queste discrepanze.

## Perimetro ed esclusioni

**Incluso:** creazione, eliminazione, elenco e dettaglio delle pool; ricarica delle pool di base con
anteprima; ridenominazione delle carte in pool; caricamento, ritaglio e cancellazione delle carte
caricate a mano; ridimensionamento delle immagini; lettura e salvataggio admin dei cinque
contenitori di carte del pilota (Mazzo da gioco, due inventari e due pool del campionato); API,
servizi, modelli concettuali, schema descritto, frontend admin, test.

**Escluso:** composizione del mazzo da gioco da parte del giocatore e interfacce degli inventari
(scheda [Team, piloti e mazzi](team-piloti-e-mazzi.md)); estrazione e acquisti dei pacchetti
(scheda [Negozio, pacchetti e acquisti](negozio-e-pacchetti.md)); giocate, regali, revisione e
conteggi (scheda [Carte sponsor in gara e revisione](carte-sponsor-e-revisione.md)); regole della
preparazione gara e dei mazzi pronti (scheda [Preparazione della prossima gara](setup-prossima-gara.md));
database SQLite reale, esecuzione dei test, CI e browser.

Questa scheda è proprietaria dei router `pools`, `card_admin` e `admin_pilot_cards`, dei servizi
`pools`, `pool_cards`, `card_upload`, `card_delete`, `images`, `admin_pilot_*` e
`admin_card_transfers`, delle pagine `routes/admin/pools/` e dei componenti di ritaglio e
caricamento. I mazzi del pilota sono citati solo come contenitori toccati dall'amministrazione.

## Revisione e stato del worktree esaminati

- Revisione: `21e17e637b43528d7320e88f0af5623db7158ee9`; branch
  `feat/0.9-mappe-eventi` in tracking con `origin/feat/0.9-mappe-eventi`.
- Worktree invariato rispetto alle fasi documentali precedenti: tre file tracciati modificati e due
  directory non tracciate. Qui si aggiungono solo scheda e link all'indice.
- Non sono stati eseguiti test, né ispezionato il database reale o usato il browser.

## Punti d'ingresso e flusso

### API e contratto

- Router registrati: `pools` sotto `/api/pools`, `card_admin` sotto `/api/admin/cards`,
  `admin_pilot_cards` sotto `/api/admin/championships`; `/media` serve le immagini:
  `backend/app/main.py:65-87`.
- Pool: elenco con conteggi, anteprima e ricarica delle base, dettaglio, ridenominazione di una
  carta, creazione ed eliminazione. 401/403 per non admin, 404 per pool o carta assente, 409 per
  nome in uso, pool protetta o carta con nome duplicato, 422 per scelte non valide:
  `backend/app/api/championship/pools.py:25-45`,
  `backend/app/api/championship/pools.py:48-70`,
  `backend/app/api/championship/pools.py:72-106`,
  `backend/app/api/championship/pools.py:109-153`.
- Caricamento ed eliminazione di carte: il corpo è l'immagine già ritagliata, tipo/nome/copie
  viaggiano nella query; 413 sopra 2 MB, 409 nome già usato o carta non caricata, 404 carta
  assente, 422 file non valido: `backend/app/api/admin/card_admin.py:15-63`.
- Carte dei piloti: elenco iscritti, lettura e un'unica `PUT` di salvataggio; traduzione degli
  errori di dominio in 403/404/409/422 senza assorbire errori SQL:
  `backend/app/api/admin/admin_pilot_cards.py:17-53`.
- DTO: tipi di pool e scelte con limiti, esiti di ricarica e anteprima; risposta di
  caricamento/cancellazione; cinque contenitori con id, versione e disponibilità esplicita, bozza
  con versioni attese e trasferimenti ordinati:
  `backend/app/schemas/championship/pool.py:8-51`,
  `backend/app/schemas/cards/card_admin.py:6-16`,
  `backend/app/schemas/cards/admin_pilot_cards.py:7-61`.

### Servizi e persistenza descritta

- Pool: tipi `modifiche` e `sponsor`, nomi delle due base, errori di dominio e strutture di esito;
  creazione con copie non superiori alla base e nomi/percorsi copiati; eliminazione protetta per le
  base: `backend/app/services/championship/pools.py:21-71`,
  `backend/app/services/championship/pools.py:73-143`,
  `backend/app/services/championship/pools.py:146-152`.
- Ricarica: legge la cartella `cards/base/<tipo>`, aggiunge solo WebP con nome `nome_N`, scarta i
  file non validi con avviso, rimuove le carte con file sparito, conserva nome e copie già presenti;
  con `apply=False` non scrive: `backend/app/services/championship/pools.py:155-234`.
- Anteprima: segna le carte da togliere presenti nella copia di pool di un campionato attivo:
  `backend/app/services/championship/pools.py:237-262`.
- Ridenominazione: la carta si identifica dal percorso, che non cambia; nome non vuoto e univoco
  nella sola pool: `backend/app/services/championship/pool_cards.py:9-38`.
- Caricamento: formati JPEG/PNG/WebP, nome pulito e privo di caratteri pericolosi, al massimo 64
  caratteri e 999 copie, file fino a 2 MB, salvataggio WebP con nome univoco; il percorso risultante
  è sotto `cards/uploads/<tipo>/`: `backend/app/config.py:11-13`,
  `backend/app/services/cards/card_upload.py:10-100`,
  `backend/app/services/cards/images.py:8-60`.
- Eliminazione: solo le carte con percorso sotto `cards/uploads/`; la rimozione dei file orfani
  controlla pool, mazzi, giocate e regali e lascia i file non cancellabili; anche la cancellazione
  di un campionato chiuso richiama la pulizia a transazione confermata:
  `backend/app/services/cards/card_delete.py:12-85`,
  `backend/app/services/championship/championships.py:205-247`.
- Script di ridimensionamento: cartelle predefinite `media/cards` e `media/pack`, `--dry-run`,
  conversione in WebP dentro la scatola 560x870 senza tagliare e senza toccare gli originali:
  `backend/app/scripts/resize_cards.py:8-86`.
- Lettura admin: ruolo ricontrollato sul database, iscritti non eliminati, cinque Deck letti in una
  query con versioni, pool assenti rese esplicite e blocco se campionato chiuso, preparazione attiva
  o gara/revisione non confermata: `backend/app/services/cards/admin_pilot_cards.py:18-120`.
- Trasferimenti: cinque contenitori con destinazioni fisse; una copia per clic su liste clonate,
  rifiuto di percorsi ambigui o nomi associati a immagini diverse, senza ruoli o scritture:
  `backend/app/services/cards/admin_card_transfers.py:10-94`,
  `frontend/src/lib/admin/pilot-cards/admin-pilot-cards-draft.ts:11-110`.
- Salvataggio: lock SQLite condiviso, rilettura dello snapshot, confronto di tutte le versioni,
  piano senza mutare lo snapshot, un solo commit con due eventi `cards.changed` senza carte,
  rollback su `StaleDataError`, database occupato o errore inatteso, nessun retry:
  `backend/app/services/cards/admin_pilot_card_save.py:18-107`.
- **Schema SQLite effettivo non verificato**: i contenitori sono `Deck`/`DeckPrototype` con
  `cards` e `base_cards` JSON; tabelle, colonne, indici e vincoli non sono stati ispezionati nel
  database reale.

### Frontend

- Pagina delle pool: elenco e distinzione tra base e derivate, moduli di ricarica con anteprima e
  conferma, creazione con copie limitate alla base, due tasti di esclusione di gruppo, caricamento
  ed eliminazione delle carte; la conferma di ricarica usa il componente condiviso:
  `frontend/src/routes/admin/pools/+page.svelte:22-95`,
  `frontend/src/routes/admin/pools/+page.svelte:107-168`,
  `frontend/src/routes/admin/pools/+page.svelte:170-230`.
- Dettaglio pool: griglia di carte con copie e ridenominazione salvata su `blur` o Invio, con
  `path` come chiave stabile: `frontend/src/routes/admin/pools/[id]/+page.svelte:13-74`.
- Selettore: carte caricate evidenziate e con tasto "Elimina", copie tra 0 e il massimo della base:
  `frontend/src/lib/components/championship/pool-card-picker.svelte:6-51`.
- Ritaglio: area 560x870, trascinamento con puntatore, zoom, spostamento con frecce e passo fine,
  anteprima su canvas ed esportazione WebP a qualità 0,9 a ogni modifica:
  `frontend/src/lib/cards/card-crop.ts:1-97`,
  `frontend/src/lib/components/cards/card-crop-editor.svelte:14-132`,
  `frontend/src/lib/components/cards/card-crop-editor.svelte:134-189`.
- Modulo di caricamento e client: nome, copie, file, anteprima e invio del blob senza JSON, con
  messaggi leggibili per 409/413/422:
  `frontend/src/lib/components/cards/card-upload-form.svelte:7-103`,
  `frontend/src/lib/admin/card-admin-api.ts:17-70`.
- Riconoscimento dell'origine delle carte e esclusione di gruppo nella sola bozza del modulo:
  `frontend/src/lib/cards/card-origin.ts:3-30`,
  `frontend/src/lib/championship/pool-exclusion.ts:4-25`.
- Pannello carte admin: bozza locale, spostamenti, blocchi di conflitto, conferma di uscita con
  modifiche in sospeso e aggiornamenti live; la `PUT` valida il contesto della risposta senza
  ritentare: `frontend/src/lib/components/admin/admin-pilot-cards-panel.svelte:44-170`,
  `frontend/src/lib/admin/pilot-cards/admin-pilot-cards-save-api.ts:5-50`.

## Test individuati (non eseguiti in questa fase)

- `backend/tests/test_pool_kinds_api.py`, `backend/tests/test_pool_counts_api.py`,
  `backend/tests/test_championships_api.py` — tipi di pool, ricarica, conteggi e creazione.
- `backend/tests/test_card_admin_services.py`, `backend/tests/test_images.py`,
  `backend/tests/test_championship_delete_cards.py` — caricamento, eliminazione, immagini e
  pulizia dopo cancellazione del campionato.
- `backend/tests/test_admin_pilot_cards_api.py`, `backend/tests/test_admin_pilot_card_save.py` —
  letture e salvataggio admin, inclusa la concorrenza su due salvataggi.
- `frontend/src/lib/cards/card-crop.spec.ts`, `frontend/src/lib/cards/card-origin.spec.ts`,
  `frontend/src/lib/championship/pool-exclusion.spec.ts`,
  `frontend/src/lib/admin/card-admin-api.spec.ts` — logica pura e client.
- `frontend/src/lib/admin/pilot-cards/` — test colocated per bozza, piano, sessione, eventi live,
  salvataggio e vista.

Nessun test è stato eseguito durante la generazione della scheda. I risultati riportati nei
documenti di fase e in `docs/PROJECT_STATUS.md` sono riferiti ad altre sessioni e non qui
ri-osservati.

## Osservato, dedotto e non verificato

- **Osservato:** router, DTO, servizi, script, client, pagine, componenti e test citati; documenti
  canonici e note di fase, incluse le affermazioni disallineate elencate sopra.
- **Dedotto dal codice:** la ricarica distingue le carte di base dalle caricate e non sovrascrive
  nomi corretti a mano; l'anteprima non scrive; l'eliminazione di un file dipende da tutti i mazzi e
  dai registri, non solo dalle pool dei campionati; il salvataggio admin usa lo stesso lock e le
  stesse versioni degli altri mazzi, con evento senza carte e rollback completo; il frontend non
  autorizza il salvataggio, che resta validato dal backend.
- **Non verificato:** database SQLite reale, file presenti in `backend/media`, esecuzione test,
  browser, CI e concorrenza effettiva con più worker.

## Fonti da ricontrollare quando cambiano le fonti pertinenti

- `backend/app/main.py`, `backend/app/api/championship/pools.py`,
  `backend/app/api/admin/card_admin.py`, `backend/app/api/admin/admin_pilot_cards.py`,
  `backend/app/schemas/championship/pool.py`, `backend/app/schemas/cards/`.
- `backend/app/services/championship/{pools,pool_cards,championships}.py`,
  `backend/app/services/cards/{card_upload,card_delete,images,admin_pilot_cards,admin_pilot_card_save,admin_card_transfers}.py`,
  `backend/app/scripts/resize_cards.py` e `backend/app/config.py`.
- `frontend/src/routes/admin/pools/`, `frontend/src/lib/components/{admin,cards,championship}/`,
  `frontend/src/lib/cards/`, `frontend/src/lib/admin/pilot-cards/` e i test elencati sopra.
- I documenti canonici linkati all'inizio. Se cambiano i prefissi delle immagini, i limiti di
  caricamento, le regole di ricarica/esclusione o i contenitori toccati dall'amministrazione,
  aggiornare qui i rimandi a `PROJECT_SPEC.md`, `PHASE_13_SPEC.md` e `DATABASE.md`.
