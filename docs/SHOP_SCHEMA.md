> **STATO: IN IMPLEMENTAZIONE.** Traduzione tecnica di `SHOP_DESIGN.md`. La
> sottofase 12a è completata (tabelle, inventario sponsor, immagini); le altre
> sono da fare. Quando il Negozio sarà finito, le regole passano in
> `PROJECT_SPEC.md`.

# Negozio — schema, servizi, rotte e sottofasi

## 1. Regola aggiunta all'ultimo giro

Un template di negozio che ha perso tutti i suoi template di pacchetto (triangolo
giallo) **non è utilizzabile**: nell'elenco del modulo di creazione del
campionato è disattivato. Questa regola va riportata anche in `SHOP_DESIGN.md`
quando lo si aggiorna.

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

- **Immagini dei pacchetti** (fatto nella 12a, `services/pack_images.py`):
  caricamento (png, jpg/jpeg, webp; massimo 5 MB), conversione in webp e
  ridimensionamento nella scatola 560x870 px con la logica di `services/images.py`;
  elenco delle immagini disponibili; immagine predefinita da `defaultIllustration`.
  Lo script `resize_cards` tratta anche le immagini dei pacchetti.
- **Template di pacchetto e di negozio**: creazione, modifica, eliminazione con le
  regole di `SHOP_DESIGN.md` (almeno un pacchetto alla creazione di un template di
  negozio; indicatore "vuoto" calcolato, non salvato).
- **Pacchetti del campionato**: creazione da un template o da zero, modifica per
  intero, eliminazione. Creazione del campionato con `shop_template_id` facoltativo:
  copia i pacchetti dei template di pacchetto collegati.
- **Acquisto** (unico punto delicato), in una sola transazione:
  1. verifica che il campionato sia attivo, che il pilota appartenga all'utente ed
     sia iscritto, e che non ci sia una gara in corso;
  2. verifica il saldo nella valuta del pacchetto;
  3. per ciascuna pool (modifiche poi sponsor) prende le carte che corrispondono al
     filtro (il nome contiene uno dei termini, senza distinguere le maiuscole;
     filtro disattivato = tutta la pool); se le copie sono meno di quelle da
     estrarre risponde "Terminato";
  4. estrae una carta alla volta con probabilità proporzionale alle copie rimaste e
     toglie una copia dalla pool del campionato;
  5. somma le carte all'inventario delle modifiche o a quello sponsor (tetto 100 per
     carta);
  6. scala il costo, scrive la riga dello storico e restituisce le carte uscite.
  La transazione usa il blocco delle scritture di SQLite e il numero di versione dei
  mazzi: un acquisto concorrente sulla stessa pool riceve l'errore 409 e può
  riprovare.
- **Storico**: elenco per pilota per l'utente (solo i propri piloti iscritti);
  elenco completo per l'admin.
- **Cancellazione del campionato**: deve eliminare anche `pack` e `pack_purchase`
  (da fare nella 12b).

## 5. Rotte proposte (prefisso `/api`)

| Rotta | Chi | Funzione |
|---|---|---|
| `GET/POST /shop/pack-templates`, `GET/PUT/DELETE /shop/pack-templates/{id}` | admin | Template di pacchetto. |
| `GET/POST /shop/shop-templates`, `GET/PUT/DELETE /shop/shop-templates/{id}` | admin | Template di negozio. |
| `GET/POST /shop/images` | admin | Elenco e caricamento delle immagini dei pacchetti. |
| `GET /me/shops` | utente | Campionati attivi in cui ha un pilota iscritto (per la barra e l'elenco). |
| `GET /championships/{id}/shop` | utente con pilota, admin | Pacchetti del negozio con stato (acquistabile, "Terminato", saldo insufficiente). |
| `POST /championships/{id}/packs`, `PUT/DELETE /championships/{id}/packs/{pack_id}` | admin | Pacchetti del campionato (anche da `template_id`). |
| `POST /championships/{id}/packs/{pack_id}/purchase` | utente con pilota | Acquisto; corpo: `pilot_id`. |
| `GET /championships/{id}/shop/history` | utente (propri piloti), admin (tutti) | Storico. |

Errori: 403 senza permesso, 404 elemento assente, 409 negozio bloccato (gara in
corso o campionato chiuso), pacchetto "Terminato", saldo insufficiente o conflitto
di versione, 422 dati non validi.

## 6. Pagine e componenti del frontend

- Barra di navigazione: voce "Negozio" solo con un pilota iscritto.
- `/shop`: elenco dei campionati con negozio. `/shop/[championshipId]`: scelta del
  pilota, due sezioni, pacchetti con ordinamento e ricerca, popup inventario, popup
  storico, animazione di apertura (busta, scorrimento verso il basso, carte verso
  sinistra, sfondo sfocato e bloccato).
- Admin: pagina "Gestione negozio" con due schede (template di pacchetto, template
  di negozio con triangolo giallo); modulo di creazione del campionato con scelta
  del template di negozio; ingranaggio del campionato con "Crea pack", modifica ed
  eliminazione dei pacchetti e storico di tutti i piloti.

## 7. Sottofasi e verifiche

| Sottofase | Contenuto | Test | Stato |
|---|---|---|---|
| 12a | Migrazione, modelli, inventario sponsor e reset, servizio e script delle immagini | Migrazione su e giù, reset all'iscrizione e alla chiusura, caricamento immagini | Completata (248 test) |
| 12b | Template di pacchetto e di negozio, pacchetti del campionato, creazione del campionato con template, rotte delle immagini | Regole di creazione ed eliminazione, copie indipendenti, permessi | Da fare |
| 12c | Acquisto, estrazione, storico | Probabilità per copia, filtro, "Terminato", saldo, gara in corso, campionato chiuso, concorrenza, tetto 100 | Da fare |
| 12d | Frontend del giocatore: elenco, negozio, popup, animazione | Test dei componenti e controlli del frontend | Da fare |
| 12e | Frontend dell'admin: gestione negozio, "Crea pack", storico completo | Come sopra | Da fare |
| 12f | Documenti, `PROJECT_SPEC.md`, stato e note | Revisione finale | Da fare |

Ogni sottofase si chiude con test, controlli e commit sul ramo `phase-12-shop`,
come nelle fasi precedenti.
