# Specifiche del Progetto — Heat

> STATO: BOZZA IN ATTESA DI APPROVAZIONE.

## 1. Stack noto
- Frontend: SvelteKit (minimal, TypeScript, npm, ESLint, Prettier, Vitest) in `frontend/`.
- Migrazioni database: Alembic.
- Sorgente schema attuale: `HeatDB.sql` (solo DDL, nessun dato).

## 2. Decisioni definitive
- Possono esistere più campionati attivi contemporaneamente.
- La cronologia dei campionati chiusi deve essere mantenuta.
- Negozio, amministrazione carte e spareggio sportivo sono rinviati
  e non bloccano la prima versione.
- Prima versione del Negozio: solo placeholder "Funzionalità in definizione".
- In caso di pari punti, l'ordine alfabetico serve solo come stabilizzatore
  di visualizzazione, non come spareggio.

## 3. Entità e relazioni
- User 1:N Team
- User 1:N Pilot
- Team 1:N Pilot
- Pilot 1:1 Deck
- Championship 1:N ChampionshipPilot
- ChampionshipPilot N:1 Pilot
- Championship 1:N Race
- Race 1:N RaceResult
- Pilot 1:N RaceResult
- DeckPrototype: indipendente, usato solo come sorgente per reset/creazione mazzi.

## 4. Formato carte (Deck.cards)
Array JSON di oggetti:
{"path": "/images/cards/N_nome.ext", "value": N}

## 5. Differenze tra schema attuale e modello target
Da risolvere con migrazioni Alembic:
- Tabella `"Championship "` con spazio finale nel nome.
- `Championship.pilots` è TEXT: sostituire con tabella `ChampionshipPilot`.
- Mancano le tabelle `Race` e `RaceResult`.
- `Deck` non ha FK verso `Pilot`; serve il collegamento 1:1.
- `Pilot.user_id` non ha vincolo UNIQUE (la relazione User-Pilot è 1:N, quindi corretto).
- `Team` non ha riferimento a `User`; serve per User 1:N Team.
- Nessun campo ruolo in `User`; formato `password` non definito.

## 6. DA COMPLETARE (decisioni non presenti nei documenti)
- Autenticazione e gestione password (hash).
- Ruoli e creazione del primo admin.
- Pagine principali e loro comportamento.
- Iscrizioni ai campionati e regole di classifica.
- Validazione delle carte.
- Strategia di migrazione (dettagli Alembic).

## 7. Domande aperte (rinviate)
1. Negozio: entità, prodotti, prezzi.
2. Amministrazione carte: funzioni e nuove entità.
3. Spareggio sportivo: criterio in caso di pari punti.
