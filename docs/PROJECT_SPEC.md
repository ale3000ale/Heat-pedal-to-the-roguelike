# Specifiche del Progetto — Heat

> STATO: APPROVATO. Si aggiorna nel tempo quando emergono nuove esigenze.
> Ultimo aggiornamento: 22 ottobre 2026. Fase 15 unita a main con PR 14 (6dcdc83). Fase 16 sul ramo dedicato, PR 15 in bozza: dominio trasferimenti, integrazione ancora da eseguire.

> Riallineamento autorizzato il 2026-10-22: per SSE, notifiche, timer e stato di
> completamento prevale l'appendice "Fase 15 - specifica consolidata". I passaggi
> delle fasi 13/14 preservati sotto descrivono anche stati storici, non nuove
> attivita' da ricreare. Regole di gioco non coinvolte e testo restante conservati.

## 1. Stack e contesto

- Applicazione web locale basata sul gioco da tavolo Heat.
- Backend: FastAPI. Frontend: SvelteKit (minimal, TypeScript, npm, ESLint, Prettier, Vitest) in `frontend/`.
- Database: SQLite, schema gestito da Alembic. `HeatDB.sql` è lo schema di partenza storico (solo DDL, nessun dato).
- Migrazioni database: Alembic, una migrazione per ogni cambiamento di schema, a partire da una migrazione iniziale che allinea lo schema al modello target.
- Integrazione continua: GitHub Actions esegue i test del backend e i controlli del frontend a ogni pull request.
- Sicurezza flessibile perché l'app è locale, ma progettata per un eventuale uso online futuro. Per l'uso online con SQLite: un solo server con pochi worker, perché SQLite accetta una sola scrittura alla volta.
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
- Le gare non si eliminano a mano: esistono finché esiste il campionato.
- Il Negozio e i pacchetti di carte sono realizzati nella fase 12 (sezione 13). Le carte sponsor giocate in gara sono la fase 13 (sezione 14). L'amministrazione delle carte (caricamento, ritaglio, esclusione nelle pool personalizzate) è prevista nelle sottofasi 13e e 13f (`PHASE_13_SPEC.md`, parte B).
- Lo spareggio sportivo non serve (decisione del 2026-10-12): in caso di pari punti, l'ordine alfabetico serve solo come stabilizzatore di visualizzazione.
- Tutto il lavoro della fase 13 resta nel ramo `phase-13a-card-plays` e nella pull request #9: non si creano rami separati per le sottofasi.

## 3. Autenticazione

- Login con username e password.
- Password salvate con hash (bcrypt o argon2), mai in chiaro.
- Sessione tramite cookie di sessione httpOnly.
- Registrazione libera: chiunque può creare un account.

## 4. Ruoli

- Ruoli previsti: `admin`, `judge` (giudice) e `player`.
- Il primo admin viene creato al primo avvio tramite comando di setup o variabile d'ambiente.
- Admin: crea, chiude e cancella i campionati, gestisce le pool, le impostazioni generali (compreso l'intervallo di controllo delle notifiche) e il Negozio, crea le gare, inserisce e corregge i risultati, assegna il ruolo di giudice, pulisce gli elementi nascosti, riapre la revisione dell'ultima gara.
- Giudice: ruolo fisso, valido per tutti i campionati, assegnato e tolto dall'admin a un utente. Serve a delegare del lavoro all'admin: può creare le gare e terminarle inserendo i risultati e i punti sponsor. Non può correggere una gara già terminata e non ha altri poteri di amministrazione. Può avere team e piloti come un giocatore. Può usare il tasto S su qualsiasi pilota iscritto. Se avvia la revisione di una gara ne diventa il revisore unico e può vedere le carte sponsor giocate, annullarne una, dare un bonus e rimuovere carte (sezione 14).
- Player: gestisce i propri team e piloti.
- Il ruolo dell'admin non si può cambiare, nemmeno da parte dell'admin stesso. Dall'interfaccia si assegna solo `player` o `judge`; l'admin si crea con il setup.
- Ogni risposta dell'API che descrive un utente (login, utente corrente, registrazione) deve poter restituire tutti e tre i ruoli.

## 5. Entità e relazioni

- User 1:N Team
- User 1:N Pilot
- Team 1:N Pilot (il team del pilota è facoltativo)
- Pilot 1:1 Inventario delle modifiche
- Pilot 1:1 Inventario degli sponsor
- Pilot 1:1 Mazzo da gioco
- Championship 1:N ChampionshipPilot
- ChampionshipPilot N:1 Pilot
- Championship 1:N Race
- Race 1:N RaceResult
- Pilot 1:N RaceResult
- Race 1:N CardPlay; Pilot 1:N CardPlay (carte sponsor giocate in gara, sezione 14).
- Race 1:N CardGift; Pilot 1:N CardGift (carte sponsor regalate con il tasto S, sezione 14).
- Race N:1 User tramite `review_started_by_user_id` (revisore unico della gara, facoltativo).
- Championship N:2 pool: una copia della pool delle modifiche e una della pool degli sponsor.
- Championship 1:N Pack (pacchetti del negozio); Championship 1:N PackPurchase (storico).
- DeckPrototype: indipendente, ha un tipo (`modifiche` o `sponsor`); sorgente delle pool di ogni campionato.
- ChampionshipDefaults: una sola riga con le impostazioni generali (regole dell'oro per gara, copiate su ogni nuovo campionato; `card_poll_seconds`, che non si copia e vale per tutti).
- PackTemplate e ShopTemplate: modelli del Negozio gestiti dall'admin (sezione 13).

Nota di modellazione: inventario delle modifiche, inventario degli sponsor e mazzo da gioco sono tre mazzi distinti per pilota, rappresentati da tre riferimenti a `Deck` sul pilota (`inventory_deck_id`, `sponsor_inventory_deck_id` e `game_deck_id`, tutti univoci).

## 6. Mazzi, inventario e pool di carte

- Ogni pilota ha tre mazzi:
  - **Inventario delle modifiche**: tutte le carte possedute dal pilota. Nessun limite di dimensione: la composizione iniziale è solo il punto di partenza. Nel negozio ogni carta ha un tetto di 100 copie.
  - **Inventario degli sponsor**: le carte sponsor ottenute dai pacchetti e dal tasto S; vuoto alla creazione.
  - **Mazzo da gioco**: le carte usate in gara, massimo 15 carte in totale (somma delle copie).
- Il pilota costruisce il mazzo da gioco scegliendo carte dal proprio inventario: per ogni carta, le copie nel mazzo non superano quelle dell'inventario. Nella pagina del pilota le carte si spostano con un clic tra inventario e mazzo.
- I mazzi si possono modificare anche con un campionato attivo; un eventuale blocco varrà solo durante una gara.
- Ogni mazzo ha un numero di versione (blocco ottimistico): se due modifiche si incrociano, la seconda riceve un errore 409.
- Stato iniziale alla creazione del pilota (fisso, indipendente dalle pool):
  - Inventario delle modifiche: Velocità 1, Velocità 2, Velocità 3, Velocità 4, 3 copie ciascuna. La carta Calore parte con 0 copie e non compare nell'elenco.
  - Inventario degli sponsor: vuoto.
  - Mazzo da gioco: vuoto.
- Il pilota ottiene nuove carte tramite i pacchetti del negozio, che consumano le pool del campionato (sezione 13), e le carte sponsor anche con il tasto S (sezione 14).
- Le carte sponsor non entrano nel mazzo da gioco. Si giocano in gara dall'inventario degli sponsor ed escono dall'inventario in modo definitivo alla chiusura della gara, tornando nella pool sponsor del campionato: regole nella sezione 14.
- Nel dettaglio del pilota l'inventario ha due sezioni a scomparsa, "Modifiche" e "Sponsor". Le carte modifica si cliccano per metterle nel mazzo da gioco; le carte sponsor sono in sola lettura.

### Pool di base, pool derivate e pool del campionato

- **Due pool di base, distinte**: la pool delle **modifiche** e la pool degli **sponsor**. Ciascuna è un `DeckPrototype` con il suo tipo ed è il catalogo completo delle carte e delle copie di quel tipo. Nomi tecnici: `default` per le modifiche e `sponsor` per gli sponsor. La pool degli sponsor è usata dai pacchetti per le carte sponsor e dal tasto S.
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
- L'eliminazione definitiva di un pilota rimuove pilota, mazzi, iscrizioni, risultati gara, giocate e notifiche di carte; non modifica la classifica finale congelata dei campionati chiusi. Lo storico degli acquisti resta, con il nome del pilota copiato al momento dell'acquisto.
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

- `Deck.cards` e `DeckPrototype.base_cards`: array JSON di oggetti `{"name": "...", "path": "...", "copies": N}`.
- `name`: nome della carta, unico nel mazzo (senza distinguere le maiuscole); è l'identità della carta.
- `path`: percorso dell'immagine (es. `images/cards/ruota da bagnato_3.webp`).
- `copies`: numero di copie identiche, almeno 1.
- Nessun campo `value`: valori e simboli sono nell'immagine.
- Nome dei file immagine: `nome_N.ext`, dove N è il numero di copie.
- Il backend valida la struttura; il database non ha vincoli `CHECK`.
- Immagini: ridimensionate senza tagliare dentro una scatola massima di 560x870 px (proporzione 5,6 x 8,7 cm).

## 7. Risorse del pilota

- `gold`: denaro spendibile nel negozio. Si ottiene a ogni gara terminata (sezione 9).
- `sponsor`: punti che permettono di riscattare premi nel negozio. Si ottengono a fine gara (sezione 9) e si possono spendere: per questo il totale non si ricalcola mai dalla somma delle gare, ma si aggiorna solo con la differenza quando un risultato viene corretto, senza scendere sotto zero.
- `point`: punti del pilota nel campionato.

## 8. Iscrizione a un campionato

Ad ogni iscrizione a un campionato, tutto il pilota viene reimpostato:

- Inventario delle modifiche: composizione iniziale (Velocità 1-4, 3 copie ciascuna, 0 calore). Il pilota può iscriversi solo se ha un team e non partecipa a un altro campionato attivo.
- Inventario degli sponsor: vuoto.
- Mazzo da gioco: vuoto.
- `gold`, `sponsor`, `point`: 0 (valore predefinito dello schema).

Il pilota può iscriversi solo se non partecipa a un altro campionato attivo. Lo stesso reset si applica ai piloti iscritti anche alla chiusura del campionato; quello dell'iscrizione resta.

## 9. Campionati, gare e classifica

- L'admin crea il campionato scegliendo due pool: una di modifiche e una di sponsor. Per ciascuna può scegliere una pool derivata o, come valore predefinito, la rispettiva pool di base. Può anche scegliere un template di negozio (sezione 13).
- Il nome del campionato è unico senza distinguere maiuscole; la grafia scelta dall'admin è quella mostrata nell'interfaccia.
- Il campionato riceve una copia indipendente di ciascuna delle due pool scelte.
- L'admin può chiudere un campionato anche se alcune gare non sono state create o completate. Dopo la chiusura, il campionato è in sola lettura.
- L'admin può cancellare definitivamente solo un campionato chiuso.

### Impostazioni generali e regole dell'oro

- Le **impostazioni generali** contengono le regole dell'oro per gara e l'intervallo di controllo delle notifiche di carta ottenuta; si modificano dal pannello admin. Le regole dell'oro valgono solo per i campionati creati dopo la modifica.
- L'**intervallo di controllo** (`card_poll_seconds`) è un intero da 1 a 10 secondi, predefinito 5, modificabile solo dall'admin, valido per tutti i campionati (anche quelli già creati). Il giocatore lo legge una volta all'apertura della pagina del campionato.
- Ogni campionato ha le proprie regole dell'oro, copiate dalle impostazioni generali alla creazione. L'admin le modifica dal popup delle impostazioni del campionato (ingranaggio), insieme a chiusura e cancellazione. Aperto dal negozio, lo stesso popup mostra solo pacchetti, pool completa e storico.
- Le regole sono: un **oro base** dato a tutti gli iscritti, un **modificatore** per ciascuna delle posizioni 1-6 e un modificatore "altre" per le posizioni dalla 7ª in poi. Chi non ha corso riceve solo l'oro base. L'oro di una gara non scende mai sotto zero.
- L'oro si assegna **una sola volta**, alla prima chiusura della gara, con le regole del campionato di quel momento. Le correzioni dei risultati non lo modificano.

### Gare

- Ogni gara appartiene a un campionato e riceve automaticamente il numero successivo: 1, 2, 3, ecc. La pagina del campionato mostra le gare dalla più recente (data decrescente, poi numero decrescente).
- La data della gara è quella della creazione. Le gare create prima di questa regola possono non avere data ("Data da definire").
- La gara la crea l'admin o il giudice. In un campionato c'è una sola gara in corso alla volta: una gara è **in corso** finché non ha risultati, **terminata** quando ne ha almeno uno. Creare una nuova gara con una in corso è rifiutato (errore 409); l'interfaccia mostra l'avviso solo quando si preme "Nuova gara".
- Una gara in corso può essere **in revisione** (sezione 14): è uno stato della gara in corso, non una terza fase.
- Massimo 12 piloti partecipanti per gara.
- **Terminare la gara**: coincide con l'inserimento dei risultati. L'admin o il giudice inseriscono la classifica (la posizione deriva dall'ordine) con i punti sponsor di ciascun pilota e indicano a mano i piloti che non partecipano. Ogni iscritto va assegnato alla classifica o ai non partecipanti, e serve almeno un pilota in classifica. Non esiste uno stato salvato. Premere "termina gara" avvia anche la revisione delle carte sponsor (sezione 14).
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
- Pilota: inventario in due sezioni (modifiche e sponsor) e mazzo da gioco, con spostamento delle carte (massimo 15 nel mazzo) e campionato attivo.
- Campionati: elenco di attivi e chiusi (pulsante "+" per crearne uno, solo admin), dettaglio con iscrizione di un pilota, gare ("in corso" o "terminata") e classifica; con una gara in corso, blocco "Le tue carte sponsor" con una sezione per pilota (uso con conferma, annulla ultima); ingranaggio con le impostazioni del campionato (solo admin).
- Gara: classifica, piloti da assegnare, non partecipanti, pulsante "Termina"; correzione solo per l'admin; per giudice e admin, con la gara in corso, la scheda "Piloti iscritti" con il tasto S accanto a ogni pilota; la revisione delle carte è in realizzazione (13d).
- Elenco dei negozi (`/shop`): un riquadro per campionato attivo con i propri piloti iscritti e il loro saldo (oro e punti sponsor); un clic apre il negozio con quel pilota.
- Negozio del campionato: sezioni modifiche e sponsor, pacchetti, acquisto con apertura animata e riepilogo finale, pulsante Inventario (popup di riepilogo); lo storico è una pagina separata (sezione 13).
- Pannello admin, raggiungibile dal menu "Admin" in alto (visibile solo all'admin):
  - pool: elenco, pulsante "Ricarica" per le due pool di base (con conferma se toglie carte), creazione ed eliminazione delle pool derivate, dettaglio con carte rinominabili;
  - creazione, chiusura e cancellazione dei campionati, con la scelta delle due pool (modifiche e sponsor);
  - impostazioni generali (regole dell'oro per i nuovi campionati e intervallo di controllo delle notifiche);
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
| `c3e7a1d5b9f2` registro carte giocate | Tabella `card_play` (gara, pilota, nome e percorso della carta, stato `giocata`/`annullata`/`consumata`, `played_at`), indice su gara e pilota |
| `d4f8b2e6a0c3` gara in revisione | Colonna `review_started_at` (facoltativa) su `race` |
| `e7a3c9d1f5b2` carte regalate | Tabella `card_gift` (gara, pilota, nome e percorso della carta, `created_at`, `seen_at`), indice su pilota e `seen_at` |
| `f8a4d2c6e0b1` intervallo di controllo | Colonna `card_poll_seconds` su `championship_defaults` (valore 5 per la riga esistente) |
| `a9c3e7b1d5f0` revisore unico | Colonna `review_started_by_user_id` (facoltativa) su `race` |

Le differenze elencate nelle prime versioni di questo documento (nome della tabella con lo spazio, elenco piloti in campo testo, mancanza di gare e risultati, mazzi non collegati al pilota, team senza utente, ruolo utente mancante, `deleted_at`) sono risolte da queste migrazioni. I campionati presenti nel database sono solo di prova: non servono regole di conversione per dati reali. Dopo un cambio di computer o un `git pull` è necessario applicare le migrazioni: `python heat.py migrate` (l'avvio lo fa da solo).

## 12. Domande aperte (rinviate)

1. Amministrazione carte: caricamento singolo da interfaccia in `uploads/`, modifica e reset delle carte già presenti nelle pool di base (la ricarica aggiunge e toglie solo in base ai file). Previsto nelle fasi 13e e 13f (`PHASE_13_SPEC.md`, parte B).
2. Interfacce delle carte sponsor non ancora complete: tasto Indietro del giocatore (13c) e revisione nella pagina della gara (13d).
3. Uso online con un database diverso da SQLite: servirà un blocco sulla riga del pilota negli acquisti. L'uso online è rinviato a dopo la fase 14.

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
- Sequenza di apertura, solo grafica (non cambia l'acquisto né il suo esito):
  1. La busta ha come texture l'immagine del pacchetto acquistato e si apre con uno strappo: la striscia superiore se ne va e la busta resta tagliata in alto, con il bordo irregolare.
  2. Le carte compaiono **una alla volta**, già scoperte, prima le carte modifiche e poi le carte sponsor, con il contatore "Carta N di M".
  3. Ogni tocco (oppure Invio o Spazio) fa scorrere la carta corrente a sinistra e mostra la successiva; dopo l'ultima carta un altro tocco apre il riepilogo finale.
  4. Il **riepilogo finale** mostra in una griglia le carte ottenute, ciascuna con la sua immagine e l'etichetta "Modifica" o "Sponsor", con il testo "Hai ottenuto N carte" (N conta tutte le estrazioni). Le copie uguali (stessa sezione e stesso percorso immagine) compaiono una sola volta, con il numero di copie ("x N").
  5. Il pulsante "Salta", presente in ogni fase, porta direttamente al riepilogo.
  6. Fino al riepilogo la finestra si chiude solo con la X: il clic fuori dalla finestra e il tasto Esc non la chiudono. Dal riepilogo si chiude in ogni modo.
  7. Con il movimento ridotto la sequenza parte direttamente dalle carte e lo scorrimento dura 0.

### Storico

- Il giocatore vede lo storico in una pagina separata, raggiungibile dal pulsante "Storico" del negozio: gli acquisti dei propri piloti iscritti, divisi per pilota; non vede quelli di un pilota che ha eliminato.
- L'admin vede la cronologia completa di tutti i piloti dal pulsante "Storico" delle impostazioni del campionato, anche quando sono aperte dal negozio. Dopo la chiusura lo storico resta visibile solo all'admin e sparisce con la cancellazione del campionato.
- Le righe restano se pilota o pacchetto vengono eliminati.

### Stato

Backend (12a-12c) completato e approvato; frontend del giocatore (12d) e dell'admin (12e) completati e verificati a mano dall'autore. La fase 12 è unita in `main`.

## 14. Carte sponsor in gara (fase 13)

La fase 13 ha sottofasi 13a-13g; il piano completo e le decisioni approvate sono in `PHASE_13_SPEC.md`, che resta come storico. Questa sezione fissa le regole approvate. La fase è stata unita in `main` con la pull request #9 il 18 ottobre 2026.

### Chi gioca e quando

- Gioca il **pilota**, cioè l'utente proprietario del pilota (anche se è giudice; l'admin solo se ha un pilota iscritto, come nel negozio).
- Si gioca solo con il pilota iscritto al campionato, con campionato attivo e con la gara **in corso**, cioè senza risultati. Con la gara terminata la giocata e l'annullamento sono rifiutati. Con la gara **in revisione** sono rifiutati anche la giocata, l'annullamento e il tasto S (errore 409).
- Un pilota eliminato non può giocare.

### Cosa si gioca

- Solo carte **sponsor**, scelte dall'**inventario degli sponsor** del pilota (`sponsor_inventory_deck_id`). Le carte modifiche e il mazzo da gioco non c'entrano.
- **Nessun limite al numero di giocate**: il pilota gioca le carte che vuole, finché ne ha copie disponibili.
- Giocando una carta l'inventario sponsor **non viene modificato**. Le giocate sono registrate in una tabella a parte, `card_play`; le copie disponibili di una carta in una gara sono quelle dell'inventario meno le giocate non annullate di quella gara. L'inventario cambia durante la gara solo con il tasto S, con il bonus e con la rimozione del revisore (più sotto).
- La carta si identifica per `name` (come nel formato delle carte, sezione 6); la giocata conserva anche `path` e l'orario.

### Annullamento (Indietro)

- Il pilota può annullare **solo l'ultima carta giocata** (la più recente tra quelle non annullate), fino a un massimo di **5 annullamenti consecutivi**. Annullando, la carta torna disponibile.
- Il conteggio degli annullamenti consecutivi si calcola dal registro nel backend e sopravvive al ricaricamento della pagina. Si azzera quando il pilota gioca una nuova carta.
- Il limite di 5 vale solo per l'annullamento. Il registro completo delle giocate della gara resta intero: le giocate annullate restano nel registro con lo stato `annullata`.
- Non si può annullare a gara terminata né in revisione.

### Registro delle giocate (`card_play`)

- Una riga per ogni giocata: gara, pilota, nome e percorso della carta, stato (`giocata`, `annullata` o `consumata`) e data e ora della giocata (`played_at`). Non si conserva la data dell'annullamento.
- Le righe non si cancellano durante il gioco: una giocata annullata o consumata resta nello storico. Si rimuovono solo con l'eliminazione definitiva del pilota. Le gare non si eliminano a mano.

### Chiusura della gara e consumo delle carte

- Alla chiusura della gara le carte giocate e non annullate escono **in modo definitivo** dall'inventario sponsor dei piloti e **tornano nella copia di pool sponsor del campionato**. Le righe corrispondenti passano allo stato `consumata`. Senza pool sponsor sul campionato le carte escono dall'inventario ma non tornano in nessuna pool.
- La chiusura e il passaggio delle carte avvengono nella stessa operazione: se uno dei due fallisce, non viene salvato nessuno dei due.
- Il passaggio avviene una sola volta, alla prima chiusura della gara. Le correzioni dei risultati e le riconferme della revisione non lo ripetono.

### Revisione della gara (13b)

- La revisione si avvia con "termina gara", da giudice o admin: chi la avvia diventa il **revisore unico** (`review_started_by_user_id`). Ogni altro utente, giudici e admin compresi, riceve 409 su tutte le azioni della revisione.
- Durante la revisione i giocatori non possono giocare, annullare né usare il tasto S (409).
- La revisione **scade dopo 15 minuti** dall'inizio (`review_started_at`): alla prima richiesta successiva (lettura dello stato o creazione di una nuova gara) viene confermata così com'è, senza processi in background.
- Il revisore può **rinunciare** (le giocate non cambiano) o **confermare**. Con la revisione scaduta o mai aperta può confermare solo l'admin.
- L'**admin** può **riaprire** la revisione già confermata della sola ultima gara del campionato: diventa il revisore con altri 15 minuti. Per chi non è admin la riapertura dà 403; per una gara non ultima o una revisione non confermata dà 409.
- Lo stato della revisione (`GET .../review`) è leggibile da ogni utente collegato e riporta `in_review`, `reviewer_user_id`, `review_expires_at`, `review_closed_at` e `is_last_race`.

### Riepilogo e correzioni del revisore

- Il revisore vede le carte giocate da tutti i piloti della gara, raggruppate per pilota, con lo stato di ciascuna giocata.
- **Annullo**: porta una giocata a `annullata` (resta nel registro), anche se già consumata: in quel caso la carta torna al pilota dalla pool sponsor solo se la pool ha ancora una copia uguale, altrimenti 409. Una giocata già annullata è rifiutata (409).
- **Bonus**: una copia di una carta della pool sponsor passa all'inventario del pilota iscritto, senza notifica, per correggere errori. 409 se la carta non è in pool o il campionato è chiuso.
- **Rimozione**: una copia passa dall'inventario sponsor del pilota alla pool sponsor del campionato. 409 se il campionato non ha pool sponsor, se la carta non è nell'inventario o se tutte le copie sono impegnate in giocate attive; 404 per pilota inesistente o eliminato; 403 per pilota non iscritto.

### Tasto S e notifica

- Il tasto S dà al pilota una carta sponsor **casuale** dalla pool sponsor del campionato, con probabilità proporzionale alle copie rimaste. La copia passa dalla pool all'inventario del pilota, e viene creata una riga in `card_gift`; la carta è subito giocabile nella stessa gara.
- Lo premono **giudice e admin**, dalla pagina della gara, su qualsiasi pilota iscritto non eliminato; il giocatore non ha più il tasto S. Chi lo preme vede solo "Carta assegnata a [nome]", non la carta. A livello di backend il giocatore può ancora usarlo solo sui propri piloti (404 sugli altri).
- Con la pool sponsor vuota (409), senza gara in corso o con la gara in revisione il tasto S è rifiutato (409).
- La notifica "Hai ottenuto una carta sponsor" va al proprietario del pilota e resta da leggere finché `seen_at` è vuoto: il giocatore la vede in un popup che si chiude solo con la X e, chiudendosi, segna come viste le notifiche del suo pilota nel campionato. Il bonus del revisore non crea notifiche.

### Intervallo di controllo (13c-1)

- Il giocatore controlla le nuove notifiche a intervalli: valore `card_poll_seconds` delle impostazioni generali (1-10 secondi, predefinito 5), letto con `GET /api/admin/card-poll` e modificato dall'admin con `PUT`. Se la lettura fallisce o il valore non è valido il frontend usa 5 secondi.
- Il controllo parte solo con campionato attivo e almeno un proprio pilota iscritto, e non fa nulla mentre il popup è aperto.

### Amministrazione delle carte (13e, 13f)

- Il solo admin carica le carte: foto da smartphone o file da computer, JPEG, PNG e WebP. Il ritaglio avviene nel frontend: il backend riceve l'immagine già tagliata a 560x870 px, la converte in WebP (qualità 90) e rifiuta con 422 le immagini di dimensioni diverse (`CARD_IMAGE_SIZE` in `config.py`).
- Nome da 1 a 64 caratteri, senza spazi ai bordi, che non comincia con un punto e senza `/ \ : * ? " < > |`; copie da 1 a 999. Nome già usato nella pool di base del tipo (senza distinguere le maiuscole) o file di destinazione già esistente: 409. Dimensione massima `MAX_CARD_UPLOAD_BYTES` in `backend/app/config.py`: 413 se l'intestazione `content-length` lo rivela subito, altrimenti 422.
- Le carte caricate si riconoscono dal percorso `cards/uploads/<tipo>/nome_quantità.webp` (relativo a `backend/media`) e non da colonne del database: la 13e non ha migrazioni. La ricarica della pool di base toglie solo le carte con percorso `cards/base/<tipo>/` e non tocca le caricate. Nelle pagine di gestione delle pool i nomi delle carte caricate sono in arancione.
- Eliminazione: solo l'admin, solo carte caricate (409 per le altre). La carta esce dalla pool di base; le copie già presenti nelle pool dei campionati e negli inventari non cambiano. Il file immagine resta finché un campionato, attivo o chiuso, usa la carta, e viene cancellato quando nessun campionato la usa più; la pulizia dei file orfani avviene anche all'eliminazione di un campionato.
- Nella creazione di una pool personalizzata due tasti escludono in un colpo solo le copie scelte: «Escludi tutte le carte caricate» ed «Escludi tutte le carte di base». Ogni tasto azzera solo le scelte del proprio gruppo nel modulo di creazione, senza toccare il database; le carte di partenza non si toccano.

### Stato

Fase 13 completata e unita in `main` (pull request #9, 18 ottobre 2026). Backend delle sottofasi 13a, 13b, 13c-1 e 13e; frontend della 13c (uso e annulla ultima, sezione del pilota aperta quando è l'unico iscritto, riepilogo con immagini del mazzo da gioco), della 13d (revisione nella pagina della gara), del popup della notifica con controllo periodico, del campo dell'intervallo nelle impostazioni generali, dell'inventario in due sezioni, del tasto S nella pagina della gara e della 13f (caricamento con ritaglio e zoom, elenco con nomi in arancione, eliminazione, tasti di esclusione nelle pool personalizzate). CI verde sui commit della fase e su `main` dopo l'unione. Il ripristino di una carta da parte dell'admin dopo la chiusura non è previsto: la riapertura della revisione e l'annullo di giocate consumate lo sostituiscono.


## Fase 15 - specifica consolidata (2026-10-22)

## Chiusura autorizzata della fase 15 - 2026-10-22

Alle 00:47 CEST l'autore autorizza il riallineamento dei documenti generali e
la chiusura della fase 15 senza riprendere i test manuali non praticabili.
Fase 15 completata e chiusa sul ramo phase-15-sse-sistemazione, con limiti di
collaudo accettati. Non significa PR 14 unita a main o messa in produzione.
Codice finale 1226172, CI ordinaria 39674942800 verde; lifecycle/canvas 8018d18,
CI 39658083388 verde. Sei casi manuali PASS (1/4/5/6/7/9), 2/3 non verificabili,
8/10 non eseguiti. Restano tali: non sono convertiti in PASS. Fix iscrizioni
confermato dall'autore alle 23:24 del 2026-10-21 con "funziona".
Nessun ulteriore collaudo di quei quattro casi e' richiesto per questa chiusura.
Restano fuori da questa accettazione produzione, vulnerabilita' npm,
backup/setup sicuro, configurazione online, nuove fasi e migrazioni reali.
Merge e gestione della PR richiedono una richiesta separata.
Dettagli e verifiche in PHASE_15.md, PHASE_15_BROWSER_CHECKLIST.md,
PHASE_15_ENROLLMENT_LIVE.md e PHASE_15_CLOSURE.md.

### Contratto corrente approvato

- SSE autenticato via cookie e /api/events/stream same-origin. Un client
  condiviso per applicazione nella scheda, registro event_log persistente,
  cursori/Last-Event-ID, resync e auth.expired. Gli eventi invalidano letture
  REST autorizzate, non trasferiscono carte o bozze nei payload pubblici.
- Polling con card_poll_seconds solo come fallback senza stream open; niente
  polling lento di sicurezza con stream aperto. Nessun retry automatico delle
  scritture. Le descrizioni storiche di startGiftPolling non rappresentano
  il collegamento corrente del campionato.
- Timer periodico delle revisioni nel lifespan per worker, ogni 5 secondi,
  con controllo transazionale e stop cooperativo; resta la verifica REST.
  La scadenza non dipende piu' soltanto dal prossimo accesso. Nessuna
  migrazione nel timer. Questo aggiorna i passaggi storici "senza background".
- Conferma notifiche con /seen-selected sui soli ID effettivamente resi,
  per pilota; annulli/chiusure remote non confermano. /seen resta compatibile
  ma non e' il nuovo flusso campionato. Replay non ricrea popup visti.
- Gara: assegnazione ordine/assenti coerente e sponsor per pilota, base server
  distinta dalla bozza, PUT esplicita e conservazione delle modifiche locali.
  Permesso perso rende la bozza readonly, uscite protette senza annullare
  richieste gia' inviate. Nessuna nuova atomicita' fra REST o lock ottimistico.
- Revisione inventari: GET-only al mount, bozza solo propria, chiave
  gara/revisore/inizio controllata. Merge conserva conteggi locali e aggiorna
  metadati remoti; revoca spunte interessate e blocca incompatibilita' senza
  clamp. Rilettura sostitutiva richiede conferma e backup browser riuscito.
  Un nuovo titolare/inizio non riceve automaticamente la vecchia bozza.
- Il pannello gia' mostrato resta sul solo cambio stato nel medesimo contesto
  finche' il ruolo e' ammesso; enabled del genitore congela le azioni senza
  eliminare la copia. Nuovo contesto o perdita ruolo possono smontarlo.
  Riapertura e recupero rispettano il limite, riabilitazione richiede lettura.
- Canvas: controllo nativo con nome/focus, trascinamento e frecce, Maiusc per
  passo fine, Invio/Spazio per esportare. Ruolo img non consentito rimosso,
  senza soppressioni; dimensioni, zoom e WebP invariati.
- Iscrizioni: championship.pilots_changed registrato con iscrizione/reset,
  solo ID campionato, pilot_id nullo e payload vuoto. Solo questo segnale
  canonico raggiunge anche osservatori autenticati non iscritti, coerentemente
  con il dettaglio REST. Non amplia altri eventi o dati privati; modello SQL
  ed endpoint d'iscrizione invariati. Backend e frontend validano il segnale.

### Limiti dell'accettazione

Accettazione funzionale sul ramo e limiti manuali sopra, non certificazione
di accessibilita', carico, proxy/buffering reale, produzione o collaudo completo.
Nessun test saltato dichiarato superato e nessuna nuova esecuzione locale
dell'assistente. Restano separati vulnerabilita' npm, backup/setup e cookie/
percorso SQLite per online. Nessun audit fix/force implicito.
Questa appendice non cambia formati Deck.cards, immagini, stack, dipendenze
o altre regole del Negozio. La discrepanza sul formato carte gia' annotata in
DATABASE.md resta separata, non risolta cambiando dati. Le indicazioni
storiche di migrate/start non autorizzano operazioni sul DB originale:
prima arresto app, backup verificato, prova su copia e permesso esplicito.

## Fase 16 - gestione admin carte e avvio con mazzi da 15

Requisiti approvati: contratto della fase, non funzionalita' gia' integrate.
Per questo ambito prevalgono sui passaggi storici precedenti.

### 1. Obiettivo e accesso

Solo l'admin, dalle opzioni di un campionato, apre una sezione chiamata Piloti.
Elenco dei piloti iscritti con nome del pilota, username del proprietario e pulsante
con icona di carte/mazzo ed etichetta accessibile. Il pulsante apre la gestione
carte di quel pilota nel contesto del campionato selezionato.
Non modifica utenti, team, ruoli, saldi o punteggi. Non amplia i diritti del giudice.

### 2. Schermata

Prima meta', carte del pilota, tre sezioni apribili e distinte:
- Mazzo da gioco, con conteggio delle copie N/15.
- Inventario Modifiche, cioe' copie disponibili fuori dal mazzo.
- Inventario Sponsor.

Seconda meta', due sezioni apribili:
- Pool Modifiche del campionato.
- Pool Sponsor del campionato.

Tutte le carte in queste cinque sezioni hanno immagini e quantita', usando le
risorse correnti. Nessun inventario totale ottenuto sommando visivamente mazzo e
inventario: restano contenitori separati. Su mobile le due aree si dispongono in
sequenza mantenendo le sezioni apribili. Non sono richieste immagini o avatar degli
utenti. Pool di base, prototipi e pool di altri campionati non vengono modificati.

### 3. Spostamenti, una copia per clic

| Carta premuta in | Destinazione |
|---|---|
| Mazzo da gioco | Pool Modifiche del campionato |
| Inventario Modifiche | Pool Modifiche del campionato |
| Inventario Sponsor | Pool Sponsor del campionato |
| Pool Modifiche | Inventario Modifiche del pilota |
| Pool Sponsor | Inventario Sponsor del pilota |

Dalla pool non si aggiunge mai direttamente al mazzo. Le carte sponsor non entrano
nel mazzo da gioco. Ogni clic toglie una copia dalla sorgente selezionata e ne
aggiunge una alla destinazione, senza creare/distruggere copie o sottrarne una
seconda da un altro contenitore. Esempio: rimozione di una copia dal mazzo significa
mazzo -1 e pool Modifiche +1, inventario disponibile invariato. Copie uguali negli
altri contenitori restano al loro posto.

La precedente formulazione sul togliere una carta gia' nel mazzo viene resa
esplicita dalla nuova schermata: si puo' rimuovere proprio la copia della sezione
Mazzo. Non si applica una doppia sottrazione mazzo+inventario per un singolo clic.
Le copie a zero non sono spostabili. I clic modificano soltanto la bozza locale.
Non aggiungere un trasferimento diretto inventario/mazzo in questa schermata;
la costruzione ordinaria del mazzo resta quella del giocatore.

### 4. Salva e riepilogo

Salva in basso a destra apre un modal di conferma prima di scrivere sul server.
Il riepilogo e' testuale, senza immagini, ed elenca le modifiche effettivamente
da applicare, con pilota/utente, nome carta, quantita', sorgente e destinazione.
Mostra anche il nuovo conteggio del mazzo. Le altre rappresentazioni delle carte
restano con immagini, come richiesto dall'autore.

Annulla chiude la conferma senza salvare e conserva la bozza per correggerla.
Solo il comando di conferma invia il salvataggio, proteggendo dai doppi invii.
Salvataggio unico e atomico di tutti i contenitori coinvolti; un errore non deve
lasciare trasferimenti applicati a meta'. La chiusura/uscita con modifiche locali
richiede conferma prima di abbandonarle. Nessun autosalvataggio a ogni clic.

### 5. Quando e' vietato modificare

Campionato chiuso in sola lettura, regola esistente mantenuta. Modifiche vietate
anche con una gara aperta o una revisione non ancora confermata, come chiarito
dall'autore alle 17:49. Il controllo usa lo stato autorevole del backend, non
soltanto pulsanti disabilitati o un timer nel browser.

Ricontrollare stato, ruolo, iscrizione e versioni al salvataggio. Se durante la
bozza si apre una gara, cambia una pool o un altro client modifica i mazzi, non
sovrascrivere silenziosamente: rifiutare il salvataggio incompatibile, spiegare
l'errore e preservare la copia locale. Nessun retry automatico delle scritture.

### 6. Aggiornamento live

Dopo commit riuscito aggiornare la schermata admin, inventari e mazzo del pilota
nelle viste autorizzate gia' aperte. Usare il client SSE condiviso e riletture REST
protette, senza secondo stream, polling continuo o copie private nei segnali
pubblici. Non usare notifiche di regalo/tasto S per questi trasferimenti admin.
Nessun evento di successo o aggiornamento definitivo prima del commit.

### 7. Avvio gara e mazzi da 15

Prima di creare/avviare una nuova gara controllare tutti i piloti iscritti al
campionato: ogni mazzo da gioco deve contenere esattamente 15 copie totali.
Sono 15 carte contate per copia, non 15 nomi diversi e non 15 carte possedute tra
tutti gli inventari. In assenza di una selezione partecipanti prima dell'avvio,
il controllo e' su tutti gli iscritti, non sulla classifica inserita a fine gara.
Non aggiunge nuove regole sul numero minimo di iscritti rispetto a quelle esistenti.

Controllo obbligatorio nel backend, dentro la protezione transazionale dell'avvio.
Se qualche mazzo non e' pronto, nessuna nuova gara o evento race.started; mostrare
ai gestori l'elenco dei piloti non pronti e il loro conteggio N/15. Il controllo
deve restare coerente con modifiche contemporanee del giocatore o dell'admin:
non basta leggere 15 nel frontend prima della richiesta.

Tra le gare un mazzo puo' essere incompleto. Il Salva dell'admin puo' lasciarlo
sotto 15: e' l'avvio gara che viene bloccato finche' il giocatore non lo completa.
Non si cambia automaticamente l'inventario iniziale e non si inventano carte per
arrivare a 15. Restano il massimo di 15 durante la costruzione e gli altri blocchi
esistenti. L'aggiunta dalla pool va nell'inventario, mai direttamente nel mazzo.

### 8. Vincoli tecnici e verifiche

Codice letto: championship-settings.svelte; modelli Pilot e servizi races.py e
pilot_deck.py. Pilot ha tre riferimenti a Deck distinti. move_card sposta copie
fisicamente tra inventario disponibile e game_deck; create_race attuale controlla
stato e gare non concluse ma non la dimensione dei mazzi. Si riusano formato carte,
parser, versioni e risorse correnti, senza trasformare Deck.cards o immagini.
Nessuna migrazione prevista senza prima motivarla e farla autorizzare.

Specifica e stato generali riallineati al perimetro approvato in questo incremento. Endpoint, DTO e file specifici verranno descritti nel relativo blocco,
non presentati come gia' esistenti. Funzioni di dominio piccole e indipendenti;
API, tipi, store, validatori e componenti separati. Nessun falso scaffold frontend.

Test richiesti: movimenti nei cinque sensi, copie e immagini, indipendenza dei
contenitori, conservazione quantita', rollback, ruoli/campionato/iscrizione,
gara/revisione aperta, conflitti e richieste concorrenti, conferma senza scritture
su Annulla, live autorizzato e privacy. Per avvio: 15 validi, incompleti o eccessivi,
elenco non pronti e assenza di nuova gara/evento sul rifiuto, concorrenza con modifiche
mazzo. Aggiornare le fixture dei test senza alterare dati o inventari di produzione.

Lint/check/test/build frontend e suite backend, poi documenti riallineati con esiti
reali; collaudo browser separato. Nessun comando o test eseguito in questa
pubblicazione solo documentale. Nessun accesso, migrazione o reset del DB originale.

## Stato corrente fase 16 - decisione formato e primo dominio (2026-10-22)

Questa sezione aggiorna lo stato corrente; le descrizioni precedenti conservano
la cronologia e non dichiarano nuovamente aperte le fasi gia' unite.
Fase 15 integrata in main con PR 14, merge 6dcdc83. Fase 16 solo su
phase-16-admin-pilot-inventory, PR 15 in bozza, senza merge autorizzato.

Alle 18:49 CEST l'autore conferma il contratto gia' usato dall'applicazione:
Deck.cards resta TEXT con array JSON di name, path e copies. Si mantengono i
percorsi correnti relativi ai media, inclusi cards/starter/velocita-1.webp;
nessuna conversione al precedente esempio path/value o a /images/cards.
Questa decisione aggiorna quel precedente requisito per la fase 16. Nessuna
migrazione, modifica del DB reale, nuovo scaffold o dipendenza introdotta.

backend/app/services/admin_card_transfers.py prepara una copia indipendente dei
cinque contenitori e applica una copia per clic nelle sole direzioni approvate.
Non modifica gli input neppure su errore; non espone endpoint e non salva dati.
Nessuna aggiunta pool/mazzo, nessuna doppia sottrazione. I nomi mantengono
l'identita' normalizzata esistente e le immagini non vengono sostituite.

backend/tests/test_admin_card_transfers.py: 19 test unitari, con cinque sottocasi
per le direzioni. Eseguiti con unittest nell'ambiente isolato dell'assistente
usando cards.py verificato contro il blob b329ece85fef6cc232ef322cb857108088ea5cf7;
esito 19/19 OK. Rieseguiti da questo workflow prima del commit documentale.
Non sono test transazionali/HTTP o di concorrenza, ne' collaudo browser.
La precedente CI 39815434564 era verde prima di questo incremento: non ne e'
una verifica. Rileggere la CI sul nuovo codice; nessun nuovo verde globale gia'
dichiarato. Setup, script d'avvio e schema DB restano invariati.

Da completare nel blocco backend approvato: rotte/DTO admin, iscrizione e username,
letture dei cinque Deck, versioni e salvataggio atomico senza retry automatici,
blocchi gara/revisione/chiusura, eventi privati e segnali senza carte nel payload,
coordinamento con move_card e create_race per il controllo esatto delle 15 copie.
Poi frontend, conferma testuale, live autorizzato e prove browser. Il dominio
puro non garantisce ancora queste integrazioni e non va presentato come funzione
utilizzabile. Nessun test, reset o migrazione sul database reale autorizzato.

## Fase 16 - Incremento API admin di lettura

Data: 2026-10-22. Solo ramo phase-16-admin-pilot-inventory, PR 15 in bozza.
Questo incremento espone letture, non il salvataggio o la gestione frontend.

## Contratto

- GET /api/admin/championships/{championship_id}/pilots: iscritti visibili,
  con pilot_id, name, user_id e username. Solo admin, mai password o sessioni.
- GET /api/admin/championships/{championship_id}/pilots/{pilot_id}/cards:
  metadati del pilota, read_only, blocked_reason e cinque contenitori distinti.
- Ogni contenitore espone available, id, version e cards nel formato corrente
  name/path/copies. Le pool assenti hanno available=false, id/version null e
  cards vuoto; una pool esistente ma vuota e' disponibile. Nessuna pool creata.
- Tutti i Deck presenti vengono letti con una sola query. Riferimenti duplicati
  o mancanti e JSON corrotto danno 409, non carte inventate o svuotate.
- Campionato chiuso, gara o revisione non confermata sono leggibili ma indicati
  in sola lettura. Nessuna conferma automatica della revisione dentro queste GET.
- Il servizio ricontrolla il ruolo oltre alla dipendenza HTTP AdminUser.
  Pilota nascosto o non iscritto: 404. Giudice e giocatore: 403; anonimo: 401.

## File e verifiche

Nuovi schemas/admin_pilot_cards.py, services/admin_pilot_cards.py e
api/admin_pilot_cards.py; main.py registra il router senza alterare lifespan.
Test HTTP in backend/tests/test_admin_pilot_cards_api.py: 13 casi, inclusi i
parametri per ruoli e revisione. Verificano anche assenza di modifiche a Deck
ed EventLog, immagini/versioni, pool assenti o vuote, dati corrotti e privacy.
Alla preparazione: parsing Python e git diff --check riusciti. Test HTTP non
eseguiti localmente: vanno eseguiti nel repository completo, senza dichiararli
PASS sulla sola analisi sintattica. Il workflow documentale li esegue prima di
riallineare i dieci documenti generali e di fase. La CI completa resta separata.

## Limiti e seguito

Nessuna POST/PUT di gestione carte, transazione di salvataggio, evento nuovo,
regola di avvio da 15, modifica ai movimenti del giocatore o interfaccia ancora
aggiunta da questo incremento. Quelle parti restano da implementare e testare.
Le versioni lette non autorizzano una futura scrittura: il salvataggio dovra'
ricontrollare ruolo, iscrizione, stato gara/revisione e tutti i contenitori.
Nessun nuovo schema DB, migrazione, dipendenza o accesso al DB reale. Restano
il formato confermato name/path/copies e i percorsi relativi ai media correnti.
Un messaggio vuoto o solo @GitHub approva la proposta pendente; le sole modifiche
documentali non richiedono attesa della CI applicativa. Nessun merge implicito.

<!-- phase16-admin-save:start -->
## Fase 16 - Salvataggio admin atomico

Data: 2026-10-22. Ramo phase-16-admin-pilot-inventory, PR 15 in bozza.
Questo incremento supera il precedente limite delle sole letture. Frontend e
controllo di avvio gara da 15 copie restano da completare, senza merge implicito.

### Contratto di scrittura

PUT /api/admin/championships/{championship_id}/pilots/{pilot_id}/cards riceve
versions e transfers. versions contiene tutti i cinque contenitori: id/version
interi positivi, oppure null per le sole pool assenti. Ogni trasferimento ha solo
source e path; una copia per elemento, destinazione imposta dal dominio. Campi
extra, sostituzioni arbitrarie delle carte e destinazioni client sono rifiutati.

Ruolo, pilota visibile/iscritto, chiusura e gara/revisione non confermata vengono
ricontrollati nella transazione. Confronto id e versione anche dei contenitori
non toccati; pool assenti non sono create e non possono ricevere o fornire copie.
Conflitto: 409 e nessun retry automatico. Movimento non applicabile: 422.

SQLite acquisisce il lock prima delle letture autorevoli e scade le identita'
SQLAlchemy gia' caricate. Una transazione nativa esistente e' promossa con un
UPDATE senza righe; se lo snapshot non puo' essere promosso si rifiuta la scrittura.
Un solo commit per Deck ed eventi, rollback anche per errore nel registro eventi.
Nessun nuovo schema DB, migrazione, dipendenza o accesso al database reale.

Solo le differenze effettive aggiornano le versioni. Nessuna differenza significa
nessun evento. Il mazzo puo' restare incompleto: nessuna aggiunta pool/mazzo o
sponsor/mazzo, nessuna doppia sottrazione. Risposta con snapshot e versioni nuove.
Dopo variazioni sono accodati cards.changed pubblico vuoto e privato al proprietario
con solo pilot_id: nessun dettaglio carte, regalo o notifica tasto S inventata.

### Verifiche e limiti

Preparati 27 casi in backend/tests/test_admin_pilot_card_save.py: cinque direzioni,
versioni di tutti i contenitori, blocchi, ruoli, input non ammessi, pool assenti o
riassegnate, rollback tardivo/eventi, bozza senza differenze, segnali privi di carte
e due salvataggi concorrenti con sessioni distinte su un SQLite temporaneo.
Test HTTP non eseguiti localmente. Eseguiti invece controlli sintattici e una prova
SQLite isolata: UPDATE senza righe blocca il secondo writer, non incrementa
versioni e rollback libera il lock. Il conteggio dei test e' stato corretto dopo
un NameError del solo script di analisi; nessun risultato HTTP PASS inventato.

Il workflow esegue dominio, letture e salvataggi prima del riallineamento generale.
La CI completa resta da leggere separatamente. Non chiudere/riaprire la PR come
procedura abituale. Per commit solo documentali non attendere la CI applicativa.
Restano da integrare il controllo esatto di 15 all'avvio e il coordinamento con
move_card, interfaccia con conferma testuale e protezione bozza, SSE condiviso e
collaudo browser. Il backend non dimostra ancora queste parti. Il formato resta
TEXT con array name/path/copies e percorsi correnti relativi ai media.

### Riscontro CI e diagnosi sincronizzazione - 2026-10-22 20:15 CEST

La lettura della CI 39827070228 riporta successo per backend pytest, frontend
check/lint/test/build e migrazioni sul database di test. Non e' una nuova
esecuzione dei test in locale e non costituisce un collaudo browser.
Il commit fbc7789 aggiunge il collegamento documentale alla CI, ma al controllo
seguente non risultavano nuovi check o un commit documentale successivo.
La lettura della PR 15 esponeva ancora db94beb: i risultati del connettore non
consentono di distinguere sincronizzazione GitHub da dati non aggiornati.
Nessuna causa certa attribuita a token, eventi o configurazione senza prove.

Per la verifica si usa un aggiornamento reale di questo documento con
create_or_update_file (API Contents), anziche' push_files. Nessuna modifica a
workflow, codice o DB reale e nessuna chiusura/riapertura o merge della PR.
L'effettivo aggiornamento della testa PR e l'avvio dei nuovi controlli vanno
verificati dopo la scrittura: questa nota non dichiara gia' risolto il problema
ne' gia' riallineati i dieci documenti generali. Per il solo aggiornamento
documentale non attendere la CI applicativa.

Test mirati superati dal workflow prima di questo riallineamento; CI completa separata.
<!-- phase16-admin-save:end -->
