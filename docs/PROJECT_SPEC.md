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
- La cronologia dei campionati chiusi deve essere mantenuta.
- Cancellare un campionato è un'azione dell'admin e rimuove anche il suo storico.
- Un campionato chiuso diventa in sola lettura e resta nella cronologia.
- Un pilota non può essere iscritto a due campionati contemporaneamente;
  può iscriversi a un nuovo campionato dopo la chiusura del precedente.
- Solo l'admin crea e chiude i campionati.
- Negozio, amministrazione carte e spareggio sportivo sono rinviati
  e non bloccano la prima versione.
- Prima versione del Negozio: solo placeholder "Funzionalità in definizione".
- In caso di pari punti, l'ordine alfabetico serve solo come stabilizzatore
  di visualizzazione, non come spareggio.

## 3. Autenticazione

- Login con username e password.
- Password salvate con hash (bcrypt o argon2), mai in chiaro.
- Sessione tramite cookie di sessione httpOnly.
- Registrazione libera: chiunque può creare un account.

## 4. Ruoli

- Ruoli previsti: `admin` e `player`.
- Il primo admin viene creato al primo avvio tramite comando di setup
  o variabile d'ambiente.
- Admin: crea e chiude campionati, gestisce le gare, inserisce i risultati.
- Player: gestisce i propri team e piloti.

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

### Pool di base e pool del campionato

- **Pool di base** (`DeckPrototype.base_cards`): catalogo di tutte le carte
  e delle loro copie. Gestita solo dall'admin.
- **Pool del campionato**: copia indipendente della pool di base, creata alla
  creazione del campionato. Le carte prese dalla pool di un campionato non
  influenzano le pool degli altri campionati.
- Operazioni sulla pool di base (admin):
  - Sincronizzazione con le immagini: aggiunge solo le carte nuove, non tocca
    le esistenti; chiede conferma.
  - Caricamento di una singola carta, con nome e copie modificabili prima
    della conferma.
  - Modifica manuale di nome e copie.
  - Reset: ricostruisce la pool di base da nome e copie indicati nei nomi
    dei file immagine.
- Operazioni sulla pool del campionato (admin):
  - Sincronizzazione con la pool di base: aggiunge solo le carte nuove,
    non tocca le esistenti.
  - Modifica manuale di nome e copie.
  - Nessun reset della pool del campionato.

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

### Eliminazione di team e piloti

- Il player elimina i propri team e piloti in modo logico: la riga resta nel
  database (`deleted_at`) e sparisce dalla sua vista. L'eliminazione di un
  team nasconde anche i suoi piloti.
- Un pilota iscritto a un campionato attivo non può essere eliminato.
- Gli elementi nascosti si conservano fino a un anno.
- Un elemento nascosto continua a occupare il suo nome fino alla pulizia.
- L'admin può cancellare definitivamente: prima i piloti, poi il team.
  Un pilota si cancella solo se non compare in alcun campionato
  (il campionato va cancellato prima).
- La pulizia annuale è un comando manuale: cancella solo gli elementi nascosti
  da oltre 12 mesi che non hanno collegamenti.
- Nomi di team e di piloti: unici su tutto il gioco, senza distinguere le maiuscole.
- Un pilota può esistere senza team; per iscriversi a un campionato serve un team.

## 7. Risorse del pilota

- `gold`: denaro spendibile nel negozio.
- `sponsor`: punti che permettono di riscattare premi nel negozio.
- `point`: punti del pilota nel campionato.

## 8. Iscrizione a un campionato

Ad ogni iscrizione a un campionato, tutto il pilota viene reimpostato:

- Inventario: composizione iniziale (Velocità 1-4, 3 copie ciascuna, 0 calore).
  Il pilota può iscriversi solo se ha un team e non partecipa a un altro campionato attivo.
- Mazzo da gioco: vuoto.
- `gold`, `sponsor`, `point`: 0 (valore predefinito dello schema).

Il pilota può iscriversi solo se non partecipa a un altro campionato attivo.

## 9. Campionati, gare e classifica

- Punti per posizione di arrivo:

| Posizione | Punti |
|---|---|
| 1° | 9 |
| 2° | 6 |
| 3° | 4 |
| 4° | 3 |
| 5° | 2 |
| 6° | 1 |
| 7°–12° | 0 |

- Massimo 12 piloti per gara.
- La classifica di un campionato è la somma dei punti ottenuti nelle gare.
- A pari punti: ordine alfabetico, solo per stabilità di visualizzazione.

## 10. Pagine principali

- Login e registrazione.
- Dashboard con i propri team e piloti.
- Gestione team e piloti.
- Mazzi del pilota: inventario e mazzo da gioco.
- Campionati: un'unica sezione che contiene elenco (attivi e chiusi),
  dettaglio con classifica e gare, e iscrizione di un pilota.
- Negozio: placeholder "Funzionalità in definizione".
- Pannello admin: campionati, gare, risultati.

## 11. Schema attuale verificato e differenze

Schema attuale (HeatDB.sql): 6 tabelle `User`, `Pilot`, `Deck`,
`"Championship "`, `Team`, `Deck_prototype`. Nessun dato, indice o vista.
Tutte le foreign key usano `ON UPDATE/DELETE NO ACTION`.

Da risolvere con migrazioni Alembic:

- La tabella `"Championship "` ha uno spazio finale nel nome.
- `Championship.pilots` è TEXT: sostituire con `ChampionshipPilot`.
- Mancano le tabelle `Race` e `RaceResult`.
- `Deck` non è collegato a `Pilot`: servono inventario e mazzo da gioco.
- `Deck` è oggi collegato solo al campionato (`Championship.deck`).
- `Team` non ha riferimento a `User`: serve per User 1:N Team.
- `User` non ha campo ruolo: serve per admin/player.
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