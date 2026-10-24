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

Aggiornamento: 2026-10-23. Ramo phase-16-admin-pilot-inventory, PR 15 in bozza.
Stato sintetico fase 16: Perimetro funzionale implementato, incluso live e riepilogo effettivo; CI 40026443509 riuscita su 2366d1d; riscontro manuale complessivamente positivo dell'autore, senza protocollo caso per caso; riallineamento finale documentale; nessun merge autorizzato.

L'intestazione H1 e la riga Stato sintetico fase 16 sono contratti del workflow.
Il titolo deve restare esattamente quello corrente; la riga di stato e' unica e
senza pipe. Questo documento consolida lo stato corrente; le note incrementali
precedenti restano nello storico Git. Non costituisce merge o rilascio in main.

### Contratto backend e conservazione delle copie

GET /api/admin/championships/{championship_id}/pilots restituisce iscritti visibili
con nome e username. GET e PUT sul percorso
/api/admin/championships/{championship_id}/pilots/{pilot_id}/cards leggono o
salvano il contesto del pilota. Accesso solo admin; nessun diritto ampliato al
giudice e nessuna modifica a utenti, team, ruoli, saldi o punteggi.

Il PUT riceve versions di tutti i cinque contenitori e transfers con soli
source/path. ID/version interi positivi; solo le due pool possono essere null.
Campi extra, destinazioni client e sostituzioni arbitrarie sono rifiutati.
Pool assente distinta da pool vuota, mai creata automaticamente. Riferimenti
Deck incoerenti o JSON corrotto non diventano contenitori validi o vuoti.

Ogni clic sposta una copia nelle sole direzioni approvate:
- game_deck verso modification_pool;
- modification_inventory verso modification_pool;
- sponsor_inventory verso sponsor_pool;
- modification_pool verso modification_inventory;
- sponsor_pool verso sponsor_inventory.

Nessun movimento diretto pool/mazzo, sponsor/mazzo o inventario/mazzo nella
schermata admin. Una rimozione dal mazzo non sottrae anche dall'inventario.
Il pianificatore clona gli input e rifiuta copie non valide, percorsi ambigui
e nomi associati a immagini discordanti, senza mutazioni parziali su errore.

Il backend ricontrolla ruolo, pilota visibile/iscritto, campionato chiuso, gara
aperta, revisione non confermata e tutte le versioni nella transazione. 409 per
conflitto, 422 per movimento non applicabile, senza retry automatici. Commit
unico di Deck/eventi e rollback anche su errore eventi. Differenze effettive
soltanto: versioni ed eventi non cambiano per un salvataggio senza differenze.
Dopo commit: cards.changed pubblico vuoto e privato al proprietario con solo
pilot_id, senza carte o notifiche regalo/tasto S.

### Lock condiviso e avvio con mazzi da 15

services/sqlite_write_lock.py e' condiviso da salvataggio admin, move_card e
create_race prima delle letture autorevoli. Invalida identita' ORM precedenti e
rifiuta modifiche pendenti; promuove una transazione nativa gia' aperta tramite
UPDATE senza righe, senza cambiare carte/versioni. Il retry preesistente di
move_card resta limitato a StaleDataError; admin e avvio non ritentano i lock.

create_race richiede esattamente 15 copie nel mazzo da gioco di tutti gli
iscritti, inclusi i nascosti, sotto lo stesso lock. Non 15 nomi o il totale degli
inventari; nessun nuovo minimo di iscritti. race_deck_snapshot.py riusa il
dominio race_deck_readiness.py. Mancanza mazzo o JSON corrotto non sono sanati.
Tra le gare un mazzo puo' restare incompleto, anche dopo un salvataggio admin.

Rifiuto di avvio: nessuna nuova gara o race.started, rollback e 409 con nomi e
conteggi dei non pronti, senza carte. BUSY/LOCKED diventano RaceStartConflictError
e 409; altri errori SQL non sono mascherati. Restano blocchi di chiusura e
gara/revisione non confermata; gestione precedente delle revisioni scadute invariata.

### UI, richiesta e riepilogo effettivo

Nelle impostazioni campionato l'admin apre Piloti, vede nome/username e un
pulsante Carte accessibile. Cinque sezioni apribili con immagini e quantita':
mazzo N/15 per copie, due inventari distinti e due pool. Su mobile le aree
restano in sequenza. Modal e CardTile riusati, senza nuovo scaffold o risorse.

Il piano costruisce versions dalla baseline, anche per contenitori non toccati,
e ricalcola la sequenza senza fidarsi di un'anteprima alterata. Percorsi entro
255 code point, identita' nomi coerente con strip().casefold() del backend.
Nessun arrotondamento di ID/version e nessuna destinazione/copertura di copie
arbitraria nella richiesta. Tutti gli output sono indipendenti dalla sessione.

Salva in fondo a destra apre un modal solo testuale con pilota, username, nome
carta, quantita', sorgente/destinazione e nuovo conteggio del mazzo. Il riepilogo
accorpa copie e compensa i versi opposti inventario/pool della stessa carta,
senza inventare un verso inverso verso il mazzo. Non cambia il registro PUT:
il server riceve i clic originali validati in ordine. Nessuna proposta di PUT
quando non restano variazioni effettive. Annulla, X, Escape e sfondo non inviano
e conservano la bozza. Solo Conferma e salva consuma una proposta una volta.

Durante conferme e operazioni sono protetti clic, ripristino, ritorno, chiusura
ordinaria e navigazione. Successo: nuova sessione da snapshot PUT e versioni
server. Errori conservano la bozza; 422 consente azioni manuali, altri errori
bloccano nuovi invii fino a rilettura. Esito di rete o risposta inutilizzabile
non provano un rollback. Rileggi dal server e' esplicito: con bozza pendente
richiede conferma e la sostituisce soltanto dopo risposta utilizzabile.
Ripristina bozza e' locale e conserva i blocchi, non equivale a una rilettura.
Il client controlla contesto e la creazione della sessione controlla carte:
non e' una validazione runtime completa di ogni campo del DTO.

### Live e lifecycle

Il pannello usa eventClient condiviso e riletture REST autorizzate tramite il
coordinatore createRefreshCoalescer. Nessun secondo EventSource, polling o
autosalvataggio. I segnali non trasferiscono carte e non autorizzano scritture.
Eventi pertinenti di carte, iscrizioni, gara/revisione, resync e riapertura del
trasporto invalidano il contesto; gli altri campionati sono filtrati. Lo stato
della connessione non viene presentato come prova della freschezza dei dati.

Riletture accorpate e risultati obsoleti scartati. Una bozza non viene
sovrascritta: aggiornamenti incompatibili la bloccano conservando i dati.
Le conferme aperte sono distinte dalle richieste HTTP effettivamente in corso:
un evento puo' invalidare la proposta prima dell'invio; durante PUT/GET viene
rinviato, evitando di scartare il successo del proprio salvataggio. Una GET
live puo' seguire un evento pendente dopo il PUT: non e' un retry della scrittura.
Solo l'accettazione di uno snapshot server utilizzabile libera il blocco delle
riletture, non un reset locale o un cambio di stato del trasporto.

Cambio utente/ruolo, campionato, pilota o smontaggio invalidano il contesto;
risposte e callback tardive non ripopolano un contesto successivo. I cleanup
rimuovono i soli listener propri, senza chiudere lo stream condiviso. Una
chiusura forzata del browser non annulla una scrittura gia' inviata.

### Esiti finali verificati e collaudo dell'autore

Codice candidato: 2366d1de37cf1cf638b45c55313a3e31601eebff. CI 40026443509
riuscita per Frontend (check, lint, test, build), job 120664599995, Backend
(pytest), job 120664600371, Migrazioni (database di test), job 120664600375,
e Documenti fase 16 dopo backend, job 120665715224. Non sono nuove esecuzioni
locali. I conteggi complessivi di test e warning non sono stati letti dai log.

Dopo il via libera e la checklist in conversazione sul candidato 2366d1d,
il 2026-10-23 alle 23:59 CEST l'autore riferisce: «sembra funzionare tutto».
E' un riscontro manuale complessivamente positivo, non un verbale con esito
per ogni caso. Non sono stati forniti browser/dispositivo, log o risultati
individuali; non si marca automaticamente ogni voce OK. Non e' un collaudo
browser eseguito dall'assistente ne' prova di tutte le condizioni concorrenti.

Restano non attestati singolarmente i casi avanzati della checklist: doppio
invio, rete interrotta/esito incerto, conflitti tra sessioni, risposte tardive,
permessi e scadenza durante rete, rollback/concorrenza reale e privacy dei
payload. Le coperture automatiche e il riscontro qualitativo non vanno confusi.

### Tracciabilita' delle verifiche precedenti

Storico: dominio 934333c; sessione eedd729; chiusura modal d9ee662; UI c950510;
trasporto PUT 549e83e/f95c915; piano 024d47a/ad377d4; salvataggio 9769dd5/7d449cb;
adattatore eventi ecbf684/e725ba4; riletture 914ee47; collegamento live
fbcbd89/dc06e29; rimozione import 78661d8; prefer-const nei test 283c0ac;
riepilogo effettivo e posizione Salva 6d1b7cd/2366d1d. I controlli finali
sopra sostituiscono come stato corrente le letture incrementali in coda.

Il precedente riepilogo dell'autore era 748 passed, 14 warnings e 14 subtests
passed prima della pulizia 4514348; 27 asserzioni snapshot conservate tramite
AST. La regressione 72 failed/676 passed, poi un fallimento, era stata corretta
senza saltare test o allentare il dominio. Non sono i conteggi della CI finale.
Dieci casi di readiness includevano lock simulato, non tutta la concorrenza reale.

Identita' Unicode 15.0 verificata con confronto Node/Python su 1.112.064 scalari
e nove casi composti, senza NFC/rimozione accenti; non era type-check. Controlli
Node senza tipi: dodici scenari politica modal, venticinque adattatore eventi
e nove coordinatore riletture; non equivalgono a Vitest o browser. Sette test
Python della trasformazione documentale su fixture temporanee erano riusciti,
non il workflow GitHub completo. Le esecuzioni npm locali non sono inventate.

### Riallineamento documentale e consegna

Il titolo stabile e' stato ripristinato in f8a94e4; la tabella PROJECT_STATUS
deriva dalla riga Stato sintetico fase 16, senza stato hardcoded su vecchi commit.
Il pin CI aggiornato usa il blob 6858f05d89072cca488efeeb46166a2770383545 del
workflow approvato. Restano controlli su titolo, stato unico e marcatori anche
invertiti/adiacenti, protezioni di ramo e percorsi e nessun force-push.

Questo commit aggiorna soltanto i documenti sorgente e dedicati, dopo codice e
verifiche come richiesto dall'autore. La propagazione ai dieci documenti generali
va verificata dopo la pubblicazione, senza attendere nuovi test applicativi
per i soli docs. Il successo del job documentale sul codice precedente non
dimostra gia' propagato questo nuovo testo. Nessun merge, rilascio o ZIP finale
creato implicitamente; la PR resta in bozza.

Deck.cards resta TEXT con JSON name/path/copies e percorsi relativi ai media,
come confermato il 2026-10-22. Nessuna conversione a path/value o /images/cards,
migrazione, dipendenza, modifica di setup/avvio o accesso al database reale
da parte dell'assistente. Perimetro funzionale fase 16 distinto dal resto
delle istruzioni generali del progetto e da una consegna ZIP complessiva.

Test mirati superati dal workflow prima di questo riallineamento; CI completa separata.
<!-- phase16-admin-save:end -->

<!-- production-lan-current:start -->
## Produzione Wi-Fi/LAN - aggiornamento corrente del 24 ottobre 2026

Per la produzione prevale questa sezione sulle indicazioni storiche relative al solo loopback o al tunnel. Funzionalita sul ramo production-lan, PR #16 in bozza, senza merge in main.

Dalla radice: python heat.py production, oppure voce 7 del menu. Senza URL esplicito seleziona l IPv4 privato del PC e mostra l indirizzo da usare anche sugli altri dispositivi della LAN. Nessun tunnel o client aggiuntivo richiesto. --public-url resta facoltativo per un origine esplicita, incluso il solo loopback.

Gateway sul solo IPv4 scelto:5173, backend su 127.0.0.1:8000 con un worker. API, immagini e SSE passano dal gateway; controlli Host/Origin mantenuti. HTTP solo su rete fidata: traffico non cifrato. Nessuna modifica automatica a firewall o router. PC acceso e dispositivi reciprocamente raggiungibili necessari.

Production non installa dipendenze, non crea DB e non applica migrazioni: verifica soltanto le revisioni in lettura. Il comportamento storico di setup/start/migrate resta invariato. Nessuna modifica a schema, dati reali, formato carte, risorse, dipendenze o lockfile.

Verifica osservata: Production runtime checks 40047553032, job runtime 120733397223, success sul codice formattato 09a9aa594bd75650fe0af0556b67b64f2c0dcc15. Include test launcher/LAN/gateway, tipi, frontend, build, smoke test e lint. Non e una nuova attestazione di tutti i job della CI generale, ne un collaudo Wi-Fi/browser. Conteggi e warning non letti dai log. Nessun nuovo test locale per questo riallineamento; nessun merge o ZIP finale implicito.

Guida operativa e limiti: [Produzione Wi-Fi/LAN](PRODUCTION_LAN.md).
<!-- production-lan-current:end -->

<!-- account-password-current:start -->
## Impostazioni account e cambio password - 24 ottobre 2026

Su main: clic sul proprio nome apre Impostazioni account. Password attuale e doppio inserimento della nuova; nuova password di 8-128 caratteri, validata anche sul server. La sessione corrente resta attiva con token e scadenza invariati; le altre sessioni dello stesso account vengono revocate. Hash e revoche sono nella stessa transazione con rollback su errore. Gli altri account non cambiano.

Endpoint POST /api/auth/change-password, autenticato, successo 204. Nessuna migrazione o dipendenza nuova. Nessuna modifica al DB reale eseguita dall assistente. Durante l invio niente doppio invio o chiusura ordinaria; campi svuotati dopo la richiesta e alla chiusura. Errori di rete: esito incerto e nessun retry automatico. SSE riusa il controllo periodico delle sessioni.

Riallineamento dopo pytest backend, tipi, lint, test frontend e build riusciti nel runner: run 40114589745, checkout 97653418434af55ff904d36ab75d80fb0e8fe365, formattazione circoscritta applicata prima delle verifiche. Nessun conteggio inventato, test locale o collaudo browser attestato.

Dettagli, limiti e prove: [Impostazioni account](ACCOUNT_SETTINGS.md).
<!-- account-password-current:end -->

<!-- account-password-ui-current:start -->
## Aggiornamento grafico impostazioni e login - 24 ottobre 2026

Nel modal Impostazioni account la sezione Cambio password e a scomparsa e inizialmente chiusa a ogni nuova apertura. La chiusura della sezione svuota i campi. In login e nei tre campi del cambio password e disponibile Mostra/Nascondi, indipendente per ogni campo e nascosto inizialmente. La visibilita non viene salvata; il componente dedicato password-input.svelte e riusato nei due contesti. Durante le richieste i controlli relativi sono disabilitati. Backend, API, database e comportamento di revoca delle altre sessioni restano invariati.

Il fallimento Prettier su account-settings.svelte e stato affrontato applicando il formatter del lockfile solo a quel componente. Prima di questo riallineamento sono riusciti sul runner: npm run check, npm run lint, npm test e npm run build. Run 40124870171, checkout fc8d1f301a9350c555e4c4f2ab0d8ff6a7bb89ae, con componente formattato prima delle verifiche. Il successivo commit pubblica quello stile e questi documenti; non e una nuova esecuzione della CI sul commit risultante. Nessun test locale o conteggio inventato.

I test password-ui.spec.ts presenti nel candidato sono controlli di rendering server, non prove interattive di clic, tastiera o browser. Restano da verificare manualmente espansione/richiusura, reset alla riapertura e Mostra/Nascondi nei quattro campi. Nessuna migrazione, nuova dipendenza, modifica al lockfile o operazione sul DB reale.
<!-- account-password-ui-current:end -->
