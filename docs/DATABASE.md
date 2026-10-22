# Database — Heat

Ultimo aggiornamento: 2026-10-21 (delta fase 15 su registro eventi, ID e conferme notifiche).

Lo schema di base sotto deriva dai modelli SQLAlchemy in `backend/app/db/models` letti il 2026-10-13 sul ramo `phase-13a-card-plays`; non è una nuova analisi completa del file SQLite reale. I delta della fase 15 sono distinti nelle sezioni `card_gift` e Migrazioni e nelle note collegate. Database: SQLite, `sqlite:///./heat.db` (vedi `backend/app/config.py`). Le migrazioni sono Alembic (`python heat.py migrate`). Le date `DateTime` dei modelli sono senza fuso; dove i modelli usano un'ora propria sono in UTC.

Prima di eseguire migrazioni sui dati del gioco: arresto dell'app, backup verificato e prova su copia. Anche `heat.py start` e `setup` applicano migrazioni: non avviarli sui dati da conservare prima di questi passaggi. Nessuna migrazione reale è stata applicata dall'assistente.

## Utenti e sessioni

### user

- `id` (chiave), `username` (unico), `password`, `role`.
- `role` ammette solo `admin`, `judge`, `player` (vincolo `ck_user_role`), predefinito `player`.
- `password` contiene un hash prodotto da `hash_password` in `backend/app/security.py` (libreria `pwdlib`, `PasswordHash.recommended()`).

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

### Formato di `cards` e `base_cards`

- `deck.cards` e `deck_prototype.base_cards` sono colonne di testo che contengono un array JSON. Il formato è definito da `CardEntry` in `backend/app/services/cards.py`: `[{"name":"Velocità 1","path":"cards/starter/velocita-1.webp","copies":3}]`.
- `name`: testo da 1 a 64 caratteri. `path`: testo da 1 a 255 caratteri, relativo a `backend/media`. `copies`: intero da 1 a 999.
- Testo vuoto o assente equivale a nessuna carta. La lettura (`parse_cards`) rifiuta i formati errati e i nomi duplicati nello stesso mazzo (confronto senza spazi ai bordi e senza distinguere le maiuscole). La scrittura passa da `dump_cards`.
- Il mazzo da gioco (`game_deck_id`) può avere al massimo 15 carte in totale (somma delle copie) e, per ogni carta, non più copie di quelle possedute nell'inventario (`validate_game_deck`).
- Questo formato (`name`, `path`, `copies`) è diverso da quello indicato nelle istruzioni del progetto (`path`, `value`, percorsi come `/images/cards/1_nome.webp`). Il codice è la fonte di verità per lo stato attuale; la differenza va chiarita con il proprietario del progetto prima di cambiare uno dei due.
- Il nome file di una carta caricata segue `nome_N`, dove N è il numero di copie (`parse_card_filename`).

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
- Delta fase 15: modello con `sqlite_autoincrement=True`; migrazione `d6f0a4b8c2e7` per `AUTOINCREMENT` esplicito sulla chiave `id`. Gli ID assegnati automaticamente non vengono riutilizzati dopo l'annullo del regalo, anche svuotando la tabella, nel database migrato.
- La migrazione ricrea la sola tabella con copia delle righe; non aggiunge colonne e preserva ID presenti, date, chiavi esterne e indici nei test sintetici. Non modifica il formato delle carte.
- Il downgrade conserva le righe ma perde la garanzia e la storia di allocazione. Non usarlo con client o endpoint che richiedono ID stabili; non trasferire conferme pendenti attraverso ripristini o ricreazioni del DB.
- Dettagli e precauzioni in `PHASE_15_GIFT_ID_MIGRATION.md`. `/seen` storico resta invariato. API selettiva aggiunta in `cda06a9`, verificata in CI `39476606868`; contratto in `PHASE_15_GIFT_SEEN_SELECTED.md`. Ora usata dal flusso campionato `df7edf5`/`dc97fcf`, CI `39502927035` verde; dettagli in `PHASE_15_CHAMPIONSHIP_LIVE.md`.
- `POST /api/championships/{id}/card-gifts/seen-selected` modifica solo `seen_at` delle notifiche richieste, del pilota posseduto dall'utente e nel campionato indicato. Richieste ripetute non riscrivono la data già registrata; ID assenti, annullati o fuori ambito sono ignorati. Massimo 100 ID positivi per richiesta. Nessuna nuova migrazione nel blocco API e nessun trasferimento di carte o evento SSE.
- Il servizio TypeScript conserva il pilota assente dal DTO `CardGift`, valida ID sicuri JavaScript e invia batch per pilota. Non garantisce atomicità tra richieste. Il collegamento frontend non modifica tabelle, colonne, indici o formato delle carte e non certifica il database originale.

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

Secondo `PROJECT_STATUS.md` (letto il 2026-10-13): oro per gara `c9f3a1b6d8e4`, tabelle del Negozio `a1c5e9b3d7f2`, unione delle teste `b2d6f0a4c8e1`, `card_play` `c3e7a1d5b9f2`, stato "in revisione" `d4f8b2e6a0c3`, `card_gift` `e7a3c9d1f5b2`, intervallo di controllo `f8a4d2c6e0b1`, revisore unico `a9c3e7b1d5f0`. Dopo l'unione delle teste `alembic downgrade -1` dà "Ambiguous walk": si usa la revisione precisa. Le migrazioni delle fasi precedenti non sono elencate qui. I commit della 13e e della 13f non aggiungono migrazioni (verificato nell'elenco di `backend/alembic/versions` il 18 ottobre 2026).

Delta letti nella fase 15: `a2e6c0d4f8b3` (bozza revisione), poi `d5e9a3b7c1f6` (registro `event_log` con ID non riutilizzabili), poi `d6f0a4b8c2e7` (ID `card_gift` non riutilizzabili). Schema del registro e indici documentati in `PHASE_15_DATABASE.md`; avanzamento in `PHASE_15.md`.

Commit `aa1a4c7aa6d1a2e56ef38ff3f95fc4ed93b33204`: CI `39467182291` verde il 2026-10-20, inclusi backend pytest e ciclo delle migrazioni su database di test. Verificati gli esiti dei job, non il database originale. Nessuna certificazione di upgrade sui dati reali.

API selettiva `cda06a91799049022358df5cbb4129c91b83b7b2`: nessuna migrazione aggiuntiva, CI `39476606868` interamente verde. La testa Alembic resta `d6f0a4b8c2e7`. I test includono conferme selettive, idempotenza e conferma tardiva dopo annullamento; sono verifiche sintetiche, non prove sul database del gioco.

Collegamento campionato `df7edf5` e formattazione `dc97fcf`: CI `39502927035` tutta verde il 2026-10-20, nessuna migrazione aggiuntiva. La testa Alembic resta invariata. Questo riallineamento è solo documentale: nessuna nuova ispezione SQLite, comando locale, backup o applicazione di migrazioni ai dati reali.

## Non verificato

L'analisi iniziale non comprendeva `backend/app/db/models/__init__.py`, `backend/app/db/base.py`, le migrazioni in sé, la cartella `database/` o il database SQLite originale. Nel blocco fase 15 sono stati riletti specificamente modello CardGift, migrazione storica CardGift, migrazione event_log e nuova migrazione degli ID, configurazione Alembic, test e verificatore CI; non equivale a una nuova ispezione dell'intero DB originale. Gli indici automatici delle colonne uniche non sono elencati. Lo schema storico è in `DATABASE_ANALYSIS.md` e quello del Negozio in `SHOP_SCHEMA.md`.

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

Test mirati superati dal workflow prima di questo riallineamento; CI completa separata.
<!-- phase16-admin-save:end -->
