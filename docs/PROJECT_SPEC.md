# Specifiche del Progetto — Heat

> STATO: BOZZA IN ATTESA DI APPROVAZIONE.

## 1. Stack e contesto

- Applicazione web locale basata sul gioco da tavolo Heat.
- Backend: FastAPI. Frontend: SvelteKit (minimal, TypeScript, npm, ESLint,
  Prettier, Vitest) in `frontend/`.
- Database: schema attuale in `HeatDB.sql` (solo DDL, nessun dato).
- Migrazioni database: Alembic, una migrazione per ogni cambiamento di schema,
  a partire da una migrazione iniziale che allinea lo schema al modello target.
- Sicurezza flessibile perché l'app è locale, ma progettata per un eventuale
  uso online futuro.

## 2. Decisioni definitive

- Possono esistere più campionati attivi contemporaneamente.
- La cronologia dei campionati chiusi viene mantenuta tramite una classifica finale congelata.
- Cancellare un campionato è un'azione dell'admin, possibile solo dopo la chiusura; rimuove anche gare, risultati, iscrizioni, classifica finale e copia della pool.
- Un campionato chiuso diventa in sola lettura, per tutti, admin compreso.
- Un pilota non può essere iscritto a due campionati attivi contemporaneamente; può iscriversi a uno nuovo dopo la chiusura del precedente.
- Solo l'admin crea, chiude e cancella i campionati.
- L'admin e il giudice creano le gare e le chiudono inserendo i risultati; solo l'admin può correggere i risultati di una gara già chiusa.
- Negozio, amministrazione completa delle carte e spareggio sportivo sono rinviati e non bloccano la prima versione.
- Prima versione del Negozio: solo placeholder "Funzionalità in definizione".
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
- Admin: crea, chiude e cancella i campionati, gestisce le pool, crea le gare, inserisce e corregge i risultati, assegna il ruolo di giudice, pulisce gli elementi nascosti.
- Giudice: ruolo fisso, valido per tutti i campionati, assegnato e tolto dall'admin a un utente. Serve a delegare del lavoro all'admin: può creare le gare e chiuderle inserendo i risultati e i punti sponsor. Non può correggere una gara già chiusa e non ha altri poteri di amministrazione. Può avere team e piloti come un giocatore.
- Player: gestisce i propri team e piloti.
- Il ruolo dell'admin non si può cambiare, nemmeno da parte dell'admin stesso. Dall'interfaccia si assegna solo `player` o `judge`; l'admin si crea con il setup.

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
- DeckPrototype: indipendente, sorgente della pool di carte di ogni campionato.

Nota di modellazione: inventario e mazzo da gioco sono due mazzi distinti per
pilota. La rappresentazione nel database (due riferimenti a `Deck` oppure un
campo tipo) è rinviata alla fase backend e migrazioni.

## 6. Mazzi, inventario e pool di carte

- Ogni pilota ha due mazzi:
  - **Inventario**: tutte le carte possedute dal pilota. Nessun limite di dimensione:
    la composizione iniziale è solo il punto di partenza.
  - **Mazzo da gioco**: le carte usate in gara, massimo 15 carte in totale
    (somma delle copie).
- Il pilota costruisce il mazzo da gioco scegliendo carte dal proprio inventario:
  per ogni carta, le copie nel mazzo non superano quelle dell'inventario.
- Stato iniziale alla creazione del pilota (fisso, indipendente dalla pool):
  - Inventario: Velocità 1, Velocità 2, Velocità 3, Velocità 4, 3 copie ciascuna.
    La carta Calore parte con 0 copie e non compare nell'elenco.
  - Mazzo da gioco: vuoto.
- Il pilota ottiene nuove carte tramite pacchetti, che consumano la pool
  del campionato selezionato.
- La meccanica dei pacchetti (contenuto, costo, apertura) è rinviata.

### Pool di base, pool derivate e pool del campionato

- **Pool di base** (`DeckPrototype` con nome `default`): catalogo completo delle carte e delle copie disponibili.
- **Pool derivata**: l'admin la crea sempre a partire dalla pool di base, senza nuove immagini. Sceglie le carte da includere, il numero di copie di ciascuna (mai superiore a quello della base) e assegna un nome univoco.
- Le pool derivate usano nome, immagine e percorso delle carte già presenti nella pool di base.
- La pool di base non può essere eliminata; una pool derivata può essere eliminata senza modificare i campionati già creati.
- **Pool del campionato**: alla creazione di un campionato, l'admin sceglie una pool; se non la sceglie viene usata la pool di base. Il campionato riceve sempre una copia indipendente della pool selezionata.
- Le modifiche o l'eliminazione della pool di origine non modificano mai la copia già assegnata a un campionato.

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

- `gold`: denaro spendibile nel negozio.
- `sponsor`: punti che permettono di riscattare premi nel negozio. Si ottengono a fine gara (sezione 9) e si possono spendere: per questo il totale non si ricalcola mai dalla somma delle gare, ma si aggiorna solo con la differenza quando un risultato viene corretto, senza scendere sotto zero.
- `point`: punti del pilota nel campionato.

## 8. Iscrizione a un campionato

Ad ogni iscrizione a un campionato, tutto il pilota viene reimpostato:

- Inventario: composizione iniziale (Velocità 1-4, 3 copie ciascuna, 0 calore).
  Il pilota può iscriversi solo se ha un team e non partecipa a un altro campionato attivo.
- Mazzo da gioco: vuoto.
- `gold`, `sponsor`, `point`: 0 (valore predefinito dello schema).

Il pilota può iscriversi solo se non partecipa a un altro campionato attivo.

## 9. Campionati, gare e classifica

- L'admin crea il campionato scegliendo una pool derivata o, come valore predefinito, la pool di base.
- Il nome del campionato è unico senza distinguere maiuscole; la grafia scelta dall'admin è quella mostrata nell'interfaccia.
- Il campionato riceve una copia indipendente della pool scelta.
- L'admin può chiudere un campionato anche se alcune gare non sono state create o completate. Dopo la chiusura, il campionato è in sola lettura.
- L'admin può cancellare definitivamente solo un campionato chiuso.

### Gare

- Ogni gara appartiene a un campionato e riceve automaticamente il numero successivo: 1, 2, 3, ecc.
- La data della gara è facoltativa.
- La gara la crea l'admin o il giudice.
- Massimo 12 piloti partecipanti per gara.
- **Chiusura della gara**: coincide con l'inserimento dei risultati. L'admin o il giudice inseriscono l'elenco ordinato dei piloti (la posizione deriva dall'ordine) e, per ogni pilota, i punti sponsor. Non esiste uno stato salvato: una gara è chiusa quando ha almeno un risultato.
- **Correzione**: solo l'admin può sostituire i risultati di una gara già chiusa (in caso di errore), e solo finché il campionato è attivo. Il giudice che ci prova riceve un rifiuto.
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

- **Punti sponsor**: non dipendono dalla posizione, dipendono da come va la partita. Sono inseriti a mano per ogni pilota, valgono 0 se non indicati e non possono essere negativi. Vengono assegnati al pilota nel momento della chiusura della gara; in una correzione il pilota riceve (o perde) solo la differenza rispetto ai valori precedenti, senza scendere sotto zero.
- Un iscritto che non partecipa a una gara non ha una riga di risultato, ma viene mostrato nel dettaglio della gara con posizione assente, 0 punti e 0 punti sponsor.

### Classifica

- Nel campionato attivo, la classifica è la somma dei punti ottenuti nelle gare (i punti sponsor non contano).
- Include tutti gli iscritti, anche chi non ha partecipato a nessuna gara.
- A pari punti, i piloti condividono la stessa posizione; l'ordine alfabetico stabilizza soltanto la visualizzazione.
- Alla chiusura del campionato viene salvata una classifica finale congelata con: posizione, nome del pilota, punti totali e gare disputate.
- La classifica congelata non conserva il riferimento al pilota: se il pilota viene eliminato definitivamente, lo storico del campionato resta visibile con nome, punti e posizione finale.
- Non viene conservato il dettaglio gara per gara dei piloti eliminati definitivamente.

## 10. Pagine principali

- Login e registrazione.
- Dashboard con i propri team e piloti.
- Gestione di team e piloti.
- Mazzi del pilota: inventario e mazzo da gioco.
- Campionati: elenco di attivi e chiusi, dettaglio, iscrizione di un pilota, gare e classifica.
- Negozio: placeholder "Funzionalità in definizione".
- Gestione gare (admin e giudice):
  - creazione delle gare;
  - chiusura della gara con ordine di arrivo e punti sponsor;
  - correzione dei risultati di una gara chiusa: solo admin.
- Pannello admin:
  - creazione e gestione delle pool derivate;
  - creazione, chiusura e cancellazione dei campionati;
  - elenco degli utenti e assegnazione o rimozione del ruolo di giudice;
  - elenco e pulizia di team e piloti nascosti.

## 11. Schema attuale verificato e differenze

Schema attuale (HeatDB.sql): 6 tabelle `User`, `Pilot`, `Deck`,
`"Championship "`, `Team`, `Deck_prototype`. Nessun dato, indice o vista.
Tutte le foreign key usano `ON UPDATE/DELETE NO ACTION`.

Da risolvere con migrazioni Alembic:

- La tabella `"Championship "` ha uno spazio finale nel nome.
- `Championship.pilots` è TEXT: sostituire con `ChampionshipPilot`.
- Mancano le tabelle `Race` e `RaceResult`.
- `RaceResult` ha bisogno di `sponsor_points` (intero, 0 o più).
- `Deck` non è collegato a `Pilot`: servono inventario e mazzo da gioco.
- `Deck` è oggi collegato solo al campionato (`Championship.deck`).
- `Team` non ha riferimento a `User`: serve per User 1:N Team.
- `User` non ha campo ruolo: serve per admin/judge/player.
- `Pilot.user_id` non ha vincolo UNIQUE, coerente con User 1:N Pilot.
- Nessuna tabella per il Negozio (rinviato).
- `Team` e `Pilot` non hanno `deleted_at`.
- `Pilot.team_id` è obbligatorio: va reso facoltativo.
- I nomi `Team.name` e `Pilot.name` sono unici ma distinguono le maiuscole.

## 12. Domande aperte (rinviate)

1. Negozio: entità, prodotti, prezzi e regole.
2. Amministrazione carte: sincronizzazione, caricamento singolo, modifica e reset
   sono definiti in sezione 6; resta da progettare l'interfaccia di caricamento.
3. Spareggio sportivo: criterio in caso di pari punti.
4. Pacchetti di carte: contenuto, costo e meccanica di apertura.
