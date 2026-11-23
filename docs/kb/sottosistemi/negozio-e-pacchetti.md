# Negozio, pacchetti e acquisti

Mappa delle fonti, non requisito approvato: le regole autorevoli sono nella sezione 13 di
`PROJECT_SPEC.md`, con il progetto approvato in `SHOP_DESIGN.md` e lo schema tecnico in
`SHOP_SCHEMA.md`.

## Documenti canonici

- [Indice della KB](../INDICE.md)
- [Specifiche di gioco, sezione 13](../../PROJECT_SPEC.md) — regole approvate di accesso, pagina,
  template, acquisto e storico.
- [Progetto del Negozio](../../SHOP_DESIGN.md) — decisioni dell'autore, interfaccia e sequenza di
  apertura dei pacchetti.
- [Schema tecnico del Negozio](../../SHOP_SCHEMA.md) — tabelle, servizi, rotte, componenti e
  sottofasi 12a-12f; da leggere con le discrepanze segnalate sotto.
- [Domande aperte](../../OPEN_QUESTIONS.md) — decisioni storiche su apertura e riepilogo.
- [Mappa del codice](../../PROJECT_NOTES.md) — struttura e convenzioni.
- [Stato del progetto](../../PROJECT_STATUS.md) — avanzamento e risultati riferiti.
- [Database](../../DATABASE.md) — schema descritto, non database reale.

Schede collegate esistenti: [Team, piloti e mazzi](team-piloti-e-mazzi.md),
[Campionati e iscrizioni](campionati-e-iscrizioni.md),
[Gare, risultati e classifica](gare-risultati-e-classifica.md),
[Carte sponsor in gara e revisione](carte-sponsor-e-revisione.md),
[Database, migrazioni e concorrenza](database-migrazioni-e-concorrenza.md),
[Autenticazione, sessioni e ruoli](autenticazione-e-sessioni.md).

Allineamento controllato: accesso con un proprio pilota iscritto, admin in sola lettura senza
pilota, blocco durante la gara, sezioni distinte solo per valuta, costi predefiniti 10 oro o 2
punti sponsor, almeno una carta per pacchetto, filtro comune senza distinzione di maiuscole,
estrazione proporzionale alle copie rimaste, tetto di 100 copie, "Terminato", storico con valori
copiati e apertura solo grafica — corrispondono a `docs/PROJECT_SPEC.md:313-364`,
`docs/SHOP_DESIGN.md:17-113`, `docs/SHOP_DESIGN.md:163-193` e al codice citato sotto.

**Discrepanze segnalate senza modifica:**

1. `docs/SHOP_SCHEMA.md:1-4` reca ancora lo stato «IN IMPLEMENTAZIONE» con la sola 12f da
   chiudere, mentre `docs/SHOP_DESIGN.md:1-6`, `docs/PROJECT_STATUS.md:106-112` e
   `docs/PROJECT_SPEC.md:364` descrivono la fase 12 approvata, unita e completata. Lo schema
   tecnico resta utile come mappa, non come fonte dello stato corrente.
2. `docs/PROJECT_SPEC.md:322` dice che il negozio si blocca «con una gara in corso», senza
   citare la revisione; `docs/SHOP_DESIGN.md:38-41` precisa che la revisione conta ancora come
   gara in corso e `backend/app/services/race/races.py:64-75` mantiene la gara non conclusa fino
   alla conferma della revisione. La regola applicata dal codice è più ampia del testo della
   specifica.
3. I percorsi frontend in `docs/SHOP_SCHEMA.md:131`, `docs/SHOP_SCHEMA.md:133`,
   `docs/SHOP_SCHEMA.md:147` e `docs/OPEN_QUESTIONS.md:62` omettono le cartelle reali: i file
   sono `frontend/src/lib/shop/shop-sort.ts`, `frontend/src/lib/packs/pack-reveal-phases.ts` e
   `frontend/src/lib/packs/pack-summary.ts`.
4. `docs/PROJECT_STATUS.md:211` elenca `shop-api.ts` e `shop-history-list.svelte` come «Non
   letti»; in questa ricognizione entrambi sono stati letti e confermano la rotta
   `history/all` e il raggruppamento per pilota. La nota è superata per questa istantanea, non
   indica file assenti.
5. `docs/SHOP_SCHEMA.md:176` annovera la «concorrenza» tra i test della 12c; una ricerca nei test
   backend ha trovato test di concorrenza per salvataggio carte admin, revisioni e lock SQLite,
   ma non un test dedicato agli acquisti del negozio. La serializzazione è descritta nel codice,
   non verificata da un test qui individuato.

Nessun documento o codice è stato modificato per risolvere queste discrepanze.

## Perimetro ed esclusioni

**Incluso:** elenco dei negozi e scelta del pilota, vista del negozio, template di pacchetto e di
negozio, pacchetti del campionato, immagini dei pacchetti, costi e valute, disponibilità e
"Terminato", acquisto transazionale, estrazione e consumo delle pool, assegnazione agli inventari,
storico e riepilogo inventario, apertura animata lato client, modelli, migrazione, API, servizi e
test del negozio.

**Escluso:** giocate, tasto S, revisione e conteggi (scheda
[Carte sponsor in gara e revisione](carte-sponsor-e-revisione.md)); costruzione del mazzo da gioco e
inventari del pilota come interfaccia (scheda [Team, piloti e mazzi](team-piloti-e-mazzi.md));
guadagno di oro e punti sponsor dai risultati (scheda
[Gare, risultati e classifica](gare-risultati-e-classifica.md)); amministrazione delle immagini
delle carte, ricarica ed esclusione delle pool (scheda
[Pool, caricamento carte e amministrazione](pool-e-amministrazione-carte.md)); shell, menu e QR
(scheda [Interfaccia, navigazione e QR](interfaccia-navigazione-e-qr.md)); database SQLite reale,
esecuzione test, CI e browser.

Questa scheda è proprietaria di `Pack`, `PackTemplate`, `ShopTemplate`, `ShopTemplatePack`,
`PackPurchase`, dei router `shop`, `shop_play`, `shop_me` e `packs`, dei servizi `shop_*` e
`pack_*` e dei client e componenti del negozio. La pool del campionato è citata solo come sorgente
delle estrazioni; la sua amministrazione resta alla scheda dedicata.

## Revisione e stato del worktree esaminati

- Revisione: `21e17e637b43528d7320e88f0af5623db7158ee9`; branch
  `feat/0.9-mappe-eventi` in tracking con `origin/feat/0.9-mappe-eventi`.
- Worktree invariato: tre file tracciati modificati in fasi documentali precedenti e due
  directory non tracciate. Qui si aggiungono solo scheda e link.
- Non sono stati eseguiti test, né ispezionato il database reale o usato il browser.

## Punti d'ingresso e flusso

### API e contratto

- Router registrati: `packs` e `shop_play` sotto `/api/championships`, `shop_me` sotto `/api/me`,
  `shop` sotto `/api/shop`: `backend/app/main.py:17-20`,
  `backend/app/main.py:73-77`, `backend/app/main.py:81`.
- Template di pacchetto, template di negozio e immagini: CRUD admin, 403 per ruolo non
  autorizzato, 404 per template assente, 409 per nome di negozio in uso, 422 per elenco vuoto,
  duplicati o immagine non disponibile:
  `backend/app/api/shop/shop.py:38-70`,
  `backend/app/api/shop/shop.py:73-167`,
  `backend/app/api/shop/shop.py:170-192`.
- Pacchetti del campionato e pool completa in sola lettura per l'admin, con 404 e 409 su
  campionato assente/chiuso o pacchetto mancante: `backend/app/api/cards/packs.py:25-90`.
- Negozio giocatore: vista con saldo, `read_only`, `locked` e `sold_out`; acquisto che traduce gli
  errori di dominio in 403/404/409; inventario e storico proprio e completo:
  `backend/app/api/shop/shop_play.py:66-108`,
  `backend/app/api/shop/shop_play.py:111-150`,
  `backend/app/api/shop/shop_play.py:153-193`.
- Elenco dei negozi dell'utente: `backend/app/api/shop/shop_me.py:10-23`.
- DTO: costi predefiniti e validazione di nome, valuta, conteggi e filtro; risposta del negozio,
  richiesta di acquisto e carte uscite; storico, inventario, elenco negozi e pool:
  `backend/app/schemas/shop/shop.py:8-46`,
  `backend/app/schemas/shop/shop.py:49-89`,
  `backend/app/schemas/shop/purchase.py:4-55`,
  `backend/app/schemas/shop/history.py:8-26`,
  `backend/app/schemas/shop/shop_inventory.py:6-11`,
  `backend/app/schemas/shop/shop_list.py:4-17`,
  `backend/app/schemas/shop/shop_pool.py:4-21`,
  `backend/app/schemas/cards/pack.py:6-21`.

### Servizi e persistenza descritta

- Valori comuni a template e pacchetti: immagine predefinita o verificata tra quelle disponibili,
  copia dei campi senza commit: `backend/app/services/cards/pack_values.py:8-45`.
- Template di pacchetto e di negozio: collegamenti vivi, indicatore "vuoto" calcolato, nome
  univoco senza distinzione di maiuscole, almeno un template alla creazione, eliminazione che non
  tocca i campionati esistenti:
  `backend/app/services/cards/pack_templates.py:12-55`,
  `backend/app/services/shop/shop_templates.py:29-41`,
  `backend/app/services/shop/shop_templates.py:105-167`.
- Pacchetti del campionato: copie indipendenti, modifica integrale, storico che conserva i valori
  dell'acquisto anche dopo l'eliminazione del pacchetto: `backend/app/services/cards/packs.py:14-75`.
- Immagini: cartelle `defaultIllustration` e `illustration`, massimo 5 MB, estensioni ammesse,
  salvataggio in WebP e ridimensionamento, elenco e verifica del percorso:
  `backend/app/services/cards/pack_images.py:6-65`.
- Accesso e disponibilità: giocatore solo con pilota proprio iscritto e campionato attivo;
  admin in sola lettura senza pilota o a campionato chiuso; `locked` se esiste una gara non
  conclusa; `sold_out` se mancano copie estraibili:
  `backend/app/services/shop/shop_view.py:19-96`,
  `backend/app/services/shop/shop_draw.py:25-42`.
- Acquisto: lock di processo e `BEGIN IMMEDIATE` su SQLite, un solo commit per controlli,
  estrazione, pool, inventari, costo e storico, rollback su errore; tetto di 100 copie e saldo
  scalato nella valuta del pacchetto:
  `backend/app/services/shop/shop_purchase.py:21-26`,
  `backend/app/services/shop/shop_purchase.py:64-78`,
  `backend/app/services/shop/shop_purchase.py:81-163`.
- Estrazione: una carta alla volta, probabilità proporzionale alle copie rimaste ricalcolata a
  ogni estrazione, filtro per nome senza maiuscole, stessa carta ripetibile, pool restituita senza
  carta a zero copie: `backend/app/services/shop/shop_draw.py:6-76`.
- Elenco, storico e inventario: negozi dei campionati attivi con piloti non eliminati; acquisti
  dal più recente raggruppati per pilota con nome copiato; riepilogo senza Velocità 1-4:
  `backend/app/services/shop/shop_list.py:11-40`,
  `backend/app/services/shop/shop_history.py:13-58`,
  `backend/app/services/shop/shop_inventory.py:11-36`.
- Pool del negozio per l'admin: copie rimaste e probabilità percentuale alla prima estrazione
  senza filtro: `backend/app/services/shop/shop_pool.py:9-34`.
- Modelli: campi comuni di template e pacchetti, unicità del nome del template di negozio,
  collegamento con chiave doppia, storico con nomi e carte copiati e riferimenti che diventano
  nulli: `backend/app/db/models/shop.py:13-82`.
- Migrazione descritta: crea le cinque tabelle e aggiunge `sponsor_inventory_deck_id` al pilota
  con un mazzo vuoto per quelli esistenti:
  `backend/alembic/versions/a1c5e9b3d7f2_negozio_tabelle_e_inventario_sponsor.py:20-32`,
  `backend/alembic/versions/a1c5e9b3d7f2_negozio_tabelle_e_inventario_sponsor.py:35-120`.
- **Schema SQLite effettivo non verificato**: tabelle, colonne e indici derivano dai modelli e
  dalla migrazione; il database reale non è stato ispezionato.

### Frontend

- Client del negozio: una funzione per rotta, dal saldo allo storico completo; tipi condivisi e
  scelta del pilota azzerata all'apertura della pagina:
  `frontend/src/lib/shop/shop-api.ts:10-68`,
  `frontend/src/lib/shop/shop-types.ts:3-99`,
  `frontend/src/lib/shop/shop-selection.svelte.ts:1-8`.
- Ordinamento e ricerca locali, carte prima modifiche poi sponsor, URL dell'immagine e
  formattazione di valuta e storico: `frontend/src/lib/shop/shop-sort.ts:3-37`,
  `frontend/src/lib/shop/shop-cards.ts:3-27`,
  `frontend/src/lib/shop/shop-format.ts:3-25`.
- Fasi pure dell'animazione e raggruppamento delle copie uguali per sezione e percorso:
  `frontend/src/lib/packs/pack-reveal-phases.ts:1-35`,
  `frontend/src/lib/packs/pack-summary.ts:1-27`.
- Componente di apertura: busta con texture del pacchetto, strappo, scorrimento, carte una alla
  volta con Invio o Spazio, riepilogo con "x N", "Salta" e `done` che abilita la chiusura fuori
  solo dal riepilogo: `frontend/src/lib/components/packs/pack-reveal.svelte:1-150`.
- Pagine: elenco `/shop` con saldi, negozio del campionato con acquisto e popup, storico
  separato e gestione admin con le due schede dei template:
  `frontend/src/routes/shop/+page.svelte:1-38`,
  `frontend/src/routes/championships/[id]/shop/+page.svelte:27-84`,
  `frontend/src/routes/championships/[id]/shop/+page.svelte:86-151`,
  `frontend/src/routes/championships/[id]/shop/+page.svelte:154-210`,
  `frontend/src/routes/championships/[id]/shop/history/+page.svelte:1-42`,
  `frontend/src/routes/admin/shop/+page.svelte:1-45`.
- Storico diviso per pilota e chiave di elenco basata su id o nome copiato:
  `frontend/src/lib/components/shop/shop-history-list.svelte:1-36`.

## Test individuati (non eseguiti in questa fase)

- `backend/tests/test_shop_purchase.py`, `backend/tests/test_shop_draw.py`,
  `backend/tests/test_shop_routes.py` — acquisto, blocco in gara, esaurimento, estrazione e rotte.
- `backend/tests/test_shop_templates.py`, `backend/tests/test_pack_templates.py`,
  `backend/tests/test_championship_packs.py`, `backend/tests/test_pack_images.py` — template,
  pacchetti del campionato e immagini.
- `backend/tests/test_shop_list.py`, `backend/tests/test_shop_history_inventory.py` — elenco
  negozi, storico e inventario.
- `frontend/src/lib/shop/shop-sort.spec.ts`, `frontend/src/lib/shop/shop-format.spec.ts`,
  `frontend/src/lib/shop/shop-cards.spec.ts`, `frontend/src/lib/shop/shop-api.spec.ts`,
  `frontend/src/lib/admin/shop-admin-validation.spec.ts`,
  `frontend/src/lib/admin/shop-admin-format.spec.ts` — logica pura e client.
- `frontend/src/lib/packs/pack-reveal-phases.spec.ts`,
  `frontend/src/lib/packs/pack-summary.spec.ts` — fasi e raggruppamento; il componente grafico
  non ha test dedicati.

Nessun test è stato eseguito durante la generazione della scheda. I risultati riportati nei
documenti di fase e in `docs/PROJECT_STATUS.md` sono riferiti a fasi diverse e non qui ri-osservati.

## Osservato, dedotto e non verificato

- **Osservato:** router, DTO, modelli, servizi, migrazione, client, pagine, componenti e test
  citati; documenti canonici e note di fase, incluse le affermazioni disallineate elencate sopra.
- **Dedotto dal codice:** il blocco del negozio comprende la revisione perché la gara resta non
  conclusa fino alla conferma; un acquisto scrive pool, inventari, saldo e storico in un solo
  commit; le copie estratte non superano quelle rimaste nella pool; lo storico conserva nome del
  pilota e del pacchetto anche dopo eliminazioni; il frontend disattiva l'acquisto ma il backend
  ha l'ultima parola.
- **Non verificato:** database SQLite reale, esecuzione test, browser, CI, concorrenza effettiva
  con più worker e comportamento dell'animazione nei vari browser.

## Fonti da ricontrollare quando cambiano le fonti pertinenti

- `backend/app/main.py`, `backend/app/api/shop/`, `backend/app/api/cards/packs.py`,
  `backend/app/schemas/shop/`, `backend/app/schemas/cards/pack.py`, `backend/app/db/models/shop.py`.
- `backend/app/services/shop/`, `backend/app/services/cards/pack_*.py`,
  `backend/app/services/race/races.py` per blocco e concorrenza, e
  `backend/alembic/versions/` per le tabelle del negozio.
- `frontend/src/lib/shop/`, `frontend/src/lib/packs/`,
  `frontend/src/lib/components/{shop,packs}/` e `frontend/src/routes/` per le pagine del negozio.
- I test elencati sopra e i documenti canonici linkati all'inizio. Se cambiano valute, costi,
  limiti di copie, filtro, regole di accesso o sequenza di apertura, aggiornare qui i rimandi a
  `PROJECT_SPEC.md`, `SHOP_DESIGN.md` e `SHOP_SCHEMA.md`.
