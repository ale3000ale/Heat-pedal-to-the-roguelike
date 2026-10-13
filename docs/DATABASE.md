# Database — Heat

Ultimo aggiornamento: 2026-10-13

Schema letto dai modelli SQLAlchemy in `backend/app/db/models` (ramo `phase-13a-card-plays`, letti il 2026-10-13). Database: SQLite, `sqlite:///./heat.db` (vedi `backend/app/config.py`). Le migrazioni sono Alembic (`python heat.py migrate`). Le date `DateTime` dei modelli sono senza fuso; dove i modelli usano un'ora propria sono in UTC.

## Utenti e sessioni

### user

- `id` (chiave), `username` (unico), `password`, `role`.
- `role` ammette solo `admin`, `judge`, `player` (vincolo `ck_user_role`), predefinito `player`.

### session

- `id`, `token_hash` (unico), `user_id` (verso `user.id`, cancellazione a cascata, indicizzato), `created_at`, `expires_at`.

## Team e piloti

### team

- `id`, `name` (unico), `name_key` (unico, nome normalizzato per ignorare le maiuscole, impostato dal servizio), `user_id` (verso `user.id`), `deleted_at` (eliminazione logica).

### pilot

- `id`, `name` (unico), `name_key` (unico), `gold`, `sponsor`, `point` (interi, predefinito 0), `team_id` (verso `team.id`, facoltativo), `user_id` (verso `user.id`), `deleted_at` (eliminazione logica).
- Tre mazzi, ciascuno con una chiave verso `deck.id` obbligatoria e unica: `inventory_deck_id` (inventario delle modifiche), `sponsor_inventory_deck_id` (inventario sponsor), `game_deck_id` (mazzo da gioco).

## Mazzi

### deck_prototype

- `id`, `name` (unico), `base_cards` (testo), `kind` (`modifiche` o `sponsor`, predefinito `modifiche`; le pool derivate hanno il tipo della base).

### deck

- `id`, `cards` (testo), `id_prototype` (verso `deck_prototype.id`, facoltativo), `version` (predefinito 1).
- `version` è la colonna del blocco ottimistico: ogni modifica la incrementa e il salvataggio fallisce con `StaleDataError` se il mazzo è cambiato nel frattempo.
- `deck.cards` e `deck_prototype.base_cards` sono testo con un array JSON del tipo `[{"path":"/images/cards/1_nome.webp","value":1}]` (formato indicato nelle istruzioni del progetto; il formato attuale delle carte nei mazzi, con nome, percorso e copie, è gestito da `backend/app/services/cards.py`, non riletto per questo documento).

## Campionati

### championship

- `id`, `name` (unico), `name_key` (unico), `date`, `is_closed` (predefinito falso), `pool_deck_id` (copia della pool delle modifiche, verso `deck.id`), `sponsor_pool_deck_id` (copia della pool sponsor, verso `deck.id`).
- Regole dell'oro per gara: `gold_base` (predefinito 20), `gold_pos_1` ... `gold_pos_6` e `gold_pos_other` (predefinito 0; l'ultima vale dalla 7ª posizione in poi).

### championship_defaults

- Una sola riga (`id` = 1): le stesse 8 colonne dell'oro e `card_poll_seconds` (da 1 a 10, predefinito 5).
- Le regole dell'oro si copiano nel campionato alla creazione; `card_poll_seconds` non si copia e vale per tutti.

### championship_pilot

- `id`, `championship_id` (verso `championship.id`), `pilot_id` (verso `pilot.id`, indicizzato); la coppia è unica.

### championship_standing

- Classifica finale congelata: `id`, `championship_id` (indicizzato), `pilot_name`, `rank`, `points`, `races_played`. Non ha riferimento al pilota, che può essere eliminato dopo.

## Gare

### race

- `id`, `championship_id`, `number` (la coppia è unica), `date` (facoltativa).
- Revisione: `review_started_at`, `review_started_by_user_id` (verso `user.id`, nome vincolo `fk_race_review_started_by_user_id`) e `review_closed_at`. Le prime due sono vuote se la revisione non è aperta; `review_closed_at` è valorizzata quando la revisione è confermata e le carte giocate sono state consumate.

### race_result

- `id`, `race_id`, `pilot_id`, `position`, `points` e `sponsor_points` (predefinito 0).
- Vincoli: coppia `race_id` e `pilot_id` unica; coppia `race_id` e `position` unica; posizione da 1 a 12; punti sponsor non negativi.

## Carte sponsor in gara

### card_play

- Registro delle carte giocate (le righe non si cancellano): `id`, `race_id`, `pilot_id`, `card_name`, `card_path`, `status`, `played_at`.
- `status` ammette `giocata` (predefinito), `annullata`, `consumata` (vincolo `ck_card_play_status`). Indice `ix_card_play_race_pilot` su `race_id` e `pilot_id`.

### card_gift

- Carte regalate con il tasto S, usate per la notifica: `id`, `race_id`, `pilot_id`, `card_name`, `card_path`, `created_at`, `seen_at` (vuota finché la notifica non è stata vista). Indice `ix_card_gift_pilot_seen` su `pilot_id` e `seen_at`.
- Il bonus del giudice a fine gara non crea righe qui.

## Negozio

Campi comuni di `pack_template` e `pack`: `name`, `image_path`, `currency` (`gold` o `sponsor`), `cost`, `modifiche_count` (predefinito 3), `sponsor_count` (predefinito 0), `filter_enabled` (predefinito falso), `filter_text` (nomi separati da virgola, usato solo con il filtro attivo), `created_at`, `updated_at`.

### pack_template

- `id` e i campi comuni.

### shop_template

- `id`, `name`, `name_key` (unico), `created_at`.

### shop_template_pack

- Chiave composta `shop_template_id` e `pack_template_id`, entrambe con cancellazione a cascata.

### pack

- `id`, `championship_id` (indicizzato) e i campi comuni: copia indipendente nel negozio del campionato.

### pack_purchase

- Storico acquisti: `id`, `championship_id` (indicizzato), `pilot_id` e `pack_id` (verso `pilot.id` e `pack.id`, impostati a vuoto se l'elemento viene eliminato), `pilot_name`, `pack_name`, `currency`, `cost` (copiati all'acquisto), `cards_modifiche` e `cards_sponsor` (testo, stesso formato dei mazzi), `purchased_at`.

## Migrazioni

Secondo `PROJECT_STATUS.md`: oro per gara `c9f3a1b6d8e4`, tabelle del Negozio `a1c5e9b3d7f2`, unione delle teste `b2d6f0a4c8e1`, `card_play` `c3e7a1d5b9f2`, stato "in revisione" `d4f8b2e6a0c3`, `card_gift` `e7a3c9d1f5b2`, intervallo di controllo `f8a4d2c6e0b1`, revisore unico `a9c3e7b1d5f0`. Dopo l'unione delle teste `alembic downgrade -1` dà "Ambiguous walk": si usa la revisione precisa. Le migrazioni delle fasi precedenti non sono elencate qui.

## Carte caricate (13e)

Non c'è una colonna per l'origine "caricata": una carta è caricata se il suo percorso inizia con `cards/uploads/<tipo>/` (file in `backend/media/cards/uploads/<tipo>/`). Il commit `e26801e` della 13e non aggiunge migrazioni.

## Non verificato

Non ho letto `backend/app/db/models/__init__.py`, `backend/app/db/base.py`, le migrazioni in sé, la cartella `database/` né il database SQLite originale. Gli indici automatici delle colonne uniche non sono elencati. Il documento storico `DATABASE_ANALYSIS.md` e `SHOP_SCHEMA.md` restano nella cartella `docs/`.
