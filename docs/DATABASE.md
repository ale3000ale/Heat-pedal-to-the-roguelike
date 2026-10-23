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
Stato sintetico fase 16: Backend, client PUT, piano e salvataggio UI implementati; controlli applicativi riusciti su 7d449cb; live e collaudo browser da completare; fase non conclusa.

L'intestazione H1 e la riga Stato sintetico fase 16 sono contratti del processo
di riallineamento. Non rinominare il titolo senza aggiornare e verificare i suoi
consumatori. Questo documento consolida le note precedenti, conservate in Git.
Nessun merge, migrazione o prova sul database reale impliciti.

### Contratto backend

PUT /api/admin/championships/{championship_id}/pilots/{pilot_id}/cards riceve
versions e transfers. versions include tutti i cinque contenitori, con id/version
interi positivi; solo le due pool possono essere null. Ogni trasferimento contiene
solo source/path e sposta una copia, con destinazione imposta dal dominio. Campi
extra, destinazioni client e sostituzioni arbitrarie delle carte sono rifiutati.

Il backend ricontrolla admin, pilota visibile/iscritto, chiusura campionato, gara
aperta e revisione non confermata nella transazione. Confronta id e versione
anche dei contenitori non toccati. Pool assenti non create e non utilizzabili
come sorgente o destinazione. Conflitto 409 senza retry automatico; movimento
non applicabile 422. Commit unico Deck/eventi, rollback anche su errore eventi.

Il mazzo puo' restare incompleto tra le gare. Nessuna aggiunta pool/mazzo o
sponsor/mazzo e nessuna doppia sottrazione. Solo differenze effettive cambiano
versioni ed eventi. La risposta contiene snapshot e versioni server. Dopo
variazioni: cards.changed pubblico vuoto e privato al proprietario con solo
pilot_id, senza carte o notifiche regalo/tasto S.

### Lock e avvio gara

services/sqlite_write_lock.py e' condiviso da salvataggio admin, move_card e
create_race prima delle letture autorevoli; invalida identita' ORM precedenti e
rifiuta modifiche pendenti. La transazione nativa gia' aperta viene promossa con
UPDATE senza righe, senza modificare carte/versioni. Il retry preesistente di
move_card resta limitato a StaleDataError; admin e avvio non ritentano i lock.

create_race richiede esattamente 15 copie nel mazzo da gioco di ogni iscritto
sotto lo stesso lock, non 15 nomi o il totale degli inventari. Include iscritti
nascosti, senza nuovo minimo di iscritti. race_deck_snapshot.py riusa il dominio
race_deck_readiness.py. Mazzo mancante o JSON corrotto non diventano validi.

Iscritto non pronto: niente nuova gara o race.started, rollback e 409 con nomi e
conteggi, senza carte. BUSY/LOCKED diventano RaceStartConflictError e 409; altri
errori SQL non mascherati. Restano chiusura e gara/revisione non confermata; la
gestione preesistente delle revisioni scadute prima dell'avvio non cambia.

### Verifiche e incrementi precedenti

La CI 39917281059 su 4514348 e align-docs-pr 39917281153 risultavano riusciti.
L'autore aveva fornito prima della pulizia 748 passed, 14 warnings e 14 subtests
passed. 4514348 rimuove Result.tuples() da due snapshot eventi mantenendo 27
asserzioni verificate tramite AST. I warning successivi non sono stati contati
dai log. La regressione iniziale di 72 failed/676 passed, poi un fallimento, e'
stata corretta in fixture e aspettative senza saltare test o allentare il dominio.
Dieci casi in test_race_start_readiness.py includono conteggi, JSON corrotto,
admin/giudice, non iscritti, rollback eventi e lock simulato: non provano tutte
le interazioni concorrenti reali o il browser.

Client GET e tipi c01b486, correzione Prettier 822a85a e consultazione bb7f0f7,
corretta in 89cab3d/72e4274, hanno riscontri frontend nelle CI 39976945581 e
39986696961. Quattro test di conteggio coprono copie, vuoto e 14/16 senza
correzioni artificiali, non interazioni Svelte.

934333c aggiunge il pianificatore: game_deck e modification_inventory verso
modification_pool; sponsor_inventory verso sponsor_pool; modification_pool verso
modification_inventory; sponsor_pool verso sponsor_inventory. Una copia per
clic, input immutati anche su errore tardivo, ID/versioni invariati; percorsi
ambigui e immagini discordanti rifiutati. admin-card-identity.ts conserva
strip().casefold() con Unicode 15.0, senza NFC o rimozione accenti: confronto
Node/Python su 1.112.064 scalari e nove casi composti, non un type-check.
Prettier locale era indisponibile, con ENOTCACHED e comando globale assente.
b54cc84 mantiene le aspettative e aggiunge commenti dei code point; f2dc492
formatta il test. La lettura delle 19:21 della CI 39994183218 in coda e' storica,
non un successo; successivamente la CI 39995224182 e' risultata riuscita.

eedd729 aggiunge sessione e otto test: baseline, anteprima e registro separati,
blocco senza perdita, ripristino locale che conserva il blocco. Nessun retry,
rebase o scrittura automatici. d9ee662 aggiunge onrequestclose e politica modal
con dodici casi parametrizzati; dodici scenari Node senza tipi erano riusciti
prima della CI 39997899845. Senza callback resta la chiusura precedente; con
callback nessun open=false automatico, X disponibile ed Escape/sfondo rispettano
closeOnOutside. Non sono prove browser.

### Bozza, client PUT e piano

c950510 collega le carte alla sessione: cinque sezioni con immagini, tre
contenitori del pilota separati dalle due pool, mazzo N/15 per copie e pool
assente distinta da vuota. Modal/CardTile riusati, nessuno scaffold, dipendenza
o risorsa nuova. Le risposte tardive vengono ignorate, non annullate in rete.
Ripristino, ritorno, chiusura e navigazione sono protetti prima dello scarto.
Il ripristino usa la baseline e conserva il blocco, senza rileggere il server.

2cf25fd separa pubblicazione dello stile e controlli successivi; ceb12b1 formatta
i quattro componenti. 788e6f5 aggiunge una sola eccezione ESLint alla chiamata
goto che riusa navigation.to.url.href, senza modifica della logica o esclusione
globale. La CI 40003767478 e align-docs-pr 40003767471 erano riusciti.

549e83e aggiunge tipi e trasporto PUT, f95c915 ne formatta il test. Il client
verifica ID e contesto della risposta, non l'intero DTO runtime; propaga ApiError
e segnala risposte inutilizzabili con AdminCardSaveResponseError. Nessun retry
o GET automatica e nessuna interpretazione di errore rete come rollback certo.
024d47a aggiunge il piano, formattato in ad377d4: tutte le versioni della baseline,
trasferimenti source/path, anteprima ricalcolata e riepilogo ordinato per clic,
non differenze nette. Pool assenti null, metadati incoerenti rifiutati e percorsi
entro 255 code point. La CI frontend 40009944027 era riuscita su ad377d4.

### Salvataggio UI implementato

9769dd5 collega riepilogo e conferma unica al PUT; 7d449cb formatta i quattro
componenti. admin-pilot-cards-save-controls.svelte prepara la proposta senza
rete; Annulla, X, Escape e sfondo non inviano. Conferma e salva consuma la
proposta e blocca prima del primo await: nessun secondo invio dalla stessa
proposta. Sessione cambiata: nuovo riepilogo richiesto.

Durante conferme, PUT e rilettura, lo stato occupato raggiunge elenco piloti e
impostazioni e blocca clic, ripristino, ritorno e chiusura ordinaria. La navigazione
normale e' annullata; una chiusura forzata del browser non annulla una scrittura
gia' inviata. Risposte di componenti dismessi/sessioni sostituite ignorate.

Successo: nuova sessione dallo snapshot PUT e versioni server, senza GET.
Errori: bozza conservata; 422 consente una nuova azione manuale. Altri errori
bloccano nuovi invii: 401/403/404/409 come rifiuti/conflitti, gli altri come esiti
incerti che potrebbero essere gia' applicati. Rileggi dal server e' esplicito e
conferma lo scarto se ci sono operazioni; la bozza viene sostituita soltanto dopo
una lettura utilizzabile. Lettura fallita: baseline, anteprima e registro conservati.
Ripristinare localmente non sblocca un conflitto e non sostituisce tale rilettura.

### Ultima verifica e guasto documentale

CI 40012639610 sul codice formattato 7d449cb: Frontend (check, lint, test, build),
job 120622516434, Backend (pytest) e Migrazioni (database di test) riusciti.
Il job Documenti fase 16 dopo backend, 120623536970, e' invece fallito: il titolo
era stato rinominato aggiungendo e bozza UI e non rispettava il startswith esatto.
Non dichiarare questa CI interamente verde o il browser collaudato. Nessuna nuova
esecuzione npm locale o conteggio complessivo di test/warning dai singoli log.

Questa correzione ripristina il titolo stabile e fa derivare la riga della tabella
di PROJECT_STATUS dalla riga Stato sintetico fase 16 del sorgente. Mantiene
validazione esatta del titolo, unicita' dello stato e marcatori; corregge anche
il riconoscimento di marcatori invertiti adiacenti. Sette test Python eseguiti
su fixture temporanee della trasformazione sono riusciti: aggiornamento dei
dieci file, idempotenza, preservazione del testo esterno, rifiuto degli input
invalidi e nessuna scrittura parziale. Non sono esecuzioni del workflow GitHub,
dell'installazione dipendenze, di pytest o del push. Propagazione ancora da verificare.

### Limiti e seguito

Restano integrazione live tramite client SSE condiviso e collaudo browser di
annullamento, doppi clic, successo, 409, rete incerta, 422, rilettura fallita,
Escape, chiusura/ritorno durante rete e risposte tardive. I test di client, piano
e sessione non sono test DOM del nuovo flusso. Nessun polling, autosalvataggio
o stream SSE aggiuntivo. Fase non completa e nessun merge.

Dopo controlli applicativi riusciti, riallineare i documenti e verificare la
propagazione nei dieci file generali, senza attendere altri test applicativi per
i soli docs. format-review-ui.yml resta circoscritto ai quattro componenti di
salvataggio, con npm ci, Prettier dal lockfile, SHA controllata, protezioni del
ramo e dei percorsi estranei; un commit del bot non prova il verde globale.

Deck.cards resta TEXT con JSON name/path/copies e percorsi relativi ai media,
come confermato dall'autore il 2026-10-22. Nessuna conversione a path/value,
migrazione, modifica di setup/avvio o accesso al database reale.

Test mirati superati dal workflow prima di questo riallineamento; CI completa separata.
<!-- phase16-admin-save:end -->
