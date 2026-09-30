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
  - **Inventario**: tutte le carte possedute dal pilota.
  - **Mazzo da gioco**: le carte usate in gara, massimo 15 carte.
- Il pilota costruisce il mazzo da gioco scegliendo carte dal proprio inventario.
- Stato iniziale alla creazione del pilota:
  - Inventario: 3 carte di valore 1, 3 di valore 2, 3 di valore 3,
    3 di valore 4, 0 carte calore.
  - Mazzo da gioco: vuoto.
- Il pilota ottiene nuove carte tramite pacchetti, che consumano la pool
  del campionato selezionato.
- La meccanica dei pacchetti (contenuto, costo, apertura) è rinviata.
- `DeckPrototype` definisce la pool di carte del campionato.
- Ogni campionato ha una pool nuova e indipendente, creata alla sua creazione
  dal prototipo. Le carte prese dalla pool di un campionato non influenzano
  le pool degli altri campionati.
- Non è previsto alcun reset della pool: la funzione è eliminata.
- Formato di `Deck.cards`: array JSON di oggetti
  `{"path": "/images/cards/N_nome.ext", "value": N}`.
- Il backend valida la struttura di `Deck.cards`; il database non ha
  vincoli `CHECK`.

## 7. Risorse del pilota

- `gold`: denaro spendibile nel negozio.
- `sponsor`: punti che permettono di riscattare premi nel negozio.
- `point`: punti del pilota nel campionato.

## 8. Iscrizione a un campionato

Ad ogni iscrizione a un campionato, tutto il pilota viene reimpostato:

- Inventario: composizione di default (3+3+3+3 carte, 0 calore).
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

## 12. Domande aperte (rinviate)

1. Negozio: entità, prodotti, prezzi e regole.
2. Amministrazione carte: funzioni e nuove entità o record.
3. Spareggio sportivo: criterio in caso di pari punti.
4. Pacchetti di carte: contenuto, costo e meccanica di apertura.