# Specifiche del Progetto — Heat

> STATO: APPROVATO. Si aggiorna nel tempo quando emergono nuove esigenze. Ultimo aggiornamento: 10 ottobre 2026 (fase 12, Negozio: backend completato, frontend in corso).

## 1. Stack e contesto

- Applicazione web locale basata sul gioco da tavolo Heat.
- Backend: FastAPI. Frontend: SvelteKit (minimal, TypeScript, npm, ESLint,
  Prettier, Vitest) in `frontend/`.
- Database: SQLite, schema gestito da Alembic. `HeatDB.sql` è lo schema di partenza storico (solo DDL, nessun dato).
- Migrazioni database: Alembic, una migrazione per ogni cambiamento di schema,
  a partire da una migrazione iniziale che allinea lo schema al modello target.
- Integrazione continua: GitHub Actions esegue i test del backend e i controlli del frontend a ogni pull request.
- Sicurezza flessibile perché l'app è locale, ma progettata per un eventuale
  uso online futuro. Per l'uso online con SQLite: un solo server con pochi worker, perché SQLite accetta una sola scrittura alla volta.
- Avvio e manutenzione: `python heat.py` (menu) oppure `setup`, `start`, `migrate`, `test`, `check`. L'avvio applica sempre le migrazioni in sospeso.
- Mappa del codice, convenzioni e stato del lavoro: `docs/PROJECT_NOTES.md`.

## 2. Decisioni definitive

- Possono esistere più campionati attivi contemporaneamente.
- La cronologia dei campionati chiusi viene mantenuta tramite una classifica finale congelata.
- Cancellare un campionato è un'azione dell'admin, possibile solo dopo la chiusura; rimuove anche gare, risultati, iscrizioni, classifica finale, copie delle pool, pacchetti e storico degli acquisti.
- Un campionato chiuso diventa in sola lettura, per tutti, admin compreso.
- Un pilota non può essere iscritto a due campionati attivi contemporaneamente; può iscriversi a uno nuovo dopo la chiusura del precedente.
- Solo l'admin crea, chiude e cancella i campionati.
- L'admin e il giudice creano le gare e le terminano inserendo i risultati; solo l'admin può correggere i risultati di una gara già terminata.
- In un campionato c'è al massimo una gara in corso alla volta: finché non è terminata non se ne crea un'altra.
- Il Negozio e i pacchetti di carte sono in realizzazione nella fase 12 (sezione 13). Amministrazione completa delle carte e spareggio sportivo sono rinviati e non bloccano la versione attuale.
- In caso di pari punti, l'ordine alfabetico serve solo come stabilizzatore di visualizzazione, non come spareggio.

## 3. Autenticazione

- Login con username e password.
- Password salvate con hash (bcrypt o argon2), mai in chiaro.
- Sessione tramite cookie di sessione httpOnly.
- Registrazione libera: chiunque può creare un account.

## 4. Ruoli

- Ruoli previsti: `admin`, `judge` (giudice) e `player`.
- Il primo admin viene creato al primo avvio tramite comando di setup
  o variabile d'ambiente.
- Admin: crea, chiude e cancella i campionati, gestisce le pool, le impostazioni generali e il Negozio, crea le gare, inserisce e corregge i risultati, assegna il ruolo di giudice, pulisce gli elementi nascosti.
- Giudice: ruolo fisso, valido per tutti i campionati, assegnato e tolto dall'admin a un utente. Serve a delegare del lavoro all'admin: può creare le gare e terminarle inserendo i risultati e i punti sponsor. Non può correggere una gara già terminata e non ha altri poteri di amministrazione. Può avere team e piloti come un giocatore.
- Player: gestisce i propri team e piloti.
- Il ruolo dell'admin non si può cambiare, nemmeno da parte dell'admin stesso. Dall'interfaccia si assegna solo `player` o `judge`; l'admin si crea con il setup.
- Ogni risposta dell'API che descrive un utente (login, utente corrente, registrazione) deve poter restituire tutti e tre i ruoli.

## 5. Entità e relazioni

- User 1:N Team
- User 1:N Pilot
- Team 1:N Pilot
  (il team del pilota è facoltativo)
- Pilot 1:1 Inventario delle modifiche
- Pilot 1:1 Inventario degli sponsor
- Pilot 1:1 Mazzo da gioco
- Championship 1:N ChampionshipPilot
- ChampionshipPilot N:1 Pilot
- Championship 1:N Race
- Race 1:N RaceResult
- Pilot 1:N RaceResult
- Championship N:2 pool: una copia della pool delle modifiche e una della pool degli sponsor.
- Championship 1:N Pack (pacchetti del negozio); Championship 1:N PackPurchase (storico).
- DeckPrototype: indipendente, ha un tipo (`modifiche` o `sponsor`); sorgente delle pool di ogni campionato.
- ChampionshipDefaults: una sola riga con le impostazioni generali (regole dell'oro per gara), copiate su ogni nuovo campionato.
- PackTemplate e ShopTemplate: modelli del Negozio gestiti dall'admin (sezione 13).

Nota di modellazione: inventario delle modifiche, inventario degli sponsor e mazzo da gioco sono tre mazzi distinti per
pilota, rappresentati da tre riferimenti a `Deck` sul pilota (`inventory_deck_id`, `sponsor_inventory_deck_id` e `game_deck_id`, tutti univoci).

## 6. Mazzi, inventario e pool di carte

- Ogni pilota ha tre mazzi:
  - **Inventario delle modifiche**: tutte le carte possedute dal pilota. Nessun limite di dimensione:
    la composizione iniziale è solo il punto di partenza. Nel negozio ogni carta ha un tetto di 100 copie.
  - **Inventario degli sponsor**: le carte sponsor ottenute dai pacchetti; vuoto alla creazione.
  - **Mazzo da gioco**: le carte usate in gara, massimo 15 carte in totale
    (somma delle copie).
- Il pilota costruisce il mazzo da gioco scegliendo carte dal proprio inventario:
  per ogni carta, le copie nel mazzo non superano quelle dell'inventario. Nella pagina del pilota le carte si spostano con un clic tra inventario e mazzo.
- I mazzi si possono modificare anche con un campionato attivo; un eventuale blocco varrà solo durante una gara.
- Ogni mazzo ha un numero di versione (blocco ottimistico): se due modifiche si incrociano, la seconda riceve un errore 409.
- Stato iniziale alla creazione del pilota (fisso, indipendente dalle pool):
  - Inventario delle modifiche: Velocità 1, Velocità 2, Velocità 3, Velocità 4, 3 copie ciascuna.
    La carta Calore parte con 0 copie e non compare nell'elenco.
  - Inventario degli sponsor: vuoto.
  - Mazzo da gioco: vuoto.
- Il pilota ottiene nuove carte tramite i pacchetti del negozio, che consumano le pool
  del campionato (sezione 13).
- L'uso delle carte sponsor in gara (a consumo) è rinviato.

### Pool di base, pool derivate e pool del campionato

- **Due pool di base, distinte**: la pool delle **modifiche** e la pool degli **sponsor**. Ciascuna è un `DeckPrototype` con il suo tipo ed è il catalogo completo delle carte e delle copie di quel tipo. Nomi tecnici: `default` per le modifiche e `sponsor` per gli sponsor. La pool degli sponsor è usata dai pacchetti per le carte sponsor.
- Le carte Velocità 1-4 non fanno parte di nessuna pool di base, perché sono assegnate di default a tutti i piloti. Le carte Calore sono carte modifiche come le altre.
- **Pool derivata**: l'admin la crea sempre a partire dalla pool di base dello stesso tipo, senza nuove immagini. Sceglie le carte da includere, il numero di copie di ciascuna (mai superiore a quello della base) e assegna un nome univoco.
- Le pool derivate usano nome, immagine e percorso delle carte già presenti nella pool di base. Le carte di una pool si possono rinominare dalla pagina di dettaglio della pool.
- Le pool di base non si possono eliminare; una pool derivata può essere eliminata senza modificare i campionati già creati.
- **Pool del campionato**: ogni campionato ha due pool, una di modifiche e una di sponsor. Alla creazione l'admin sceglie per ciascuna una pool del tipo corrispondente; se non la sceglie viene usata la rispettiva pool di base. Il campionato riceve sempre una copia indipendente di ciascuna pool selezionata.
- Le modifiche o l'eliminazione di una pool di origine non modificano mai la copia già assegnata a un campionato.

### Cartelle delle immagini

Le immagini delle carte stanno in `backend/media/cards/`:

- `base/modifiche/`: la pool di base delle modifiche.
- `base/sponsor/`: la pool di base degli sponsor.
- `starter/`: le carte dell'inventario di partenza dei piloti.
- `uploads/`: carte extra caricate in seguito, utilizzabili nella creazione delle pool.

Le immagini dei pacchetti stanno in `backend/media/pack/` (`defaultIllustration` e `illustration`). Le cartelle si riempiono a mano. Lo script `python -m app.scripts.resize_cards [cartella] [--dry-run]` (da `backend`) porta le immagini in WebP dentro la scatola massima, lasciando intatte quelle già a posto.

### Ricarica delle pool di base

Le carte delle cartelle `base/` entrano nel database con un pulsante "Ricarica" nel pannello admin, uno per ciascuna pool di base.

- La ricarica **aggiunge** in fondo alla pool le carte della cartella che non ci sono ancora e **toglie** dal database le carte il cui file non esiste più. Se la cartella manca o non contiene immagini non toglie nulla. Le carte già presenti non si modificano, così nomi e quantità corretti a mano si conservano.
- Prima di togliere carte l'admin vede un'anteprima (che non scrive nulla) e deve confermare: il popup elenca ogni carta da togliere e indica se è presente nella copia di pool di un campionato attivo. Senza carte da togliere la ricarica parte subito.
- Una carta è considerata già presente se coincide il nome (senza distinguere le maiuscole) oppure il percorso dell'immagine.
- Nome e copie di una carta nuova derivano dal nome del file (`nome_N.ext`). Un file senza il numero finale viene scartato con un avviso.
- Carte con lo stesso nome in due pool di base diverse sono carte distinte.
- Il risultato indica quante carte sono state aggiunte e rimosse, quante già presenti e quali file sono stati scartati.
- All'avvio non viene modificato nessun dato: nel log compare solo un avviso se le cartelle contengono carte non ancora presenti nelle pool.
- Le copie di pool dei campionati e le pool derivate già create non cambiano.

### Eliminazione di team e piloti

- Il player elimina i propri team e piloti in modo logico: la riga resta nel database (`deleted_at`) e scompare dalla sua vista.
- L'eliminazione logica di un pilota o di un team è rifiutata se uno dei piloti coinvolti è iscritto a un campionato attivo.
- L'eliminazione logica di un team nasconde anche tutti i suoi piloti visibili.
- Un elemento nascosto continua a occupare il suo nome fino all'eliminazione definitiva.
- L'admin può eliminare definitivamente un pilota nascosto in qualsiasi momento, purché non sia iscritto a un campionato attivo.
- L'eliminazione definitiva di un pilota rimuove pilota, mazzi, iscrizioni e risultati gara; non modifica la classifica finale congelata dei campionati chiusi. Lo storico degli acquisti resta, con il nome del pilota copiato al momento dell'acquisto.
- L'admin può eliminare definitivamente un team nascosto solo se non contiene più piloti, inclusi quelli già nascosti.
- Dopo 365 giorni dall'eliminazione logica, la pulizia avviene automaticamente: prima i piloti, poi i team. Gli elementi ancora bloccati vengono saltati e riprovati in seguito.
- L'admin può anche eseguire manualmente la pulizia automatica e cancellare prima del termine gli elementi che rispettano le regole.
- Nomi di team e piloti: unici su tutto il gioco, senza distinguere le maiuscole.
- Un pilota può esistere senza team; per iscriversi a un campionato serve un team.

### Elenco dei piloti

- L'elenco dei piloti è paginato (`limit` e `offset`) e si carica a pagine nella pagina dei team.
- Si può cercare per nome e filtrare per team.
- Accanto a ogni pilota compare il campionato attivo a cui è iscritto, se c'è.

### Formato delle carte

- `Deck.cards` e `DeckPrototype.base_cards`: array JSON di oggetti
  `{"name": "...", "path": "...", "copies": N}`.
  - `name`: nome della carta, unico nel mazzo (senza distinguere le maiuscole);
    è l'identità della carta.
  - `path`: percorso dell'immagine (es. `images/cards/ruota da bagnato_3.webp`).
  - `copies`: numero di copie identiche, almeno 1.
- Nessun campo `value`: valori e simboli sono nell'immagine.
- Nome dei file immagine: `nome_N.ext`, dove N è il numero di copie.
- Il backend valida la struttura; il database non ha vincoli `CHECK`.
- Immagini: ridimensionate senza tagliare dentro una scatola massima di
  560x870 px (proporzione 5,6 x 8,7 cm).

## 7. Risorse del pilota

- `gold`: denaro spendibile nel negozio. Si ottiene a ogni gara terminata (sezione 9).
- `sponsor`: punti che permettono di riscattare premi nel negozio. Si ottengono a fine gara (sezione 9) e si possono spendere: per questo il totale non si ricalcola mai dalla somma delle gare, ma si aggiorna solo con la differenza quando un risultato viene corretto, senza scendere sotto zero.
- `point`: punti del pilota nel campionato.

## 8. Iscrizione a un campionato

Ad ogni iscrizione a un campionato, tutto il pilota viene reimpostato:

- Inventario delle modifiche: composizione iniziale (Velocità 1-4, 3 copie ciascuna, 0 calore).
  Il pilota può iscriversi solo se ha un team e non partecipa a un altro campionato attivo.
- Inventario degli sponsor: vuoto.
- Mazzo da gioco: vuoto.
- `gold`, `sponsor`, `point`: 0 (valore predefinito dello schema).

Il pilota può iscriversi solo se non partecipa a un altro campionato attivo.

Lo stesso reset si applica ai piloti iscritti anche alla chiusura del campionato; quello dell'iscrizione resta.

## 9. Campionati, gare e classifica

- L'admin crea il campionato scegliendo due pool: una di modifiche e una di sponsor. Per ciascuna può scegliere una pool derivata o, come valore predefinito, la rispettiva pool di base. Può anche scegliere un template di negozio (sezione 13).
- Il nome del campionato è unico senza distinguere maiuscole; la grafia scelta dall'admin è quella mostrata nell'interfaccia.
- Il campionato riceve una copia indipendente di ciascuna delle due pool scelte.
- L'admin può chiudere un campionato anche se alcune gare non sono state create o completate. Dopo la chiusura, il campionato è in sola lettura.
- L'admin può cancellare definitivamente solo un campionato chiuso.

### Impostazioni generali e regole dell'oro

- Le **impostazioni generali** contengono le regole dell'oro per gara e si modificano dal pannello admin. Valgono solo per i campionati creati dopo la modifica.
- Ogni campionato ha le proprie regole dell'oro, copiate dalle impostazioni generali alla creazione. L'admin le modifica dal popup delle impostazioni del campionato (ingranaggio), insieme a chiusura e cancellazione. Aperto dal negozio, lo stesso popup mostra solo pacchetti, pool completa e storico.
- Le regole sono: un **oro base** dato a tutti gli iscritti, un **modificatore** per ciascuna delle posizioni 1-6 e un modificatore "altre" per le posizioni dalla 7ª in poi. Chi non ha corso riceve solo l'oro base. L'oro di una gara non scende mai sotto zero.
- L'oro si assegna **una sola volta**, alla prima chiusura della gara, con le regole del campionato di quel momento. Le correzioni dei risultati non lo modificano.

### Gare

- Ogni gara appartiene a un campionato e riceve automaticamente il numero successivo: 1, 2, 3, ecc. La pagina del campionato mostra le gare dalla più recente (data decrescente, poi numero decrescente).
- La data della gara è quella della creazione. Le gare create prima di questa regola possono non avere data ("Data da definire").
- La gara la crea l'admin o il giudice. In un campionato c'è una sola gara in corso alla volta: una gara è **in corso** finché non ha risultati, **terminata** quando ne ha almeno uno. Creare una nuova gara con una in corso è rifiutato (errore 409); l'interfaccia mostra l'avviso solo quando si preme "Nuova gara".
- Massimo 12 piloti partecipanti per gara.
- **Terminare la gara**: coincide con l'inserimento dei risultati. L'admin o il giudice inseriscono la classifica (la posizione deriva dall'ordine) con i punti sponsor di ciascun pilota e indicano a mano i piloti che non partecipano. Ogni iscritto va assegnato alla classifica o ai non partecipanti, e serve almeno un pilota in classifica. Non esiste uno stato salvato.
- **Uscita dalla pagina**: se si lascia una gara in corso con una classifica non salvata, un popup chiede conferma ("Esci" o "Rimani"); chiudendo o ricaricando la scheda compare l'avviso del browser.
- **Correzione**: solo l'admin può sostituire i risultati di una gara già terminata (in caso di errore), e solo finché il campionato è attivo. Il giudice che ci prova riceve un rifiuto.
- Un campionato chiuso è in sola lettura per tutti: nessuna creazione di gare e nessuna correzione, nemmeno dell'admin.
- Possono essere inseriti solo piloti iscritti al campionato e ogni pilota può comparire una sola volta.
- Punti per posizione di arrivo:

| Posizione | Punti |
|---|---:|
| 1° | 9 |
| 2° | 6 |
| 3° | 4 |
| 4° | 3 |
| 5° | 2 |
| 6° | 1 |
| 7°–12° | 0 |

- **Punti sponsor**: non dipendono dalla posizione, dipendono da come va la partita. Sono inseriti a mano per ogni pilota, valgono 0 se non indicati e non possono essere negativi. Vengono assegnati al pilota nel momento in cui la gara è terminata; in una correzione il pilota riceve (o perde) solo la differenza rispetto ai valori precedenti, senza scendere sotto zero.
- Un iscritto che non partecipa a una gara non ha una riga di risultato, ma viene mostrato nel dettaglio della gara con posizione assente, 0 punti e 0 punti sponsor.

### Classifica

- Nel campionato attivo, la classifica è la somma dei punti ottenuti nelle gare (i punti sponsor non contano).
- Include tutti gli iscritti, anche chi non ha partecipato a nessuna gara.
- A pari punti, i piloti condividono la stessa posizione (1, 2, 2, 4); l'ordine alfabetico stabilizza soltanto la visualizzazione. Nell'interfaccia ogni riga ha una chiave propria (id del pilota), perché il rango non è univoco.
- Alla chiusura del campionato viene salvata una classifica finale congelata con: posizione, nome del pilota, punti totali e gare disputate.
- La classifica congelata non conserva il riferimento al pilota: se il pilota viene eliminato definitivamente, lo storico del campionato resta visibile con nome, punti e posizione finale.
- Non viene conservato il dettaglio gara per gara dei piloti eliminati definitivamente.

## 10. Pagine principali

- Login e registrazione.
- Dashboard con i propri team e piloti.
- Gestione di team e piloti, con ricerca per nome e filtro per team.
- Pilota: inventario e mazzo da gioco, con spostamento delle carte (massimo 15 nel mazzo) e campionato attivo.
- Campionati: elenco di attivi e chiusi (pulsante "+" per crearne uno, solo admin), dettaglio con iscrizione di un pilota, gare ("in corso" o "terminata") e classifica; ingranaggio con le impostazioni del campionato (solo admin).
- Gara: classifica, piloti da assegnare, non partecipanti, pulsante "Termina"; correzione solo per l'admin.
- Negozio del campionato: sezioni modifiche e sponsor, pacchetti, acquisto con apertura animata e pulsante Inventario (popup di riepilogo); lo storico è una pagina separata (sezione 13).
- Pannello admin, raggiungibile dal menu "Admin" in alto (visibile solo all'admin):
  - pool: elenco, pulsante "Ricarica" per le due pool di base (con conferma se toglie carte), creazione ed eliminazione delle pool derivate, dettaglio con carte rinominabili;
  - creazione, chiusura e cancellazione dei campionati, con la scelta delle due pool (modifiche e sponsor);
  - impostazioni generali (regole dell'oro per i nuovi campionati);
  - elenco degli utenti e assegnazione o rimozione del ruolo di giudice;
  - elenco e pulizia di team e piloti nascosti;
  - gestione del negozio: template di pacchetto e di negozio.
- Conferme e finestre di dialogo: popup propri, mai `dialog` o `confirm` nativi (l'eliminazione di una pool nella pagina admin usa ancora `confirm`: da sostituire).

## 11. Schema e migrazioni

Lo schema è gestito da Alembic (`backend/alembic/versions`), su SQLite. Le migrazioni presenti:

| Migrazione | Contenuto |
|---|---|
| `3201b138ce2e` schema iniziale | Tabelle `user`, `team`, `pilot`, `deck`, `deck_prototype`, `championship`, `championship_pilot`, `race`, `race_result`; ruolo utente (`admin`, `player`); team collegato all'utente; mazzo inventario e mazzo da gioco sul pilota; pool del campionato su `pool_deck_id`; posizione dei risultati limitata a 1-12 |
| `3daf355a6ffd` tabella session | Sessioni di login |
| `9f4d32c3525f` team e pilota | `deleted_at` per l'eliminazione logica, `name_key` obbligatoria e unica per nomi senza distinzione di maiuscole e spazi doppi, `team_id` del pilota facoltativo |
| `c7a1e5d2b9f4` nome campionato | Nome normalizzato del campionato per l'unicità senza distinguere le maiuscole |
| `d4e8a2b6c1f7` giudice e sponsor | Ruolo `judge` nel vincolo dei ruoli; colonna `sponsor_points` in `race_result` (predefinito 0, mai negativa) |
| `e5b9c3d7a2f8` tipo pool e pool sponsor | Colonna `kind` su `DeckPrototype` (`modifiche` o `sponsor`), pool sponsor di base, seconda pool (`sponsor_pool_deck_id`) sul campionato |
| `f6c0d4e8b3a9` classifica finale | Tabella `championship_standing` (classifica congelata alla chiusura del campionato) |
| `a7d1e9c4b2f6` indice iscrizioni | Indice su `championship_pilot.pilot_id` per le ricerche per pilota |
| `b8e2f0a5c3d7` versione mazzi | Colonna `version` su `deck` (blocco ottimistico) |
| `c9f3a1b6d8e4` oro per gara | Regole dell'oro sul campionato e tabella delle impostazioni generali (`ChampionshipDefaults`) |
| `a1c5e9b3d7f2` Negozio | Tabelle `pack_template`, `shop_template`, `shop_template_pack`, `pack`, `pack_purchase`; colonna `sponsor_inventory_deck_id` sul pilota (con un mazzo sponsor vuoto per ogni pilota esistente) |
| `b2d6f0a4c8e1` unione delle teste | Unisce le due teste di migrazione; dopo l'unione `alembic downgrade -1` dà "Ambiguous walk": si usa la revisione precisa |

Le differenze elencate nelle prime versioni di questo documento (nome della tabella con lo spazio, elenco piloti in campo testo, mancanza di gare e risultati, mazzi non collegati al pilota, team senza utente, ruolo utente mancante, `deleted_at`) sono risolte da queste migrazioni. I campionati presenti nel database sono solo di prova: non servono regole di conversione per dati reali.

Dopo un cambio di computer o un `git pull` è necessario applicare le migrazioni: `python heat.py migrate` (l'avvio lo fa da solo).

## 12. Domande aperte (rinviate)

1. Amministrazione carte: caricamento singolo da interfaccia in `uploads/`, modifica e reset delle carte già presenti nelle pool di base (la ricarica aggiunge e toglie solo in base ai file).
2. Spareggio sportivo: criterio in caso di pari punti.
3. Carte sponsor a consumo: uso in gara, consumo, ingresso nel mazzo da gioco (vedi `OPEN_QUESTIONS.md`).
4. Uso online con un database diverso da SQLite: servirà un blocco sulla riga del pilota negli acquisti.

## 13. Negozio e pacchetti (fase 12)

Il funzionamento esteso è in `SHOP_DESIGN.md`, lo schema tecnico, i servizi e le rotte in `SHOP_SCHEMA.md`. Regole fissate:

### Accesso

- Il giocatore entra nel negozio di un campionato solo con un proprio pilota iscritto; se ne ha più di uno nello stesso campionato sceglie con quale proseguire.
- L'elenco dei campionati con negozio e dei piloti iscritti, usato per la barra di navigazione e per la scelta del pilota, viene da `GET /api/me/shops`.
- L'admin entra in ogni negozio, anche senza pilota, in sola lettura; con un pilota iscritto nel campionato si comporta come un giocatore. Il giudice senza pilota iscritto non ha accesso.
- Con una gara in corso il negozio si blocca (nessun acquisto). A campionato chiuso il negozio non è più disponibile per gli utenti; l'admin lo apre in sola lettura.
- Un pilota eliminato non può comprare durante un campionato attivo.

### Pagina del negozio

- In alto a destra compaiono il nome del pilota scelto, il suo oro e i suoi punti sponsor.
- Due sezioni, modifiche e sponsor, che distinguono **solo la valuta**: i pacchetti pagati in oro stanno nella sezione modifiche, quelli pagati in punti sponsor nella sezione sponsor. Le carte che escono da un pacchetto non dipendono dalla sezione.
- Un solo pulsante Inventario, uguale per le due sezioni, apre un popup con il riepilogo dell'inventario del pilota (miniature con il numero di copie, senza le carte Velocità 1-4); il resto della pagina elenca i pacchetti. Un pulsante separato, Storico, porta alla pagina dello storico.
- Ordinamento e ricerca sono scelte del singolo giocatore e non vengono salvate: di default dal meno caro al più caro, oppure dal più caro al meno caro, alfabetico o alfabetico inverso, con una barra di ricerca per nome.
- Con saldo insufficiente si disattiva solo il pulsante d'acquisto di quel pacchetto, che resta visibile con il suo prezzo.

### Template e pacchetti

- L'admin crea template di pacchetto (nome, immagine, valuta oro o sponsor, costo maggiore di 0, carte da estrarre per ciascuna pool, filtro per nome facoltativo) e template di negozio, che raccolgono template di pacchetto senza ripeterli. Un template di negozio si crea con almeno un template di pacchetto; se poi li perde tutti resta, con un avviso, e non è utilizzabile alla creazione del campionato.
- Un nuovo campionato nasce con il negozio vuoto oppure da un template di negozio scelto solo nel modulo di creazione. I pacchetti ottenuti sono copie indipendenti: le modifiche successive ai template non toccano i campionati esistenti. L'admin può anche creare, modificare ed eliminare pacchetti del campionato, partendo o no da un template.
- Le carte da estrarre dalla pool delle modifiche sono 3 se non indicate; ciascun numero può essere 0 ma la somma deve essere almeno 1. Se la valuta non è indicata è oro; se il costo non è indicato vale 10 oro o 2 punti sponsor, secondo la valuta.
- Il filtro è unico per pacchetto, si applica a entrambe le pool, si basa solo sul nome della carta senza distinguere le maiuscole e accetta più nomi separati da virgola.
- Una modifica a un pacchetto vale subito per gli acquisti successivi; lo storico conserva i valori del momento dell'acquisto. I nomi dei pacchetti non devono essere unici.
- L'immagine predefinita sta in `backend/media/pack/defaultIllustration`; se ne può caricare un'altra (massimo 5 MB, png, jpg/jpeg o webp, convertita in webp nella scatola massima delle carte).

### Acquisto

- Operazione unica: controllo del saldo, estrazione di una carta alla volta con probabilità proporzionale alle copie rimaste (ricalcolata dopo ogni estrazione), filtro per nome, copie tolte dalla pool del campionato, carte aggiunte all'inventario, costo scalato e riga di storico.
- Se le copie rimaste nel sottoinsieme filtrato sono meno di quelle richieste, il pacchetto non si compra e al posto del prezzo compare "Terminato".
- Le copie ottenute si sommano a quelle possedute, con un tetto di 100 per carta (oltre, l'acquisto è rifiutato con 409). Gli acquisti sono serializzati con un blocco sul database.
- Nell'animazione di apertura si mostrano prima le carte modifiche e poi le carte sponsor.

### Storico

- Il giocatore vede lo storico in una pagina separata, raggiungibile dal pulsante "Storico" del negozio: gli acquisti dei propri piloti iscritti, divisi per pilota; non vede quelli di un pilota che ha eliminato.
- L'admin vede la cronologia completa dalle impostazioni del campionato. Dopo la chiusura lo storico resta visibile solo all'admin e sparisce con la cancellazione del campionato.
- Le righe restano se pilota o pacchetto vengono eliminati.

### Stato

Backend (12a-12c) completato e approvato; frontend del giocatore (12d) e dell'admin (12e) in corso.
