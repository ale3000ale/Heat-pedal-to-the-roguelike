# Specifiche del Progetto — Heat

> STATO: APPROVATO. Si aggiorna nel tempo quando emergono nuove esigenze.

## 1. Stack e contesto

- Applicazione web locale basata sul gioco da tavolo Heat.
- Backend: FastAPI. Frontend: SvelteKit (minimal, TypeScript, npm, ESLint,
  Prettier, Vitest) in `frontend/`.
- Database: SQLite, schema gestito da Alembic. `HeatDB.sql` è lo schema di partenza storico (solo DDL, nessun dato).
- Migrazioni database: Alembic, una migrazione per ogni cambiamento di schema,
  a partire da una migrazione iniziale che allinea lo schema al modello target.
- Integrazione continua: GitHub Actions esegue i test del backend e i controlli del frontend a ogni pull request.
- Sicurezza flessibile perché l'app è locale, ma progettata per un eventuale
  uso online futuro.
- Avvio e manutenzione: `python heat.py` (menu) oppure `setup`, `start`, `migrate`, `test`, `check`. L'avvio applica sempre le migrazioni in sospeso.
- Mappa del codice, convenzioni e stato del lavoro: `docs/PROJECT_NOTES.md`.

## 2. Decisioni definitive

- Possono esistere più campionati attivi contemporaneamente.
- La cronologia dei campionati chiusi viene mantenuta tramite una classifica finale congelata.
- Cancellare un campionato è un'azione dell'admin, possibile solo dopo la chiusura; rimuove anche gare, risultati, iscrizioni, classifica finale e copie delle pool.
- Un campionato chiuso diventa in sola lettura, per tutti, admin compreso.
- Un pilota non può essere iscritto a due campionati attivi contemporaneamente; può iscriversi a uno nuovo dopo la chiusura del precedente.
- Solo l'admin crea, chiude e cancella i campionati.
- L'admin e il giudice creano le gare e le terminano inserendo i risultati; solo l'admin può correggere i risultati di una gara già terminata.
- In un campionato c'è al massimo una gara in corso alla volta: finché non è terminata non se ne crea un'altra.
- Negozio, pacchetti di carte, amministrazione completa delle carte e spareggio sportivo sono rinviati e non bloccano la versione attuale.
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
- Admin: crea, chiude e cancella i campionati, gestisce le pool e le impostazioni generali, crea le gare, inserisce e corregge i risultati, assegna il ruolo di giudice, pulisce gli elementi nascosti.
- Giudice: ruolo fisso, valido per tutti i campionati, assegnato e tolto dall'admin a un utente. Serve a delegare del lavoro all'admin: può creare le gare e terminarle inserendo i risultati e i punti sponsor. Non può correggere una gara già terminata e non ha altri poteri di amministrazione. Può avere team e piloti come un giocatore.
- Player: gestisce i propri team e piloti.
- Il ruolo dell'admin non si può cambiare, nemmeno da parte dell'admin stesso. Dall'interfaccia si assegna solo `player` o `judge`; l'admin si crea con il setup.
- Ogni risposta dell'API che descrive un utente (login, utente corrente, registrazione) deve poter restituire tutti e tre i ruoli.

## 5. Entità e relazioni

- User 1:N Team
- User 1:N Pilot
- Team 1:N Pilot
  (il team del pilota è facoltativo)
- Pilot 1:1 Inventario
- Pilot 1:1 Mazzo da gioco
- Championship 1:N ChampionshipPilot
- ChampionshipPilot N:1 Pilot
- Championship 1:N Race
- Race 1:N RaceResult
- Pilot 1:N RaceResult
- Championship N:2 pool: una copia della pool delle modifiche e una della pool degli sponsor.
- DeckPrototype: indipendente, ha un tipo (`modifiche` o `sponsor`); sorgente delle pool di ogni campionato.
- ChampionshipDefaults: una sola riga con le impostazioni generali (regole dell'oro per gara), copiate su ogni nuovo campionato.

Nota di modellazione: inventario e mazzo da gioco sono due mazzi distinti per
pilota, rappresentati da due riferimenti a `Deck` sul pilota (`inventory_deck_id` e `game_deck_id`, entrambi univoci).

## 6. Mazzi, inventario e pool di carte

- Ogni pilota ha due mazzi:
  - **Inventario**: tutte le carte possedute dal pilota. Nessun limite di dimensione:
    la composizione iniziale è solo il punto di partenza.
  - **Mazzo da gioco**: le carte usate in gara, massimo 15 carte in totale
    (somma delle copie).
- Il pilota costruisce il mazzo da gioco scegliendo carte dal proprio inventario:
  per ogni carta, le copie nel mazzo non superano quelle dell'inventario. Nella pagina del pilota le carte si spostano con un clic tra inventario e mazzo.
- I mazzi si possono modificare anche con un campionato attivo; un eventuale blocco varrà solo durante una gara.
- Ogni mazzo ha un numero di versione (blocco ottimistico): se due modifiche si incrociano, la seconda riceve un errore 409.
- Stato iniziale alla creazione del pilota (fisso, indipendente dalle pool):
  - Inventario: Velocità 1, Velocità 2, Velocità 3, Velocità 4, 3 copie ciascuna.
    La carta Calore parte con 0 copie e non compare nell'elenco.
  - Mazzo da gioco: vuoto.
- Il pilota ottiene nuove carte tramite pacchetti, che consumano le pool
  del campionato selezionato.
- La meccanica dei pacchetti (contenuto, costo, apertura) è rinviata.

### Pool di base, pool derivate e pool del campionato

- **Due pool di base, distinte**: la pool delle **modifiche** e la pool degli **sponsor**. Ciascuna è un `DeckPrototype` con il suo tipo ed è il catalogo completo delle carte e delle copie di quel tipo. Nomi tecnici: `default` per le modifiche e `sponsor` per gli sponsor. La versione attuale usa le modifiche; la pool degli sponsor è predisposta.
- Le carte Velocità 1-4 non fanno parte di nessuna pool di base, perché sono assegnate di default a tutti i piloti. Le carte Calore, per ora, sono considerate parte delle modifiche e verranno aggiunte con le foto.
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

Le cartelle si riempiono a mano. Lo script `python -m app.scripts.resize_cards [cartella] [--dry-run]` (da `backend`) porta le immagini in WebP dentro la scatola massima, lasciando intatte quelle già a posto.

### Ricarica delle pool di base

Le carte delle cartelle `base/` entrano nel database con un pulsante "Ricarica" nel pannello admin, uno per ciascuna pool di base.

- La ricarica **aggiunge soltanto**: legge la cartella e accoda in fondo alla pool le carte che non ci sono ancora. Non modifica e non toglie mai le carte già presenti, così nomi e quantità corretti a mano si conservano.
- Una carta è considerata già presente se coincide il nome (senza distinguere le maiuscole) oppure il percorso dell'immagine.
- Nome e copie di una carta nuova derivano dal nome del file (`nome_N.ext`). Un file senza il numero finale viene scartato con un avviso.
- Carte con lo stesso nome in due pool di base diverse sono carte distinte.
- Il risultato indica quante carte sono state aggiunte, quante già presenti e quali file sono stati scartati.
- All'avvio non viene modificato nessun dato: nel log compare solo un avviso se le cartelle contengono carte non ancora presenti nelle pool.
- Le carte tolte dalla cartella restano nella pool. Gli eventuali campionati e pool derivate non cambiano.

### Eliminazione di team e piloti

- Il player elimina i propri team e piloti in modo logico: la riga resta nel database (`deleted_at`) e scompare dalla sua vista.
- L'eliminazione logica di un pilota o di un team è rifiutata se uno dei piloti coinvolti è iscritto a un campionato attivo.
- L'eliminazione logica di un team nasconde anche tutti i suoi piloti visibili.
- Un elemento nascosto continua a occupare il suo nome fino all'eliminazione definitiva.
- L'admin può eliminare definitivamente un pilota nascosto in qualsiasi momento, purché non sia iscritto a un campionato attivo.
- L'eliminazione definitiva di un pilota rimuove pilota, mazzi, iscrizioni e risultati gara; non modifica la classifica finale congelata dei campionati chiusi.
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

- Inventario: composizione iniziale (Velocità 1-4, 3 copie ciascuna, 0 calore).
  Il pilota può iscriversi solo se ha un team e non partecipa a un altro campionato attivo.
- Mazzo da gioco: vuoto.
- `gold`, `sponsor`, `point`: 0 (valore predefinito dello schema).

Il pilota può iscriversi solo se non partecipa a un altro campionato attivo.

Lo stesso reset si applica ai piloti iscritti anche alla chiusura del campionato; quello dell'iscrizione resta.

## 9. Campionati, gare e classifica

- L'admin crea il campionato scegliendo due pool: una di modifiche e una di sponsor. Per ciascuna può scegliere una pool derivata o, come valore predefinito, la rispettiva pool di base.
- Il nome del campionato è unico senza distinguere maiuscole; la grafia scelta dall'admin è quella mostrata nell'interfaccia.
- Il campionato riceve una copia indipendente di ciascuna delle due pool scelte.
- L'admin può chiudere un campionato anche se alcune gare non sono state create o completate. Dopo la chiusura, il campionato è in sola lettura.
- L'admin può cancellare definitivamente solo un campionato chiuso.

### Impostazioni generali e regole dell'oro

- Le **impostazioni generali** contengono le regole dell'oro per gara e si modificano dal pannello admin. Valgono solo per i campionati creati dopo la modifica.
- Ogni campionato ha le proprie regole dell'oro, copiate dalle impostazioni generali alla creazione. L'admin le modifica dal popup delle impostazioni del campionato (ingranaggio), insieme a chiusura e cancellazione.
- Le regole sono: un **oro base** dato a tutti gli iscritti, un **modificatore** per ciascuna delle posizioni 1-6 e un modificatore "altre" per le posizioni dalla 7ª in poi. Chi non ha corso riceve solo l'oro base. L'oro di una gara non scende mai sotto zero.
- L'oro si assegna **una sola volta**, alla prima chiusura della gara, con le regole del campionato di quel momento. Le correzioni dei risultati non lo modificano.

### Gare

- Ogni gara appartiene a un campionato e riceve automaticamente il numero successivo: 1, 2, 3, ecc.
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
- Pannello admin, raggiungibile dal menu "Admin" in alto (visibile solo all'admin):
  - pool: elenco, pulsante "Ricarica" per le due pool di base, creazione ed eliminazione delle pool derivate, dettaglio con carte rinominabili;
  - creazione, chiusura e cancellazione dei campionati, con la scelta delle due pool (modifiche e sponsor);
  - impostazioni generali (regole dell'oro per i nuovi campionati);
  - elenco degli utenti e assegnazione o rimozione del ruolo di giudice;
  - elenco e pulizia di team e piloti nascosti.
- Conferme e finestre di dialogo: popup propri, mai `dialog` o `confirm` nativi.
- Negozio: rinviato, nessuna rotta.

Stato di realizzazione (7 ottobre 2026): tutte le pagine elencate sopra sono realizzate, eccetto il Negozio.

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

Le differenze elencate nelle prime versioni di questo documento (nome della tabella con lo spazio, elenco piloti in campo testo, mancanza di gare e risultati, mazzi non collegati al pilota, team senza utente, ruolo utente mancante, `deleted_at`) sono risolte da queste migrazioni. I campionati presenti nel database sono solo di prova: non servono regole di conversione per dati reali.

Punti ancora aperti nello schema:

- Nessuna tabella per il Negozio (rinviato).
- Dopo un cambio di computer o un `git pull` è necessario applicare le migrazioni: `python heat.py migrate` (l'avvio lo fa da solo).

## 12. Domande aperte (rinviate)

1. Negozio: entità, prodotti, prezzi e regole (uso di gold e punti sponsor).
2. Amministrazione carte: caricamento singolo da interfaccia in `uploads/`, modifica e reset delle carte già presenti nelle pool di base (la ricarica aggiunge soltanto).
3. Spareggio sportivo: criterio in caso di pari punti.
4. Pacchetti di carte: contenuto, costo e meccanica di apertura.
5. Uso della pool degli sponsor nel gioco (predisposta, non ancora usata).
