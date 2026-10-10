> **STATO: IN IMPLEMENTAZIONE (aggiornato il 10 ottobre 2026).** Traduzione tecnica di
> `SHOP_DESIGN.md`. Le sottofasi 12a, 12b e 12c (backend) sono completate; restano il
> frontend del giocatore (12d), il frontend admin (12e) e i documenti (12f). La pagina
> del negozio ha ora ordinamento, ricerca e saldo in alto a destra; le altre pagine
> esistono già e vanno verificate. Quando il Negozio sarà finito, le regole passano in
> `PROJECT_SPEC.md`.

# Negozio — schema, servizi, rotte e sottofasi

## 1. Regole aggiunte lungo il lavoro

- Un template di negozio che ha perso tutti i suoi template di pacchetto (triangolo
  giallo) **non è utilizzabile**: nell'elenco del modulo di creazione del campionato
  è disattivato. Questa regola va riportata anche in `SHOP_DESIGN.md` quando lo si
  aggiorna.
- Un pacchetto nuovo, se la valuta non è indicata, è in oro; se il costo non è
  indicato vale 10 oro oppure 2 sponsor. I pacchetti già creati non cambiano. Il
  modulo dei pacchetti parte da 10 e, cambiando valuta, passa a 2 (e torna a 10) solo
  se il costo non è stato scelto a mano.
- Le impostazioni del campionato aperte dal negozio mostrano soltanto pacchetti, pool
  completa e storico.

## 2. Tabelle nuove (create dalla migrazione della 12a)

Campi comuni di costo e contenuto (usati da template e pacchetti): `name`,
`image_path`, `currency` (`gold` o `sponsor`), `cost` (intero maggiore di 0),
`modifiche_count` e `sponsor_count` (interi da 0, somma almeno 1),
`filter_enabled`, `filter_text`.

I nomi delle tabelle seguono la convenzione del progetto (singolare), come nel
codice.

| Tabella | Campi principali | Note |
|---|---|---|
| `pack_template` | id, campi comuni, created_at, updated_at | Modelli di pacchetto, solo admin. |
| `shop_template` | id, name (unico, senza distinguere le maiuscole), created_at | Modelli di negozio. |
| `shop_template_pack` | shop_template_id, pack_template_id (chiave doppia) | Collegamento vivo; eliminare un template di pacchetto elimina le sue righe qui (nessun duplicato per costruzione). |
| `pack` | id, championship_id, campi comuni, created_at, updated_at | Pacchetti del campionato: copie indipendenti, cancellati con il campionato. |
| `pack_purchase` | id, championship_id, pilot_id (facoltativo), pilot_name, pack_id (facoltativo), pack_name, currency, cost, cards_modifiche (JSON), cards_sponsor (JSON), purchased_at | Storico. Il nome del pilota e del pacchetto sono copiati al momento dell'acquisto; le righe restano se il pilota o il pacchetto vengono eliminati, e spariscono solo con il campionato. |

## 3. Tabelle esistenti modificate (12a)

- `pilot`: colonna `sponsor_inventory_deck_id` (riferimento univoco a `Deck`), per
  l'inventario delle carte sponsor. La migrazione crea un mazzo vuoto per ogni
  pilota esistente.
- Iscrizione e chiusura del campionato: il reset del pilota svuota anche
  l'inventario sponsor, come reimposta l'inventario delle modifiche.
- `championship`: nessuna colonna nuova; il negozio è l'insieme dei suoi `pack`.

La migrazione Alembic ha uno scaricamento (`downgrade`) che rimuove le tabelle e la
colonna.

## 4. Servizi del backend

- **Immagini dei pacchetti** (12a, `services/pack_images.py`): caricamento (png,
  jpg/jpeg, webp; massimo 5 MB), conversione in webp e ridimensionamento nella
  scatola 560x870 px con la logica di `services/images.py`; elenco delle immagini
  disponibili; immagine predefinita da `defaultIllustration`. Lo script
  `resize_cards` tratta anche le immagini dei pacchetti.
- **Template di pacchetto e di negozio** (12b): creazione, modifica, eliminazione con
  le regole di `SHOP_DESIGN.md` (almeno un pacchetto alla creazione di un template di
  negozio; indicatore "vuoto" calcolato, non salvato).
- **Pacchetti del campionato** (12b): creazione da un template o da zero, modifica per
  intero, eliminazione. Creazione del campionato con `shop_template_id` facoltativo:
  copia i pacchetti dei template di pacchetto collegati. Cancellazione del campionato
  elimina anche `pack` e `pack_purchase`.
- **Estrazione** (12c-1, `services/shop_draw.py`): una carta alla volta con
  probabilità proporzionale alle copie rimaste, ricalcolata dopo ogni estrazione;
  filtro per nome senza distinguere le maiuscole (filtro disattivato = tutta la pool);
  "Terminato" se le copie estraibili sono meno di quelle richieste.
- **Acquisto** (12c-1, `services/shop_purchase.py`), in una sola transazione:
  1. verifica che il campionato sia attivo, che il pilota appartenga all'utente ed
     sia iscritto, e che non ci sia una gara in corso;
  2. verifica il saldo nella valuta del pacchetto;
  3. per ciascuna pool (modifiche poi sponsor) estrae le carte che corrispondono al
     filtro; se le copie sono meno di quelle da estrarre risponde "Terminato";
  4. toglie le copie estratte dalla pool del campionato;
  5. somma le carte all'inventario delle modifiche o a quello sponsor (tetto 100 per
     carta, altrimenti 409);
  6. scala il costo, scrive la riga dello storico e restituisce le carte uscite.
  Gli acquisti sono serializzati: un lock di processo più, su SQLite, `BEGIN
  IMMEDIATE` (`_lock_database`) prima di leggere pool e saldi, così anche più worker
  non possono consumare la stessa copia. Con un database diverso da SQLite il blocco
  sul database non è attivo e servirà un blocco sulla riga del pilota.
- **Vista e accesso** (12c-1, `services/shop_view.py`): il giocatore entra con un
  proprio pilota iscritto e solo a campionato attivo; l'admin entra sempre, in sola
  lettura senza pilota o a campionato chiuso, e con un pilota iscritto si comporta
  come un giocatore. Con una gara in corso gli acquisti sono bloccati.
- **Elenco dei negozi dell'utente** (`api/shop_me.py`, `services/shop_list.py`,
  `schemas/shop_list.py`): `list_my_shops` restituisce i campionati attivi a cui
  l'utente partecipa con un pilota, con i piloti iscritti.
- **Storico e inventario** (12c-2, `services/shop_history.py` e
  `services/shop_inventory.py`): storico dei propri piloti, cronologia completa per
  l'admin raggruppata per pilota; inventari di modifiche e sponsor senza Velocità 1-4.
  Il giocatore non vede gli acquisti di un pilota che ha eliminato; l'admin sì.
- **Ricarica delle pool di base** (fuori dal negozio, ma ne alimenta le pool): prima
  dell'applicazione l'admin vede un'anteprima (`GET /pools/base/{kind}/reload/preview`)
  con le carte da togliere e l'indicazione "presente nella copia di pool di un
  campionato attivo"; poi `POST /pools/base/{kind}/reload` applica.

## 5. Rotte (prefisso `/api`)

| Rotta | Chi | Funzione |
|---|---|---|
| `GET/POST /shop/pack-templates`, `GET/PUT/DELETE /shop/pack-templates/{id}` | admin | Template di pacchetto. |
| `GET/POST /shop/shop-templates`, `GET/PUT/DELETE /shop/shop-templates/{id}` | admin | Template di negozio. |
| `GET/POST /shop/images` | admin | Elenco e caricamento delle immagini dei pacchetti. |
| `POST /championships/{id}/packs`, `PUT/DELETE /championships/{id}/packs/{pack_id}` | admin | Pacchetti del campionato (anche da `template_id`). |
| `GET /me/shops` | utente autenticato | Campionati attivi con negozio a cui l'utente partecipa con un pilota, con i piloti iscritti (alimenta la voce "Negozio" della barra e la scelta del pilota). |
| `GET /championships/{id}/shop?pilot_id=` | utente con pilota, admin | Pacchetti del negozio con stato (acquistabile, "Terminato", saldo insufficiente). |
| `POST /championships/{id}/shop/purchases` | utente con pilota | Acquisto di un pacchetto con un pilota iscritto. |
| `GET /championships/{id}/shop/inventory?pilot_id=` | utente con pilota, admin | Inventari di modifiche e sponsor. |
| `GET /championships/{id}/shop/history` | utente (propri piloti), admin | Storico dei propri piloti. |
| `GET /championships/{id}/shop/history/all` | admin | Cronologia completa. |
| `GET /pools/base/{kind}/reload/preview`, `POST /pools/base/{kind}/reload` | admin | Anteprima e applicazione della ricarica. |

La rotta `GET /me/shops` era stata data per non necessaria (decisione del 10 ottobre
mattina); è invece presente nel backend (`shop_me.py`, montata con prefisso `/api/me`
in `main.py`) ed è usata dal frontend. Il documento è stato corretto leggendo il codice.

Errori: 403 senza permesso, 404 elemento assente, 409 negozio bloccato (gara in
corso o campionato chiuso), pacchetto "Terminato", saldo insufficiente, tetto di copie
dell'inventario o conflitto di versione, 422 dati non validi.

## 6. Pagine e componenti del frontend

- Barra di navigazione: voce "Negozio" solo con un pilota iscritto.
- `/shop`: elenco dei campionati con negozio e scelta del pilota (dati da
  `GET /api/me/shops`).
- `/championships/[id]/shop`: pagina del negozio. In alto a destra il pilota scelto
  con oro e punti sponsor, sotto il pulsante "Inventario" (popup con le carte in
  miniatura), il link "Storico", la scelta del pilota e, per l'admin, l'ingranaggio. Due
  pulsanti scelgono l'area modifiche (pacchetti in oro) o sponsor (punti sponsor); in
  ogni area una barra cerca per nome e un menu ordina i pacchetti (predefinito dal
  meno caro al più caro, poi dal più caro, alfabetico, alfabetico inverso; scelta non
  salvata, logica in `src/lib/shop-sort.ts`). L'animazione di apertura mostra la busta,
  lo scorrimento verso il basso, le carte verso sinistra, lo sfondo sfocato e bloccato.
- `/championships/[id]/shop/history`: storico acquisti come pagina separata (decisione
  del 10 ottobre 2026, al posto del popup previsto prima).
- Admin: pagina "Gestione negozio" con due schede (template di pacchetto, template
  di negozio con triangolo giallo); modulo di creazione del campionato con scelta
  del template di negozio; ingranaggio del campionato con "Crea pack", modifica ed
  eliminazione dei pacchetti e storico di tutti i piloti. Nel negozio l'ingranaggio
  apre solo le impostazioni del negozio (pacchetti, pool completa, storico).
- Pagina admin delle pool: la ricarica passa da un popup di conferma quando deve
  togliere carte.

## 7. Sottofasi e verifiche

| Sottofase | Contenuto | Test | Stato |
|---|---|---|---|
| 12a | Migrazione, modelli, inventario sponsor e reset, servizio e script delle immagini | Migrazione su e giù, reset all'iscrizione e alla chiusura, caricamento immagini | Completata (248 test) |
| 12b | Template di pacchetto e di negozio, pacchetti del campionato, creazione del campionato con template, rotte delle immagini | Regole di creazione ed eliminazione, copie indipendenti, permessi | Completata |
| 12c | Acquisto, estrazione, storico, inventario (backend) | Probabilità per copia, filtro, "Terminato", saldo, gara in corso, campionato chiuso, concorrenza, tetto 100 | Completata e approvata il 10 ottobre 2026 |
| 12d | Frontend del giocatore: elenco, negozio, popup, animazione | `shop-sort.spec.ts` (9 test di ordinamento e ricerca) e controlli del frontend verdi in CI | In corso (negozio con ordinamento, ricerca e saldo fatto; altre pagine da verificare) |
| 12e | Frontend dell'admin: gestione negozio, "Crea pack", storico completo | Come sopra | In corso (pagine presenti da verificare) |
| 12f | Documenti, `PROJECT_SPEC.md`, stato e note | Revisione finale | Da fare |

Ogni sottofase si chiude con test, controlli e commit sul ramo `phase-12-shop`,
come nelle fasi precedenti.
